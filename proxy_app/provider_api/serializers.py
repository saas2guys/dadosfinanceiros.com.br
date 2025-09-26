from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse
from rest_framework import serializers
from django.conf import settings
from .enums import DeniedHosts, DeniedParameters, EndpointTo, EndpointFrom
import logging

logger = logging.getLogger(__name__)

class BaseResponseSerializer(serializers.BaseSerializer):
    """
    Base serializer for processing data received from providers.
    Handles common URL filtering and transformations.
    """
    
    def __init__(self, current_view=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.financialdata_base_url = getattr(settings, 'FINANCIALDATA_BASE_URL', 'https://financialdata.online')
        self.current_view = current_view
        
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
            processed_data = self._process_data(data)
            # Standardize response format based on provider
            standardized_data = self._standardize_response_format(processed_data)
            # Add provider metadata to results if present
            if 'results' in standardized_data and isinstance(standardized_data['results'], list):
                self._add_provider_metadata(standardized_data['results'])
            return standardized_data
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
    
    def _get_current_timestamp(self) -> str:
        """
        Returns current timestamp in ISO format.
        """
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'
    
    
    
    def _standardize_array_response(self, data: list) -> dict:
        """
        Standardize array responses (typical FMP format) to consistent format.
        """
        if not isinstance(data, list):
            return data
        
        standardized = {
            'results': data
        }
        
        # Only add count for lists with multiple items
        if len(data) > 1:
            standardized['count'] = len(data)
        # Single item - no count needed (redundant)
        
        return standardized


class PolygonResponseSerializer(BaseResponseSerializer):
    """
    Serializer for Polygon API responses.
    Handles Polygon-specific transformations and pagination.
    """
    
    def _map_polygon_path_to_our_path(self, polygon_path: str, current_view=None) -> str:
        """
        Map Polygon API paths to our API paths using current view context.
        """
        base = EndpointFrom.PREFIX_ENDPOINT.value
        
        # If we have the current view context, use its endpoint mapping
        if current_view and hasattr(current_view, 'endpoint_from') and hasattr(current_view, 'endpoint_to'):
            try:
                # Get the current view's endpoint_from path
                our_path = current_view.endpoint_from.value
                result = f"{base}{our_path}"
                logger.debug(f"Using view context: {polygon_path} -> {result}")
                return result
            except Exception as e:
                logger.debug(f"Failed to use view context: {e}")
        
        # If no view context, return generic base URL without endpoint
        logger.debug(f"No view context, returning base URL: {base}")
        return base
    
    def _process_next_url(self, next_url: str) -> str:
        """
        Process next_url to replace provider URL with our URL.
        Maps Polygon paths to our API paths and preserves query parameters.
        """
        if not isinstance(next_url, str):
            return next_url
        
        try:
            parsed = urlparse(next_url)
            
            # Map Polygon paths to our API paths
            polygon_path = parsed.path
            our_path = self._map_polygon_path_to_our_path(polygon_path, self.current_view)
            query = f"?{parsed.query}" if parsed.query else ""
            
            # Build our URL with the mapped path and query
            # Remove trailing slash before query parameters
            if our_path.endswith('/') and query.startswith('?'):
                our_path = our_path.rstrip('/')
            return f"{self.financialdata_base_url}{our_path}{query}"
        except Exception:
            # If parsing fails, return a fallback URL
            return f"{self.financialdata_base_url}/api/v1/error/"
    
    def _standardize_response_format(self, data: dict) -> dict:
        """
        Standardize response format for Polygon responses.
        """
        if not isinstance(data, dict):
            return data
        
        if len(data) == 1 and isinstance(list(data.values())[0], list) and 'results' not in data:
            key, value = list(data.items())[0]
            if key == 'results':
                if 'count' not in data:
                    data['count'] = len(value)
                return data
            if key in ['data', 'results'] or not key.startswith('_'):
                standardized = {
                    'results': value
                }
                
                if isinstance(value, list) and len(value) > 1:
                    standardized['count'] = len(value)
                
                return standardized
        
        if 'results' in data:
            if isinstance(data['results'], list):
                if 'count' not in data:
                    data['count'] = len(data['results'])
                
                if 'next_url' in data:
                    data['next_url'] = self._process_next_url(data['next_url'])
            else:
                data['results'] = [data['results']]
        
        elif not any(key in data for key in ['results', 'count', 'next_url']):
            standardized = {
                'results': [data]
            }
            return standardized
        
        return data


class FMPResponseSerializer(BaseResponseSerializer):
    """
    Serializer for FMP API responses.
    Handles FMP-specific transformations without pagination.
    """
    
    def _standardize_response_format(self, data: dict) -> dict:
        """
        Standardize response format for FMP responses.
        """
        if not isinstance(data, dict):
            return data
        
        if len(data) == 1 and isinstance(list(data.values())[0], list):
            key, value = list(data.items())[0]
            if key in ['data', 'results'] or not key.startswith('_'):
                standardized = {
                    'results': value
                }
                
                if isinstance(value, list) and len(value) > 1:
                    standardized['count'] = len(value)
                
                return standardized
        
        if 'results' in data:
            if isinstance(data['results'], list):
                if 'count' not in data:
                    data['count'] = len(data['results'])
            else:
                data['results'] = [data['results']]
        
        elif not any(key in data for key in ['results', 'count', 'next_url']):
            standardized = {
                'results': [data]
            }
            return standardized
        
        return data


ProviderResponseSerializer = BaseResponseSerializer
    