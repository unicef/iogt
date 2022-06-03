# Generated by Django 3.1.14 on 2022-06-03 10:58

from django.db import migrations, models
import django.db.models.deletion
import home.blocks
import home.mixins
import messaging.blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks
import wagtailmarkdown.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0059_apply_collection_ordering'),
        ('wagtailsvg', '0002_svg_edit_code'),
        ('wagtailimages', '0022_uploadedimage'),
        ('home', '0046_auto_20220422_1825'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='offlineapppage',
            options={'verbose_name': 'Offline App Page', 'verbose_name_plural': 'Offline App Pages'},
        ),
        migrations.CreateModel(
            name='PWAPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('commenting_status', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed'), ('disabled', 'Disabled'), ('timestamped', 'Timestamped'), ('inherited', 'Inherited')], default='inherited', max_length=15)),
                ('commenting_starts_at', models.DateTimeField(blank=True, null=True)),
                ('commenting_ends_at', models.DateTimeField(blank=True, null=True)),
                ('index_page_description', models.TextField(blank=True, null=True)),
                ('body', wagtail.core.fields.StreamField([('heading', wagtail.core.blocks.CharBlock(form_classname='full title', template='blocks/heading.html')), ('paragraph', wagtail.core.blocks.RichTextBlock(features=['h2', 'h3', 'h4', 'bold', 'italic', 'ol', 'ul', 'hr', 'link', 'document-link', 'image'])), ('markdown', wagtailmarkdown.blocks.MarkdownBlock(icon='code')), ('paragraph_v1_legacy', home.blocks.RawHTMLBlock(icon='code')), ('image', wagtail.images.blocks.ImageChooserBlock(template='blocks/image.html')), ('list', wagtail.core.blocks.ListBlock(wagtailmarkdown.blocks.MarkdownBlock(icon='code'))), ('numbered_list', home.blocks.NumberedListBlock(wagtailmarkdown.blocks.MarkdownBlock(icon='code'))), ('page_button', wagtail.core.blocks.StructBlock([('page', wagtail.core.blocks.PageChooserBlock()), ('text', wagtail.core.blocks.CharBlock(max_length=255, required=False))])), ('embedded_poll', wagtail.core.blocks.StructBlock([('direct_display', wagtail.core.blocks.BooleanBlock(required=False)), ('poll', home.blocks.EmbeddedQuestionnaireChooserBlock(page_type=['questionnaires.Poll']))])), ('embedded_survey', wagtail.core.blocks.StructBlock([('direct_display', wagtail.core.blocks.BooleanBlock(required=False)), ('survey', home.blocks.EmbeddedQuestionnaireChooserBlock(page_type=['questionnaires.Survey']))])), ('embedded_quiz', wagtail.core.blocks.StructBlock([('direct_display', wagtail.core.blocks.BooleanBlock(required=False)), ('quiz', home.blocks.EmbeddedQuestionnaireChooserBlock(page_type=['questionnaires.Quiz']))])), ('media', home.blocks.MediaBlock(icon='media')), ('chat_bot', wagtail.core.blocks.StructBlock([('subject', wagtail.core.blocks.CharBlock()), ('button_text', wagtail.core.blocks.CharBlock()), ('trigger_string', wagtail.core.blocks.CharBlock()), ('channel', messaging.blocks.ChatBotChannelChooserBlock())])), ('pwa_button', wagtail.core.blocks.StructBlock([('smartphone_text', wagtail.core.blocks.CharBlock(help_text='This text appears when it is possible for the user to install the app on their phone.')), ('feature_phone_text', wagtail.core.blocks.CharBlock(help_text='This text appears when the user is using a feature phone and thus cannot install the app (the button will be disabled in this case). [Currently not implemented]', required=False)), ('offline_text', wagtail.core.blocks.CharBlock(help_text="This text appears when the user is navigating the site via the offline app and thus it doesn't make sense to install the offline app again (the button will be disabled in this case). [Currently not implemented]", required=False))]))])),
                ('icon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailsvg.svg')),
                ('image_icon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='wagtailimages.image')),
                ('lead_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='wagtailimages.image')),
            ],
            options={
                'verbose_name': 'PWA Page',
                'verbose_name_plural': 'PWA Pages',
            },
            bases=('wagtailcore.page', home.mixins.PageUtilsMixin, models.Model, home.mixins.TitleIconMixin),
        ),
    ]
