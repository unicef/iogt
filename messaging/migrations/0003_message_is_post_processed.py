# Generated by Django 3.1.14 on 2021-12-08 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0002_auto_20210719_1332'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_post_processed',
            field=models.BooleanField(default=False),
        ),
    ]
