from typing import Any
from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.contrib.auth.models import User
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from rest_framework import status 
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from collections import defaultdict
from datetime import timedelta

from .serializers import TrackedTimeSerializer
from .models import TrackedTime
from .permissions import IsOwnerOrRestricted


class IndexView(TemplateView):
    template_name = "website/index.html"


class AppsView(LoginRequiredMixin, ListView):
    model = TrackedTime 
    login_url = reverse_lazy('login')
    template_name = "website/time_data.html"
    context_object_name = "apps_data"
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        all_apps = context["apps_data"]
        apps_data = defaultdict(lambda: timedelta())
        for elem in all_apps:
            if elem.user.id == self.request.user.id:
                for app, time in elem.apps.items():
                    hours, minutes, seconds = map(int, time.split(':'))
                    apps_data[app] += timedelta(hours=hours, minutes=minutes, seconds=seconds)
        for key in apps_data:
            apps_data[key] = str(apps_data[key])
        apps_data = dict(apps_data)
        context["apps_data"] = apps_data
        return context



class TrackedTimeListView(ListCreateAPIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TrackedTimeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['day', 'month', 'year']
    def get_queryset(self):
        user = self.request.user
        return user.trackedtimes.all()
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    # def get(self, request):
    #     tracked_time = TrackedTime.objects.filter(user=request.user)
    #     serializer = TrackedTimeSerializer(tracked_time, many=True)
    #     return Response(serializer.data)
    # def post(self, request):
    #     serializer = TrackedTimeSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save(user=request.user)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# TODO: REWRITE TO GENERIC VIEWS
class TrackedTimeDetailView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerOrRestricted]

    def get_object(self, pk):
        try:
            return TrackedTime.objects.get(pk=pk)
        except TrackedTime.DoesNotExist:
            raise Http404


    def get(self, request, pk):
        TrackedTime = self.get_object(pk)
        serializer = TrackedTimeSerializer(TrackedTime)
        return Response(serializer.data)
    
    def patch(self, request, pk):
        tracked_time = self.get_object(pk)
        serializer = TrackedTimeSerializer(tracked_time, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        TrackedTime = self.get_object(pk)
        TrackedTime.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)