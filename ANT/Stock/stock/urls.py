"""stock URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path
from django.urls import include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('goods/', include('goods.urls')),
    path('stock/', include('stocks.urls')),
    path('mnf/', include('mnf.urls')),
    #static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
    path('', RedirectView.as_view(url='/mnf/', permanent=True)),
    # старая главная страница
    path('stock/', RedirectView.as_view(url='/mnf/', permanent=True)),
    path('accounts/', include('django.contrib.auth.urls')),
    path('trd/', include('trd.urls')),
    path('intg/', include('intg.urls')),
    path('rest/', include('stock.rest_urls')),
]
