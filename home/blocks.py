import random

from django.conf import settings
from django.forms.utils import flatatt
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from wagtail.core import blocks
from wagtail.core.blocks import PageChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailmarkdown.utils import render_markdown
from wagtailmedia.blocks import AbstractMediaChooserBlock


class MediaBlock(AbstractMediaChooserBlock):
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        context.update({
            'start_link': mark_safe(f'<a href="{value.url}" download>'),
            'end_link': mark_safe('</a>'),
            'template': 'blocks/media-video.html' if value.type == 'video' else 'blocks/media-audio.html'
        })

        return context

    class Meta:
        template = 'blocks/media.html'


class SocialMediaLinkBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255)
    link = blocks.URLBlock()
    image = ImageChooserBlock(template='blocks/image.html')

    class Meta:
        icon = 'site'


class SocialMediaShareButtonBlock(blocks.StructBlock):
    platform = blocks.CharBlock(max_length=255)
    is_active = blocks.BooleanBlock(required=False)
    image = ImageChooserBlock(template='blocks/image.html', required=False)

    class Meta:
        icon = 'site'


class EmbeddedQuestionnaireChooserBlock(blocks.PageChooserBlock):
    class Meta:
        icon = 'form'


class EmbeddedQuestionnaireBlock(blocks.StructBlock):
    direct_display = blocks.BooleanBlock(required=False)


class EmbeddedPollBlock(EmbeddedQuestionnaireBlock):
    poll = EmbeddedQuestionnaireChooserBlock(target_model='questionnaires.Poll')

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        poll = value.get('poll')
        if poll and poll.live:
            context.update({
                'direct_display': value['direct_display'],
                'questionnaire': poll.specific,
            })
        return context

    class Meta:
        template = 'questionnaires/tags/questionnaire_wrapper.html'


class EmbeddedSurveyBlock(EmbeddedQuestionnaireBlock):
    survey = EmbeddedQuestionnaireChooserBlock(target_model='questionnaires.Survey')

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        survey = value.get('survey')
        if survey and survey.live:
            context.update({
                'direct_display': value['direct_display'],
                'questionnaire': survey.specific,
            })
        return context

    class Meta:
        template = 'questionnaires/tags/questionnaire_wrapper.html'


class EmbeddedQuizBlock(EmbeddedQuestionnaireBlock):
    quiz = EmbeddedQuestionnaireChooserBlock(target_model='questionnaires.Quiz')

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        quiz = value.get('quiz')
        if quiz and quiz.live:
            context.update({
                'direct_display': value['direct_display'],
                'questionnaire': quiz.specific,
            })
        return context

    class Meta:
        template = 'questionnaires/tags/questionnaire_wrapper.html'


class PageButtonBlock(blocks.StructBlock):
    page = blocks.PageChooserBlock()
    text = blocks.CharBlock(required=False, max_length=255)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        button_page = value.get('page')
        if button_page and button_page.live:
            context.update({
                'button_page': button_page.specific,
                'text': value.get('text') or button_page.title
            })
        return context

    class Meta:
        template = 'blocks/page_button.html'


class ArticleBlock(blocks.StructBlock):
    display_section_title = blocks.BooleanBlock(required=False)
    article = PageChooserBlock(target_model='home.Article')

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        article = value.get('article')
        if article and article.live:
            context.update({
                'display_section_title': value['display_section_title'],
                'article': article.specific,
            })
        return context

    class Meta:
        template = 'blocks/article.html'


class NumberedListBlock(blocks.ListBlock):

    def render_basic(self, value, context=None):
        children = format_html_join(
            '\n', '<li>{0}</li>',
            [
                (self.child_block.render(child_value, context=context),)
                for child_value in value
            ]
        )
        return format_html("<ol>{0}</ol>", children)


class RawHTMLBlock(blocks.RawHTMLBlock):
    def render_basic(self, value, context=None):
        result = super(RawHTMLBlock, self).render_basic(value, context)

        return render_markdown(result)


class DownloadButtonBlock(blocks.StructBlock):
    available_text = blocks.CharBlock(
        help_text=_('This text appears when it is possible for the user to install the app on their phone.'))
    unavailable_text = blocks.CharBlock(
        required=False,
        help_text=_(
            'This text appears when the user is using a feature phone and thus cannot install the app '
            '(the button will be disabled in this case). [Currently not implemented]'),
        form_classname='red-help-text')
    offline_text = blocks.CharBlock(
        required=False, help_text=_(
            'This text appears when the user is navigating the site via the offline app and '
            'thus it doesn\'t make sense to install the offline app again '
            '(the button will be disabled in this case).'))
    page = PageChooserBlock(target_model='wagtailcore.Page')
    description = blocks.RichTextBlock(features=settings.WAGTAIL_RICH_TEXT_FIELD_FEATURES)

    class Meta:
        template = 'blocks/download_button.html'


class RandomPageButtonBlock(blocks.StructBlock):
    pages = blocks.StreamBlock(
        [("page", blocks.PageChooserBlock())]
    )
    text = blocks.CharBlock(required=False, max_length=255)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        live_pages = [page.value for page in value.get('pages') if page.value.live]
        if live_pages:
            button_page = random.choice(live_pages)
            context.update({
                'button_page': button_page.specific,
                'text': value.get('text') or button_page.title
            })

        return context

    class Meta:
        template = 'blocks/page_button.html'
