from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from .serializers import UserRegistrationSerializer, UserSerializer, TokenRegenerationSerializer, TokenHistorySerializer
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from .models import User, TokenHistory
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class RegenerateRequestTokenView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TokenRegenerationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        
        # Update token settings if provided
        if 'auto_renew' in serializer.validated_data:
            user.token_auto_renew = serializer.validated_data['auto_renew']
        if 'validity_days' in serializer.validated_data:
            user.token_validity_days = serializer.validated_data['validity_days']
        
        # Generate new token
        save_old = serializer.validated_data.get('save_old', True)
        user.generate_new_request_token(save_old=save_old)
        
        return Response(user.get_token_info(), status=status.HTTP_200_OK)

class TokenHistoryView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        return Response({
            'current_token': user.get_token_info(),
            'previous_tokens': user.previous_tokens
        }, status=status.HTTP_200_OK)

def home(request):
    """Render the home page."""
    return render(request, 'home.html')

@login_required
def profile(request):
    """Render the user profile page."""
    # Get all token history
    token_history = TokenHistory.objects.filter(user=request.user).order_by('-created_at')
    
    # Get current token info
    token_info = request.user.get_token_info()
    
    # Add active status to token info
    token_info['is_active'] = not request.user.is_token_expired()
    
    context = {
        'token_info': token_info,
        'token_history': token_history,
        'user': request.user,
        'daily_usage': {
            'made': request.user.daily_requests_made,
            'limit': request.user.daily_request_limit,
            'remaining': request.user.daily_request_limit - request.user.daily_requests_made
        }
    }
    return render(request, 'profile.html', context)

@login_required
@require_http_methods(['POST'])
def regenerate_token(request):
    """Handle token regeneration request from the frontend."""
    try:
        never_expires = request.POST.get('never_expires') == 'true'
        request.user.generate_new_request_token(save_old=True, never_expires=never_expires)
        messages.success(request, 'New token generated successfully.')
    except Exception as e:
        messages.error(request, f'Failed to generate new token: {str(e)}')
    
    return redirect('profile')

@api_view(['GET', 'POST'])
def register_user(request):
    """Handle both frontend and API registration."""
    if request.content_type == 'application/json':
        # API request
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Set initial token dates
            user.request_token_created = timezone.now()
            user.request_token_expires = user.request_token_created + timedelta(days=user.token_validity_days)
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        # Frontend request
        if request.method == 'GET':
            return render(request, 'register.html')
        elif request.method == 'POST':
            serializer = UserRegistrationSerializer(data=request.POST)
            if serializer.is_valid():
                user = serializer.save()
                # Set initial token dates
                user.request_token_created = timezone.now()
                user.request_token_expires = user.request_token_created + timedelta(days=user.token_validity_days)
                user.save()
                login(request, user)
                messages.success(request, 'Registration successful! Welcome!')
                return redirect('profile')
            else:
                for field, errors in serializer.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
                return render(request, 'register.html')

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """API endpoint for getting/updating user profile."""
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def regenerate_request_token(request):
    """API endpoint for token regeneration."""
    try:
        save_old = request.data.get('save_old', True)
        auto_renew = request.data.get('auto_renew', request.user.auto_renew_token)
        validity_days = request.data.get('validity_days', request.user.token_validity_days)

        request.user.regenerate_request_token(
            save_old=save_old,
            auto_renew=auto_renew,
            validity_days=validity_days
        )
        
        return Response({
            'request_token': request.user.request_token,
            'created': request.user.token_created_at,
            'expires': request.user.token_expires_at,
            'auto_renew': request.user.auto_renew_token,
            'validity_days': request.user.token_validity_days
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def token_history(request):
    """API endpoint for token history."""
    history = TokenHistory.objects.filter(user=request.user).order_by('-created_at')[:5]
    serializer = TokenHistorySerializer(history, many=True)
    return Response(serializer.data)
