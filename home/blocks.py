from django.db.models import Q
from django.forms.utils import flatatt
from django.template.loader import render_to_string
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext as _

from wagtail.core import blocks
from wagtail.core.blocks import PageChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailmarkdown.utils import render_markdown
from wagtailmedia.blocks import AbstractMediaChooserBlock

from questionnaires.utils import SkipLogicPaginator


class MediaBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        if not value:
            return ''

        video_not_supported_text = _("Your browser does not support the video tag.")
        audio_not_supported_text = _("Your browser does not support the audio element.")
        # Translators: Part of this message (between %(start_link)s and %(end_link)s ) is a clickable download link
        download_video_text = _('If you cannot view the above video, perhaps would'
                ' you like to %(start_link)s download it? %(end_link)s.') % {
                        'start_link': '<a href={1} download>',
                        'end_link': '</a>'
                }
        # Translators: Part of this message (between %(start_link)s and %(end_link)s ) is a clickable download link
        download_audio_text = _('If you cannot listen to the above audio, perhaps would'
                ' you like to %(start_link)s download it? %(end_link)s.') % {
                        'start_link': '<a href={1} download>', 
                        'end_link': '</a>'
                }

        if value.type == 'video':
            player_code = '''
            <div>
                <video width="320" height="240" controls>
                    {0}
                    ''' + video_not_supported_text + '''
                </video>
            </div>
            <p class='article__content--video'>''' + download_video_text + '''</p>
            '''
        else:
            player_code = '''
            <div>
                <audio controls>
                    {0}
                    ''' + audio_not_supported_text + '''
                </audio>
            </div>
            <p class='article__content--audio'>''' + download_audio_text + '''</p>
            '''

        return format_html(player_code, format_html_join(
            '\n', "<source{0}>",
            [[flatatt(s)] for s in value.sources]
        ), value.url)


class SocialMediaLinkBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255)
    link = blocks.URLBlock()
    image = ImageChooserBlock()

    class Meta:
        icon = 'site'


class SocialMediaShareButtonBlock(blocks.StructBlock):
    platform = blocks.CharBlock(max_length=255)
    is_active = blocks.BooleanBlock(required=False)
    image = ImageChooserBlock(required=False)

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
        context.update({
            'direct_display': value['direct_display'],
            'page': value['poll'].specific,
        })
        return context

    class Meta:
        template = 'questionnaires/tags/questionnaire_wrapper.html'


class EmbeddedSurveyBlock(EmbeddedQuestionnaireBlock):
    survey = EmbeddedQuestionnaireChooserBlock(target_model='questionnaires.Survey')

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        context.update({
            'direct_display': value['direct_display'],
            'page': value['survey'].specific,
        })
        return context

    class Meta:
        template = 'questionnaires/tags/questionnaire_wrapper.html'


class EmbeddedQuizBlock(EmbeddedQuestionnaireBlock):
    quiz = EmbeddedQuestionnaireChooserBlock(target_model='questionnaires.Quiz')

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        context.update({
            'direct_display': value['direct_display'],
            'page': value['quiz'].specific,
        })
        return context

    class Meta:
        template = 'questionnaires/tags/questionnaire_wrapper.html'


class PageButtonBlock(blocks.StructBlock):
    page = blocks.PageChooserBlock()
    text = blocks.CharBlock(required=False, max_length=255)

    class Meta:
        template = 'blocks/page_button.html'


class ArticleBlock(blocks.StructBlock):
    display_section_title = blocks.BooleanBlock(required=False)
    article = PageChooserBlock(target_model='home.Article')

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        context.update({
            'display_section_title': value['display_section_title'],
            'page': value['article'].specific,
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
