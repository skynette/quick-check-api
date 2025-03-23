import requests, logging, time
from django.utils import timezone
from .models import Item

logger = logging.getLogger(__name__)

class HackerNewsAPI:
    """Service class for interacting with the Hacker News API"""
    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    
    @staticmethod
    def get_item(item_id):
        """Fetch an item from the Hacker News API"""
        url = f"{HackerNewsAPI.BASE_URL}/item/{item_id}.json"
        logger.debug(f"Fetching item {item_id} from HN API: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Successfully retrieved item {item_id}")
                return data
            else:
                logger.warning(f"Failed to fetch item {item_id}: HTTP {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching item {item_id}: {str(e)}")
            return None
    
    @staticmethod
    def get_max_item_id():
        """Get the max item ID from HN"""
        url = f"{HackerNewsAPI.BASE_URL}/maxitem.json"
        logger.debug(f"Fetching max item ID from HN API: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                max_id = response.json()
                logger.info(f"Current max item ID on HN: {max_id}")
                return max_id
            else:
                logger.warning(f"Failed to fetch max item ID: HTTP {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching max item ID: {str(e)}")
            return None
    
    @staticmethod
    def get_latest_items(count=100):
        """Get the latest items from HN"""
        url = f"{HackerNewsAPI.BASE_URL}/newstories.json"
        logger.debug(f"Fetching newest stories from HN API: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                item_ids = response.json()[:count]
                logger.info(f"Retrieved {len(item_ids)} newest story IDs")
                return item_ids
            else:
                logger.warning(f"Failed to fetch newest stories: HTTP {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching newest stories: {str(e)}")
            return []
    
    @staticmethod
    def sync_item(item_id):
        """Sync a single item to the database"""
        start_time = time.time()
        logger.debug(f"Starting sync for item {item_id}")
        
        # Get the item data from HN API
        data = HackerNewsAPI.get_item(item_id)
        if not data:
            logger.warning(f"No data returned for item {item_id}, skipping sync")
            return None
        
        try:
            # Convert time to datetime
            time_value = data.get('time', 0)
            if time_value:
                time_dt = timezone.datetime.fromtimestamp(time_value, tz=timezone.get_current_timezone())
            else:
                time_dt = timezone.now()
                logger.warning(f"No time value for item {item_id}, using current time")
            
            # Create or update the item
            item, created = Item.objects.update_or_create(
                item_id=item_id,
                defaults={
                    'type': data.get('type', 'story'),
                    'by': data.get('by'),
                    'time': time_dt,
                    'text': data.get('text'),
                    'dead': data.get('dead', False),
                    'kids': data.get('kids', []),
                    'url': data.get('url'),
                    'score': data.get('score', 0),
                    'title': data.get('title'),
                    'parts': data.get('parts', []),
                    'descendants': data.get('descendants', 0),
                }
            )
            
            if created:
                logger.info(f"Created new item in database: {item.type} (ID: {item.item_id})")
            else:
                logger.info(f"Updated existing item in database: {item.type} (ID: {item.item_id})")
            
            # Handle parent relationship if present
            if 'parent' in data:
                parent_id = data['parent']
                logger.debug(f"Item {item_id} has parent {parent_id}, resolving relationship")
                
                parent_item = Item.objects.filter(item_id=parent_id).first()
                if not parent_item:
                    logger.debug(f"Parent {parent_id} not in database, syncing it first")
                    parent_item = HackerNewsAPI.sync_item(parent_id)
                
                if parent_item:
                    item.parent = parent_item
                    item.save()
                    logger.debug(f"Set parent relationship for item {item_id} -> {parent_id}")
            
            # Handle poll relationship if present
            if 'poll' in data:
                poll_id = data['poll']
                logger.debug(f"Item {item_id} is related to poll {poll_id}, resolving relationship")
                
                poll_item = Item.objects.filter(item_id=poll_id).first()
                if not poll_item:
                    logger.debug(f"Poll {poll_id} not in database, syncing it first")
                    poll_item = HackerNewsAPI.sync_item(poll_id)
                
                if poll_item:
                    item.poll = poll_item
                    item.save()
                    logger.debug(f"Set poll relationship for item {item_id} -> {poll_id}")
            
            # Log completion time
            elapsed = time.time() - start_time
            logger.debug(f"Completed sync for item {item_id} in {elapsed:.2f} seconds")
            
            return item
            
        except Exception as e:
            logger.error(f"Error syncing item {item_id}: {str(e)}", exc_info=True)
            return None
    
    @staticmethod
    def sync_latest_items(count=100):
        """Sync the latest items from HN"""
        start_time = time.time()
        logger.info(f"Starting sync of latest {count} items")
        
        item_ids = HackerNewsAPI.get_latest_items(count)
        synced_count = 0
        failed_count = 0
        
        for item_id in item_ids:
            try:
                item = HackerNewsAPI.sync_item(item_id)
                if item:
                    synced_count += 1
                    
                    # Sync children (comments) for stories
                    if item.type == 'story' and item.kids:
                        logger.debug(f"Syncing {len(item.kids)} comments for story {item_id}")
                        comment_sync_count = 0
                        for kid_id in item.kids:
                            comment = HackerNewsAPI.sync_item(kid_id)
                            if comment:
                                comment_sync_count += 1
                        logger.debug(f"Synced {comment_sync_count}/{len(item.kids)} comments for story {item_id}")
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Unexpected error syncing item {item_id}: {str(e)}", exc_info=True)
                failed_count += 1

        # Log completion stats
        elapsed = time.time() - start_time
        logger.info(f"Completed sync: {synced_count} items synced, {failed_count} failed in {elapsed:.2f} seconds")
        
        return {
            "synced_count": synced_count,
            "failed_count": failed_count,
            "elapsed_time": elapsed
        }
    
    @staticmethod
    def sync_since_last(last_id=None):
        """Sync up to 100 new items since the last sync"""
        start_time = time.time()
        
        current_max = HackerNewsAPI.get_max_item_id()
        if not current_max:
            logger.error("Failed to get max item ID, aborting sync")
            return {"error": "Failed to get max item ID"}
            
        if not last_id:
            last_item = Item.objects.filter(created_locally=False).order_by('-item_id').first()
            if last_item:
                last_id = last_item.item_id
                logger.info(f"Last synced item ID from database: {last_id}")
            else:
                logger.info("No existing items in database, syncing latest 100")
                return HackerNewsAPI.sync_latest_items(100)
        
        # Calculate the range of items to sync
        sync_start = last_id + 1
        sync_end = min(current_max, last_id + 100)
        sync_total = sync_end - sync_start + 1
        logger.info(f"Syncing items from {sync_start} to {sync_end} (total: {sync_total})")
        
        synced_count = 0
        failed_count = 0
        
        for item_id in range(sync_start, sync_end + 1):
            try:
                item = HackerNewsAPI.sync_item(item_id)
                if item:
                    synced_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Error syncing item {item_id}: {str(e)}", exc_info=True)
                failed_count += 1
        
        # Log completion stats
        elapsed = time.time() - start_time
        logger.info(f"Completed incremental sync: {synced_count} items synced, {failed_count} failed in {elapsed:.2f} seconds")
        
        return {
            "last_id": sync_end,
            "current_max": current_max,
            "synced_count": synced_count,
            "failed_count": failed_count,
            "elapsed_time": elapsed
        }
