# Generated by Django 3.1.13 on 2021-11-05 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0026_auto_20211029_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iogtflatmenuitem',
            name='link_url',
            field=models.CharField(blank=True, help_text='If you are linking back to a URL on your own IoGT site, be sure to remove the domain and everything before it. For example "http://sd.goodinternet.org/url/" should instead be "/url/".', max_length=255, null=True, verbose_name='link to a custom URL'),
        ),
    ]
