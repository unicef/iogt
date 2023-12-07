# Generated by Django 3.2.23 on 2023-12-07 19:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0053_alter_sitesettings_mtm_container_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="themesettings",
            name="navbar_background_color",
            field=models.CharField(
                blank=True,
                default="#0094F4",
                help_text="The background color of the navbar as a HEX code",
                max_length=8,
                null=True,
                verbose_name="Flat menu background color",
            ),
        ),
        migrations.AlterField(
            model_name="themesettings",
            name="navbar_font_color",
            field=models.CharField(
                blank=True,
                default="#FFFFFF",
                help_text="The font color of the navbar as a HEX code",
                max_length=8,
                null=True,
                verbose_name="Flat menu font color",
            ),
        ),
    ]
