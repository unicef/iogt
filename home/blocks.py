from django.forms.utils import flatatt
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext as _

from wagtail.core import blocks
from wagtail.core.blocks import PageChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailmarkdown.utils import render_markdown
from wagtailmedia.blocks import AbstractMediaChooserBlock


class MediaBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        if not value:
            return ''

        video_not_supported_text = _("Your browser does not support video playback.")
        audio_not_supported_text = _("Your browser does not support audio playback.")
        # Translators: Translators: This message appears below embedded video and audio on the site. Many feature phones won't be able to play embedded video/audio, so the site offers an opportunity to download the file. Part of this message (between %(start_link)s and %(end_link)s ) is a clickable download link.
        download_video_text = _('If you cannot view the above video, you can'
                ' instead %(start_link)sdownload it%(end_link)s.') % {
                        'start_link': '<a href={2} download>',
                        'end_link': '</a>'
                }
        # Translators: Translators: This message appears below embedded video and audio on the site. Many feature phones won't be able to play embedded video/audio, so the site offers an opportunity to download the file. Part of this message (between %(start_link)s and %(end_link)s ) is a clickable download link.
        download_audio_text = _('If you cannot listen to the above audio, you can'
                ' instead %(start_link)sdownload it%(end_link)s.') % {
                        'start_link': '<a href={2} download>',
                        'end_link': '</a>'
                }

        if value.type == 'video':
            player_code = '''
            <div>
                <video preload="none" width="320" height="240" {1} controls>
                    {0}
                    ''' + video_not_supported_text + '''
                </video>
            </div>
            <p class='article__content--video'>''' + download_video_text + '''</p>
            '''
        else:
            player_code = '''
            <div>
                <audio preload="none" controls>
                    {0}
                    ''' + audio_not_supported_text + '''
                </audio>
            </div>
            <p class='article__content--audio'>''' + download_audio_text + '''</p>
            '''

        thumbnail = f'poster={value.thumbnail.url}' if value.thumbnail else ''

        return format_html(player_code, format_html_join(
            '\n', "<source{0}>",
            [[flatatt(s)] for s in value.sources]
        ), thumbnail, value.url)


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


class OfflineAppButtonBlock(blocks.StructBlock):
    smartphone_text = blocks.CharBlock(
        help_text=_('This text appears when it is possible for the user to install the app on their phone.'))
    feature_phone_text = blocks.CharBlock(required=False,
        help_text=_('This text appears when the user is using a feature phone and thus cannot install the app '
                    '(the button will be disabled in this case). [Currently not implemented]'))
    offline_text = blocks.CharBlock(required=False,
        help_text=_('This text appears when the user is navigating the site via the offline app and '
                    'thus it doesn\'t make sense to install the offline app again '
                    '(the button will be disabled in this case). [Currently not implemented]'))

    class Meta:
        template = 'blocks/offline_app_button.html'
