# Generated by Django 3.1.11 on 2021-06-01 17:33

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0059_apply_collection_ordering'),
        ('wagtailimages', '0022_uploadedimage'),
        ('home', '0004_auto_20210409_1243'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('external_link', models.URLField(blank=True, help_text='Optional external link which a banner will link to e.g., https://www.google.com', null=True)),
                ('banner_image', models.ForeignKey(help_text='Image to display as the banner', on_delete=django.db.models.deletion.PROTECT, related_name='+', to='wagtailimages.image')),
                ('banner_link_page', models.ForeignKey(blank=True, help_text='Optional page to which the banner will link to', null=True, on_delete=django.db.models.deletion.SET_NULL, to='wagtailcore.page')),
            ],
        ),
        migrations.CreateModel(
            name='PageBanner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('banner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.banner')),
                ('source', modelcluster.fields.ParentalKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='page_banners', to='wagtailcore.page')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FeaturedContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('content', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wagtailcore.page')),
                ('source', modelcluster.fields.ParentalKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='featured_content', to='home.homepage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
