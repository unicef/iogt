from django.db.models import Q
from django.forms.utils import flatatt
from django.template.loader import render_to_string
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext as _

from wagtail.core import blocks
from wagtail.core.blocks import PageChooserBlock
from wagtail.images.blocks import ImageChooserBlock
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

    def render_basic(self, value, context=None):
        from questionnaires.models import Poll

        context.update({
            'page': value,
        })

        request = context['request']
        if request.session.session_key is None:
            request.session.save()
        self.session = request.session

        form_class = value.get_form_class()

        if isinstance(value, Poll):
            template = 'blocks/embedded_poll.html'
        else:
            template = 'blocks/embedded_questionnaire.html'
            paginator = SkipLogicPaginator(value.get_form_fields(), {}, {})
            step = paginator.page(1)
            if hasattr(value, 'multi_step') and value.multi_step:
                form_class = value.get_form_class_for_step(step)
            context.update({
                'fields_step': step,
            })

        multiple_submission_filter = (
            Q(session_key=request.session.session_key) if request.user.is_anonymous else Q(user__pk=request.user.pk)
        )
        multiple_submission_check = (
            not value.allow_multiple_submissions
            and value.get_submission_class().objects.filter(multiple_submission_filter, page=value).exists()
        )
        anonymous_user_submission_check = request.user.is_anonymous and not value.allow_anonymous_submissions
        if multiple_submission_check or anonymous_user_submission_check:
            return render_to_string(template, context)

        form = form_class(page=value, user=request.user)

        context.update({
            'form': form,
        })
        return render_to_string(template, context)

    class Meta:
        icon = 'form'


class PageButtonBlock(blocks.StructBlock):
    page = blocks.PageChooserBlock()
    text = blocks.CharBlock(required=False, max_length=255)

    class Meta:
        template = 'blocks/page_button.html'


class ArticleChooserBlock(PageChooserBlock):
    def __init__(self, *args, **kwargs):
        super().__init__(target_model='home.Article', *args, **kwargs)

    class Meta:
        template = 'blocks/article_page.html'
