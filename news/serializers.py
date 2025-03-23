from rest_framework import serializers
from django.db.models import Max
from .models import Item
import logging, uuid

logger = logging.getLogger(__name__)

class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comment display (without nested comments)"""
    class Meta:
        model = Item
        exclude = ['parent', 'poll', 'kids', 'parts']

class ItemSerializer(serializers.ModelSerializer):
    """Main serializer for Item model"""
    class Meta:
        model = Item
        fields = '__all__'
        read_only_fields = ['synced_at', 'item_id']
    
    def validate(self, data):
        """Validate the data before saving"""
        logger.debug(f"Validating data for item serializer: {data}")
        
        if self.context['request'].method == 'POST':
            data['created_locally'] = True
            logger.debug("Setting created_locally=True for new item")
        
        return data
    
    def create(self, validated_data):
        """Create a new item with an automatically generated item_id"""
        logger.info(f"Creating new item via API: {validated_data.get('type')}")
        unique_part = int(uuid.uuid4().int % 10000000)
        validated_data['item_id'] = 10000000 + unique_part
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing item"""
        logger.info(f"Updating item via API: {instance.item_id}")
        return super().update(instance, validated_data)
    

class ItemDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with comments"""
    comments = serializers.SerializerMethodField()
    
    class Meta:
        model = Item
        fields = '__all__'
    
    def get_comments(self, obj):
        """Get top-level comments for this item"""
        if obj.kids:
            logger.debug(f"Fetching {len(obj.kids)} comments for item {obj.item_id}")
            comments = Item.objects.filter(item_id__in=obj.kids).order_by('-score')
            serialized = CommentSerializer(comments, many=True).data
            logger.debug(f"Retrieved {len(serialized)} comments for item {obj.item_id}")
            return serialized
        return []