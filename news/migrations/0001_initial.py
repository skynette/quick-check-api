# Generated by Django 4.2.10 on 2025-03-23 08:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_id', models.IntegerField(unique=True)),
                ('type', models.CharField(choices=[('story', 'Story'), ('comment', 'Comment'), ('job', 'Job'), ('poll', 'Poll'), ('pollopt', 'Poll Option')], max_length=10)),
                ('by', models.CharField(blank=True, max_length=255, null=True)),
                ('time', models.DateTimeField()),
                ('text', models.TextField(blank=True, null=True)),
                ('dead', models.BooleanField(default=False)),
                ('kids', models.JSONField(blank=True, default=list)),
                ('url', models.URLField(blank=True, max_length=2000, null=True)),
                ('score', models.IntegerField(default=0)),
                ('title', models.CharField(blank=True, max_length=500, null=True)),
                ('parts', models.JSONField(blank=True, default=list)),
                ('descendants', models.IntegerField(default=0)),
                ('created_locally', models.BooleanField(default=False)),
                ('synced_at', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='news.item')),
                ('poll', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='poll_options', to='news.item')),
            ],
            options={
                'ordering': ['-time'],
            },
        ),
    ]
