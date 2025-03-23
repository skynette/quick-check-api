from django.urls import path
from .views import (
    ItemListCreateView, 
    ItemRetrieveUpdateDestroyView,
    SyncView,
)

urlpatterns = [
    path('items/', ItemListCreateView.as_view(), name='item-list'),
    path('items/<int:item_id>/', ItemRetrieveUpdateDestroyView.as_view(), name='item-detail'),
    path('sync/', SyncView.as_view(), name='sync'),
]