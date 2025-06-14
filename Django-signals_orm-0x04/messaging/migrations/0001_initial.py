# Generated by Django 5.2.1 on 2025-06-15 00:15

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('message_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_direct_messages', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_direct_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('notification_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('notification_type', models.CharField(choices=[('message', 'New Message'), ('mention', 'Mention'), ('system', 'System Notification')], default='message', max_length=20)),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('message', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='messaging.message')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['sender', 'receiver'], name='messaging_m_sender__5ce791_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['timestamp'], name='messaging_m_timesta_bd3028_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['is_read'], name='messaging_m_is_read_8b9e91_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', 'is_read'], name='messaging_n_user_id_bd7d88_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['created_at'], name='messaging_n_created_a9b879_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['notification_type'], name='messaging_n_notific_98cedd_idx'),
        ),
    ]
