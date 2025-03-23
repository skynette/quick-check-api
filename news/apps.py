from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    # def ready(self):
    #     """
    #     Initialize the app, including starting the scheduler
    #     """
    #     from . import scheduler
    #     try:
    #         scheduler.start()
    #         logger.info("APScheduler has been started")
    #     except Exception as e:
    #         logger.error(f"Failed to start APScheduler: {str(e)}", exc_info=True)