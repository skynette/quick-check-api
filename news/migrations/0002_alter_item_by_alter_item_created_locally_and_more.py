# Generated by Django 4.2.10 on 2025-03-23 14:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='by',
            field=models.CharField(blank=True, help_text="The username of the item's author.", max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='created_locally',
            field=models.BooleanField(default=False, help_text='Indicates whether the item was created locally (not fetched from Hacker News).'),
        ),
        migrations.AlterField(
            model_name='item',
            name='dead',
            field=models.BooleanField(default=False, help_text='Indicates whether the item is marked as dead.'),
        ),
        migrations.AlterField(
            model_name='item',
            name='descendants',
            field=models.IntegerField(default=0, help_text='For stories or polls, the total number of comments.'),
        ),
        migrations.AlterField(
            model_name='item',
            name='item_id',
            field=models.IntegerField(help_text="The item's unique identifier on Hacker News.", unique=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='kids',
            field=models.JSONField(blank=True, default=list, help_text="A list of IDs of the item's comments, in ranked display order.", null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='parent',
            field=models.ForeignKey(blank=True, help_text='The parent of the comment, which can be another comment or the relevant story.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='news.item'),
        ),
        migrations.AlterField(
            model_name='item',
            name='parts',
            field=models.JSONField(blank=True, default=list, help_text='A list of related poll options, in display order.', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='poll',
            field=models.ForeignKey(blank=True, help_text='The poll associated with a poll option.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='poll_options', to='news.item'),
        ),
        migrations.AlterField(
            model_name='item',
            name='score',
            field=models.IntegerField(default=0, help_text="The story's score or the number of votes for a poll option."),
        ),
        migrations.AlterField(
            model_name='item',
            name='synced_at',
            field=models.DateTimeField(auto_now=True, help_text='The timestamp when the item was last synced with Hacker News.'),
        ),
        migrations.AlterField(
            model_name='item',
            name='text',
            field=models.TextField(blank=True, help_text='The comment, story, or poll text. May contain HTML.', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='time',
            field=models.DateTimeField(help_text='Creation date of the item, in Unix Time.'),
        ),
        migrations.AlterField(
            model_name='item',
            name='title',
            field=models.CharField(blank=True, help_text='The title of the story, poll, or job. May contain HTML.', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='type',
            field=models.CharField(choices=[('story', 'Story'), ('comment', 'Comment'), ('job', 'Job'), ('poll', 'Poll'), ('pollopt', 'Poll Option')], help_text="The type of item. Can be one of: 'story', 'comment', 'job', 'poll', or 'pollopt'.", max_length=10),
        ),
        migrations.AlterField(
            model_name='item',
            name='url',
            field=models.URLField(blank=True, help_text='The URL of the story.', max_length=2000, null=True),
        ),
    ]
