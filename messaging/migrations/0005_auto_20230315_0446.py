# Generated by Django 3.1.14 on 2023-03-15 04:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0004_auto_20211217_1319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='rapidpro_message_id',
            field=models.BigIntegerField(null=True),
        ),
    ]
