from django.urls import path
from .views import GassmeterListView


urlpatterns = [
    path('list/', GassmeterListView.as_view(), name='gassmeter_list'),
]