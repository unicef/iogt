# Generated by Django 3.1.13 on 2021-09-20 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cannedresponse',
            name='header',
            field=models.TextField(null=True),
        ),
    ]
