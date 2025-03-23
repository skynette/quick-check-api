import logging
from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters import FilterSet, CharFilter, BooleanFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Item
from .serializers import ItemSerializer, ItemDetailSerializer
from .services import HackerNewsAPI

logger = logging.getLogger(__name__)

class ItemFilter(FilterSet):
    """FilterSet for Item model"""
    type = CharFilter(field_name='type')
    by = CharFilter(field_name='by')
    dead = BooleanFilter(field_name='dead')
    created_locally = BooleanFilter(field_name='created_locally')
    top_level = BooleanFilter(method='filter_top_level')
    
    def filter_top_level(self, queryset, name, value):
        """Filter for top-level items (no parent)"""
        if value:
            return queryset.filter(parent__isnull=True)
        return queryset
    
    class Meta:
        model = Item
        fields = ['type', 'by', 'dead', 'created_locally']


class ItemListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating HN items.
    
    GET:
    - Returns a paginated list of items
    - Supports filtering by type, author, dead status, and more
    - Supports search in title, text, and author fields
    - Supports sorting by various fields
    
    POST:
    - Creates a new item locally (not on Hacker News)
    - item_id is automatically generated for local items
    - All local items are marked with created_locally=True
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ItemFilter
    search_fields = ['title', 'text', 'by']
    ordering_fields = ['time', 'score', 'descendants', 'item_id']
    
    def create(self, request, *args, **kwargs):
        """Override create method to handle item creation and add logging"""
        logger.info(f"ItemListCreateView.create called with data: {request.data}")
        
        if 'item_id' in request.data:
            logger.warning(f"User attempted to provide item_id: {request.data['item_id']}. This will be ignored.")
            request_data = request.data.copy()
            request_data.pop('item_id')
            request._full_data = request_data
            
        if 'time' not in request.data:
            from django.utils import timezone
            request_data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
            request_data['time'] = timezone.now().isoformat()
            request._full_data = request_data
            logger.info("Added current time to request data")
        
        return super().create(request, *args, **kwargs)


class ItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting individual items.
    
    GET:
    - Returns detailed information about a specific item, including comments
    
    PUT/PATCH:
    - Updates a locally created item (not from Hacker News)
    
    DELETE:
    - Deletes a locally created item (not from Hacker News)
    """
    queryset = Item.objects.all()
    serializer_class = ItemDetailSerializer
    lookup_field = 'item_id'
    
    def get_serializer_class(self):
        """Use different serializers for different methods"""
        if self.request.method == 'GET':
            return ItemDetailSerializer
        return ItemSerializer
    
    def update(self, request, *args, **kwargs):
        """Override update method to add protection for HN items"""
        item_id = kwargs.get('item_id')
        logger.info(f"ItemRetrieveUpdateDestroyView.update called for item_id: {item_id}")
        
        instance = self.get_object()
        if not instance.created_locally:
            logger.warning(f"Attempted to update HN-sourced item {item_id}")
            return Response(
                {"error": "Cannot update items retrieved from Hacker News"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy method to add protection for HN items"""
        item_id = kwargs.get('item_id')
        logger.info(f"ItemRetrieveUpdateDestroyView.destroy called for item_id: {item_id}")
        
        instance = self.get_object()
        if not instance.created_locally:
            logger.warning(f"Attempted to delete HN-sourced item {item_id}")
            return Response(
                {"error": "Cannot delete items retrieved from Hacker News"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class SyncView(APIView):
    """
    API endpoint for manually triggering a sync with Hacker News.
    
    POST:
    - Triggers a sync with Hacker News
    - Can specify a count parameter to limit the number of items to sync
    """
    def post(self, request, format=None):
        """Handle POST requests to trigger a sync"""
        logger.info(f"SyncView.post called with data: {request.data}")
        
        try:
            count = request.data.get('count', 100)
            try:
                count = int(count)
            except (TypeError, ValueError):
                count = 100
                logger.warning(f"Invalid count parameter: {request.data.get('count')}, using default: 100")

            logger.info(f"Starting manual sync with count={count}")
            result = HackerNewsAPI.sync_latest_items(count)
            
            return Response({
                "status": "success",
                "result": result,
                "message": f"Successfully synced {result.get('synced_count', 0)} items"
            })
        except Exception as e:
            logger.error(f"Error in manual sync: {str(e)}", exc_info=True)
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
