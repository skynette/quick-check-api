import logging
from django.core.management.base import BaseCommand
from news.services import HackerNewsAPI

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sync items since the last synced item'
    
    def handle(self, *args, **options):
        self.stdout.write("Syncing items since last sync...")
        
        try:
            result = HackerNewsAPI.sync_since_last()
            
            if 'error' in result:
                self.stdout.write(self.style.ERROR(f"Sync failed: {result['error']}"))
                return
                
            self.stdout.write(self.style.SUCCESS(
                f"Successfully synced {result.get('synced_count', 0)} items "
                f"({result.get('failed_count', 0)} failed) "
                f"in {result.get('elapsed_time', 0):.2f} seconds. "
                f"Items synced: {result.get('last_id', 0)} to {result.get('current_max', 0)}"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error syncing items: {str(e)}"))
            logger.error(f"Error in sync_since_last command: {str(e)}", exc_info=True)