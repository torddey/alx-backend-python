# Generated manually for message editing functionality

import uuid
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def generate_uuid():
    """Generate a unique UUID for model fields."""
    return uuid.uuid4()


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0001_initial'),
    ]

    operations = [
        # Add UUID fields to existing models
        migrations.AddField(
            model_name='user',
            name='user_id',
            field=models.UUIDField(default=generate_uuid, unique=True, editable=False),
        ),
        migrations.AddField(
            model_name='conversation',
            name='conversation_id',
            field=models.UUIDField(default=generate_uuid, unique=True, editable=False),
        ),
        migrations.AddField(
            model_name='message',
            name='message_id',
            field=models.UUIDField(default=generate_uuid, unique=True, editable=False),
        ),
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        # Add message editing fields
        migrations.AddField(
            model_name='message',
            name='edited',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='message',
            name='edited_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        # Create MessageHistory model
        migrations.CreateModel(
            name='MessageHistory',
            fields=[
                ('history_id', models.UUIDField(default=generate_uuid, editable=False, primary_key=True, serialize=False)),
                ('old_content', models.TextField()),
                ('edited_at', models.DateTimeField(auto_now_add=True)),
                ('edited_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_edits', to='chats.user')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='chats.message')),
            ],
            options={
                'ordering': ['-edited_at'],
            },
        ),
    ] 