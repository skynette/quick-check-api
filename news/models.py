import logging
from django.db import models

logger = logging.getLogger(__name__)

class Item(models.Model):
    """
    Model representing a Hacker News item (story, comment, job, etc.)
    """
    ITEM_TYPES = (
        ('story', 'Story'),
        ('comment', 'Comment'),
        ('job', 'Job'),
        ('poll', 'Poll'),
        ('pollopt', 'Poll Option'),
    )
    
    item_id = models.IntegerField(
        unique=True,
        help_text="The item's unique identifier on Hacker News."
    )
    type = models.CharField(
        max_length=10,
        choices=ITEM_TYPES,
        help_text="The type of item. Can be one of: 'story', 'comment', 'job', 'poll', or 'pollopt'."
    )
    by = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The username of the item's author."
    )
    time = models.DateTimeField(
        help_text="Creation date of the item, in Unix Time."
    )
    text = models.TextField(
        null=True,
        blank=True,
        help_text="The comment, story, or poll text. May contain HTML."
    )
    dead = models.BooleanField(
        default=False,
        help_text="Indicates whether the item is marked as dead."
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        help_text="The parent of the comment, which can be another comment or the relevant story."
    )
    poll = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='poll_options',
        help_text="The poll associated with a poll option."
    )
    kids = models.JSONField(
        default=list,
        blank=True,
        null=True,
        help_text="A list of IDs of the item's comments, in ranked display order."
    )
    url = models.URLField(
        max_length=2000,
        null=True,
        blank=True,
        help_text="The URL of the story."
    )
    score = models.IntegerField(
        default=0,
        help_text="The story's score or the number of votes for a poll option."
    )
    title = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="The title of the story, poll, or job. May contain HTML."
    )
    parts = models.JSONField(
        default=list,
        blank=True,
        null=True,
        help_text="A list of related poll options, in display order."
    )
    descendants = models.IntegerField(
        default=0,
        help_text="For stories or polls, the total number of comments."
    )
    
    created_locally = models.BooleanField(
        default=False,
        help_text="Indicates whether the item was created locally (not fetched from Hacker News)."
    )
    synced_at = models.DateTimeField(
        auto_now=True,
        help_text="The timestamp when the item was last synced with Hacker News."
    )
    
    def __str__(self):
        return f"{self.type}: {self.title or self.text or self.item_id}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"Created new item: {self.type} (ID: {self.item_id})")
        else:
            logger.info(f"Updated item: {self.type} (ID: {self.item_id})")
    
    class Meta:
        ordering = ['-time']