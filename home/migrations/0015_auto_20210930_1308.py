# Generated by Django 3.1.13 on 2021-09-30 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0014_themesettings_mobile_navbar_background_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='themesettings',
            name='article_card_background_color',
            field=models.CharField(blank=True, default='#ffffff', help_text='The background color of the Embedded Article in Home > Featured Content as a HEX code', max_length=8, null=True),
        ),
        migrations.AlterField(
            model_name='themesettings',
            name='article_card_font_color',
            field=models.CharField(blank=True, default='#444', help_text='The background color of the Embedded Article in Home > Featured Content as a HEX code', max_length=8, null=True),
        ),
    ]
