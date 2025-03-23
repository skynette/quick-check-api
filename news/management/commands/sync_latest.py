import logging
from django.core.management.base import BaseCommand
from news.services import HackerNewsAPI

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sync the latest items from Hacker News API'
    
    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=100, help='Number of items to sync')
    
    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(f"Syncing {count} latest items from Hacker News...")
        
        try:
            result = HackerNewsAPI.sync_latest_items(count)
            self.stdout.write(self.style.SUCCESS(
                f"Successfully synced {result.get('synced_count', 0)} items "
                f"({result.get('failed_count', 0)} failed) "
                f"in {result.get('elapsed_time', 0):.2f} seconds"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error syncing items: {str(e)}"))
            logger.error(f"Error in sync_latest command: {str(e)}", exc_info=True)