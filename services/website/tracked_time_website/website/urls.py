from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path, include
from .views import *

urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    path('api/trackedtime/', TrackedTimeListView.as_view()),
    path('api/trackedtime/<int:pk>/', TrackedTimeDetailView.as_view()),
    path('apps/', AppsView.as_view(), name="apps"),
]