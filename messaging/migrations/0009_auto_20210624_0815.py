# Generated by Django 3.1.12 on 2021-06-24 08:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0008_auto_20210623_1102'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='content',
            new_name='text',
        ),
        migrations.RemoveField(
            model_name='chatbotchannel',
            name='identifier',
        ),
        migrations.RemoveField(
            model_name='message',
            name='attachments',
        ),
    ]
