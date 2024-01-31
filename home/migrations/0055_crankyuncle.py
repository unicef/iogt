# Generated by Django 3.2.23 on 2024-01-31 10:06

import cranky_uncle.blocks
from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0066_collection_management_permissions'),
        ('wagtailimages', '0023_add_choose_permissions'),
        ('home', '0054_auto_20231207_1936'),
    ]

    operations = [
        migrations.CreateModel(
            name='CrankyUncle',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('body', wagtail.core.fields.StreamField([('cranky_uncle_bot', wagtail.core.blocks.StructBlock([('subject', wagtail.core.blocks.CharBlock()), ('button_text', wagtail.core.blocks.CharBlock()), ('trigger_string', wagtail.core.blocks.CharBlock()), ('cranky_uncle_channel', cranky_uncle.blocks.CrankyUncleChannelChooserBlock())]))], blank=True, null=True)),
                ('lead_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='wagtailimages.image')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
