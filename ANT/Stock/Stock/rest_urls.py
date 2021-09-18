from django.urls import path, include

urlpatterns = [
    path('intg/', include('intg.rest_urls')),
]
