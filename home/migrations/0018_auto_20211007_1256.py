# Generated by Django 3.1.8 on 2021-10-07 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0017_merge_20211004_1341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iogtflatmenuitem',
            name='color',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='iogtflatmenuitem',
            name='color_text',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
