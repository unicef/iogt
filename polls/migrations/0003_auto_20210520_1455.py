# Generated by Django 3.1.11 on 2021-05-20 10:55

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0060_fix_workflow_unique_constraint'),
        ('polls', '0002_auto_20210520_1358'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pollpage',
            options={},
        ),
        migrations.RemoveField(
            model_name='pollpage',
            name='choices',
        ),
        migrations.RemoveField(
            model_name='pollpage',
            name='clean_name',
        ),
        migrations.RemoveField(
            model_name='pollpage',
            name='default_value',
        ),
        migrations.RemoveField(
            model_name='pollpage',
            name='field_type',
        ),
        migrations.RemoveField(
            model_name='pollpage',
            name='help_text',
        ),
        migrations.RemoveField(
            model_name='pollpage',
            name='id',
        ),
        migrations.RemoveField(
            model_name='pollpage',
            name='label',
        ),
        migrations.RemoveField(
            model_name='pollpage',
            name='required',
        ),
        migrations.RemoveField(
            model_name='pollpage',
            name='sort_order',
        ),
        migrations.AddField(
            model_name='pollpage',
            name='from_address',
            field=models.CharField(blank=True, max_length=255, verbose_name='from address'),
        ),
        migrations.AddField(
            model_name='pollpage',
            name='page_ptr',
            field=models.OneToOneField(auto_created=True, default=1, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pollpage',
            name='subject',
            field=models.CharField(blank=True, max_length=255, verbose_name='subject'),
        ),
        migrations.AddField(
            model_name='pollpage',
            name='to_address',
            field=models.CharField(blank=True, help_text='Optional - form submissions will be emailed to these addresses. Separate multiple addresses by comma.', max_length=255, verbose_name='to address'),
        ),
        migrations.AlterField(
            model_name='formfield',
            name='page',
            field=modelcluster.fields.ParentalKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='form_fields', to='polls.pollpage'),
        ),
    ]
