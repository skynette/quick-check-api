import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from .services import HackerNewsAPI

logger = logging.getLogger(__name__)

def sync_hackernews_job():
    """Job to sync data from Hacker News API"""
    logger.info(f"Running scheduled HackerNews sync job at {datetime.now()}")
    try:
        result = HackerNewsAPI.sync_since_last()
        logger.info(f"Scheduled sync complete: {result}")
    except Exception as e:
        logger.error(f"Error in scheduled sync job: {str(e)}", exc_info=True)

def start():
    print("start function called for scheduler")
    """Start the APScheduler and perform an initial sync"""
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    print("scheduler created")
    
    # # Perform an initial sync before starting the scheduler
    # logger.info("Performing initial sync...")
    # try:
    #     result = HackerNewsAPI.sync_since_last()
    #     logger.info(f"Initial sync complete: {result}")
    # except Exception as e:
    #     logger.error(f"Error during initial sync: {str(e)}", exc_info=True)
    
    # Schedule the sync job to run every 5 minutes
    scheduler.add_job(
        sync_hackernews_job,
        'interval',
        minutes=5,
        name='sync_hackernews_data',
        jobstore='default',
        replace_existing=True,
        id='sync_hackernews_data'
    )
    
    logger.info("Starting APScheduler...")
    scheduler.start()