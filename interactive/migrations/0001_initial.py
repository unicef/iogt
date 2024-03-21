# Generated by Django 3.2.24 on 2024-03-21 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InteractiveChannel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(help_text='Name for the interactive bot that the user will seen when interacting with it', max_length=80)),
                ('request_url', models.URLField(help_text='To set up a interactive bot channel on your RapidPro server and get a request URL, follow the steps outline in the Section "Setting up a Chatbot channel" here: https://github.com/unicef/iogt/blob/develop/messaging/README.md')),
            ],
        ),
    ]
