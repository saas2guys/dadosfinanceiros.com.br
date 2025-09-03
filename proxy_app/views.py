from django.shortcuts import render
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated


def api_documentation(request):
    return render(request, "api/docs.html")
