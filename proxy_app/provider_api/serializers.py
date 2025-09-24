from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse
from rest_framework import serializers
from django.conf import settings
from .enums import DeniedHosts, DeniedParameters


class ProviderResponseSerializer(serializers.BaseSerializer):
    """
    Optimized serializer for processing data received from providers.
    Handles URL filtering and provider-specific transformations in a single pass.
    """
    
    def __init__(self, provider_base_url: str, provider_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider_name = provider_name.lower()
        self.financialdata_base_url = getattr(settings, 'FINANCIALDATA_BASE_URL', 'https://financialdata.online')
        
        # Cache denied hosts and parsed URLs for performance
        self._denied_hosts = [host.value for host in DeniedHosts]
        self._denied_netlocs = set()
        for host in self._denied_hosts:
            parsed = urlparse(host)
            if parsed.netloc:  # Only add if netloc exists
                self._denied_netlocs.add(parsed.netloc)
            else:
                # For hosts without protocol, add them directly
                self._denied_netlocs.add(host)
        self._financialdata_netloc = urlparse(self.financialdata_base_url).netloc
        
        # Cache denied parameters for performance
        self._denied_parameters = [param.value for param in DeniedParameters]
        
        # Compile regex patterns for provider URL detection
        self._provider_url_patterns = self._compile_provider_patterns()
    
    def to_representation(self, data):
        """
        Processes data received from providers in a single pass.
        """
        if isinstance(data, dict):
            return self._process_data(data)
        elif isinstance(data, list):
            # FMP often returns arrays directly - standardize them
            processed_list = [self._process_data(item) if isinstance(item, dict) else item for item in data]
            return self._standardize_array_response(processed_list)
        return data
    
    def _process_data(self, data: dict) -> dict:
        """
        Single-pass processing: URL filtering + parameter filtering + provider transformations.
        """
        if not isinstance(data, dict):
            return data
            
        result = {}
        for key, value in data.items():
            # Filter out denied parameters
            if key in self._denied_parameters:
                continue  # Skip this parameter entirely
            
            if isinstance(value, str):
                result[key] = self._process_string(value)
            elif isinstance(value, dict):
                result[key] = self._process_data(value)
            elif isinstance(value, list):
                result[key] = [
                    self._process_data(item) if isinstance(item, dict)
                    else (self._process_string(item) if isinstance(item, str) else item)
                    for item in value
                ]
            else:
                result[key] = value
        
        # Standardize response format based on provider
        result = self._standardize_response_format(result)
        
        # Add provider metadata to results if present
        if 'results' in result and isinstance(result['results'], list):
            self._add_provider_metadata(result['results'])
        
        return result
    
    def _process_string(self, text: str) -> str:
        """
        Process a string value: filter URLs and return processed result.
        """
        if not isinstance(text, str) or not self._contains_provider_url(text):
            return text
        
        return self._replace_provider_url(text)
    
    def _compile_provider_patterns(self) -> list[re.Pattern]:
        """
        Compile regex patterns for detecting provider URLs.
        """
        patterns = []
        
        # Create patterns for each denied host
        for denied_host in self._denied_hosts:
            # Escape special regex characters and create pattern
            escaped_host = re.escape(denied_host)
            # Pattern to match URLs containing the provider host
            # More flexible pattern to catch subdomains and paths
            pattern = re.compile(
                rf'https?://[^/\s\'"<>]*{escaped_host}[^\s\'"<>]*',
                re.IGNORECASE
            )
            patterns.append(pattern)
        
        return patterns
    
    def _contains_provider_url(self, text: str) -> bool:
        """
        Fast check if text contains any provider URL using regex.
        """
        if not isinstance(text, str):
            return False
        
        # Check with compiled regex patterns
        for pattern in self._provider_url_patterns:
            if pattern.search(text):
                return True
        
        # Fallback to simple string check for performance
        return any(denied_host in text for denied_host in self._denied_hosts)
    
    def _replace_provider_url(self, url: str) -> str:
        """
        Replace provider URLs with our service URL using regex.
        """
        if not isinstance(url, str):
            return url
        
        try:
            # First try regex replacement for more comprehensive matching
            for pattern in self._provider_url_patterns:
                if pattern.search(url):
                    # Extract the matched URL
                    match = pattern.search(url)
                    if match:
                        matched_url = match.group(0)
                        parsed = urlparse(matched_url)
                        
                        # Skip if already our URL
                        if parsed.netloc == self._financialdata_netloc:
                            continue
                        
                        # Check if it's a provider URL
                        if parsed.netloc in self._denied_netlocs:
                            # Build new URL with our base
                            path = parsed.path
                            query = f"?{parsed.query}" if parsed.query else ""
                            fragment = f"#{parsed.fragment}" if parsed.fragment else ""
                            new_url = f"{self.financialdata_base_url}{path}{query}{fragment}"
                            
                            # Replace the matched URL in the original string
                            return url.replace(matched_url, new_url)
            
            # Fallback to original logic for exact matches
            parsed = urlparse(url)
            
            # Skip if already our URL
            if parsed.netloc == self._financialdata_netloc:
                return url
            
            # Check if it's a provider URL
            if parsed.netloc in self._denied_netlocs:
                # Build new URL with our base
                path = parsed.path
                query = f"?{parsed.query}" if parsed.query else ""
                fragment = f"#{parsed.fragment}" if parsed.fragment else ""
                return f"{self.financialdata_base_url}{path}{query}{fragment}"
            
            return url
        except Exception:
            return "[URL_FILTERED]"
    
    def _add_provider_metadata(self, results: list) -> None:
        """
        Add provider metadata to result items.
        """
        timestamp = self._get_current_timestamp()
        for item in results:
            if isinstance(item, dict):
                item['_processed_at'] = timestamp
                item['_source'] = self.provider_name
    
    def _get_current_timestamp(self) -> str:
        """
        Returns current timestamp in ISO format.
        """
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'
    
    def _standardize_response_format(self, data: dict) -> dict:
        """
        Standardize response format to ensure consistency between FMP and Polygon.
        
        Rules:
        1. If data is a list (FMP style), wrap it in a standardized format
        2. If data has 'results' key (Polygon style), keep it but ensure consistency
        3. Add next_url for pagination ONLY when it makes sense (list endpoints with pagination)
        4. Ensure all responses have consistent structure
        """
        if not isinstance(data, dict):
            return data
        
        if len(data) == 1 and isinstance(list(data.values())[0], list):
            # This is likely a wrapped FMP array response
            key, value = list(data.items())[0]
            if key in ['data', 'results'] or not key.startswith('_'):
                # Standardize to 'results' format
                standardized = {
                    'results': value
                }
                
                # Only add count and next_url for lists with multiple items
                if isinstance(value, list) and len(value) > 1:
                    standardized['count'] = len(value)
                    standardized['next_url'] = self._generate_next_url()
                elif isinstance(value, list) and len(value) == 1:
                    # Single item - no count needed (redundant)
                    pass
                
                return standardized
        
        # For Polygon-style responses (already have 'results' key)
        if 'results' in data:
            if isinstance(data['results'], list):
                # Ensure count is present - use existing count if available (total records)
                # or fall back to current results length
                if 'count' not in data:
                    data['count'] = len(data['results'])
                
                # Only add next_url if it makes sense for this type of endpoint
                if 'next_url' not in data and self._should_add_next_url(data['results']):
                    data['next_url'] = self._generate_next_url()
            else:
                # Single object in results - wrap it in a list for consistency
                # Single objects typically don't need pagination or count
                data['results'] = [data['results']]
                # No count for single objects (redundant)
                # No next_url for single objects
        
        # For single object responses, wrap in results format for consistency
        elif not any(key in data for key in ['results', 'count', 'next_url']):
            # This is likely a single object response
            standardized = {
                'results': [data]
            }
            # No count for single objects (redundant)
            # No next_url for single objects
            return standardized
        
        return data
    
    def _standardize_array_response(self, data: list) -> dict:
        """
        Standardize array responses (typical FMP format) to consistent format.
        """
        if not isinstance(data, list):
            return data
        
        standardized = {
            'results': data
        }
        
        # Only add count and next_url for lists with multiple items
        if len(data) > 1:
            standardized['count'] = len(data)
            standardized['next_url'] = self._generate_next_url()
        # Single item - no count needed (redundant)
        
        return standardized
    
    def _should_add_next_url(self, data: list) -> bool:
        """
        Determine if next_url should be added based on the data and endpoint type.
        
        Rules:
        1. Only add next_url for list endpoints that typically support pagination
        2. Don't add for single object responses
        3. Don't add for small lists that are likely complete results
        4. Consider the provider and typical pagination patterns
        """
        if not isinstance(data, list) or len(data) == 0:
            return False
        
        # For now, use a simple heuristic:
        # - If list has more than 1 item, it might be paginated
        
        # TODO:
        # 1. Check the current endpoint being called
        # 2. Look up if that endpoint supports pagination
        # 3. Check if the current response looks like a partial result
        # 4. Consider provider-specific pagination patterns
        
        return len(data) > 1
    
    def _generate_next_url(self) -> str:
        """
        Generate a next_url for pagination consistency.
        This creates a placeholder URL that can be used for pagination.
        """
        # For now, return a placeholder.
        return f"{self.financialdata_base_url}/api/v1/temporary/test/url"