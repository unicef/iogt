# Generated by Django 3.1.13 on 2021-07-20 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaires', '0002_auto_20210719_1820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizformfield',
            name='correct_answer',
            field=models.CharField(help_text='Comma separated list of choices. Only applicable in checkboxes, radio, dropdown and multiselect.', max_length=256, verbose_name='correct_answer'),
        ),
    ]
