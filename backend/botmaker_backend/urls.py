"""
URL configuration for botmaker_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.contrib import admin
from django.urls import path, include
from api.coinbase_auth import connect_coinbase, coinbase_callback  # adjust path as necessary


def index(request):
    return HttpResponse("Welcome to BotMaker Backend API!")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('coinbase/connect/', connect_coinbase, name='connect-coinbase'),
    path('coinbase/callback/', coinbase_callback, name='coinbase-callback'),
]
