from django.urls import reverse
from wagtail.contrib.modeladmin.helpers import ButtonHelper


class XtdCommentAdminButtonHelper(ButtonHelper):
    def publish_unpublish_toggle_button(self, comment):
        if comment.is_public:
            action = 'unpublish_comment'
            label = 'Unpublish'
            cn = 'button no button-small button-secondary'
        else:
            action = 'publish_comment'
            label = 'Publish'
            cn = 'button button-small button-secondary'
        return {
            'url': reverse(action, kwargs={
                'comment_pk': comment.pk,
            }),
            'label': label,
            'classname': cn,
            'title': f'{label} this {self.verbose_name}'
        }

    def clear_flags_button(self, comment):
        if comment.flags.count():
            return {
                'url': reverse('clear_flags', kwargs={
                    'comment_pk': comment.pk,
                }),
                'label': 'Clear Flags',
                'classname': 'button button-small button-secondary',
                'title': f'Clear flags for {self.verbose_name}'
            }

    def comment_reply_button(self, comment):
        return {
            'url': reverse('comment_reply_view', kwargs={
                'comment_pk': comment.pk
            }),
            'label': 'Reply',
            'classname': 'button button-small button-secondary',
            'title': f'Add Reply for {self.verbose_name}'
        }

    def get_buttons_for_obj(self, obj, *args, **kwargs):
        buttons = super().get_buttons_for_obj(obj, exclude='delete', *args, **kwargs)
        if self.request.user.has_perm('django_comments_xtd.can_moderate_on_admin_panel'):
            buttons.append(self.publish_unpublish_toggle_button(comment=obj))
            buttons.append(self.clear_flags_button(comment=obj))
            buttons.append(self.comment_reply_button(comment=obj))
        return buttons
