from django.urls import reverse
from wagtail.contrib.modeladmin.helpers import ButtonHelper


class XtdCommentAdminButtonHelper(ButtonHelper):
    def hide_show_toggle_button(self, comment):

        if comment.is_removed:
            action = 'show'
            label = 'Show'
        else:
            action = 'hide'
            label = 'Hide'

        return {
            'url': reverse('wagtail_comments_xtd_publication', kwargs={
                'comment_pk': comment.pk,
                'action': action
            }),
            'label': label,
            'classname': 'button button-small button-secondary',
            'title': f'{label} this {self.verbose_name}'
        }

    def publish_unpublish_toggle_button(self, comment):
        if comment.is_public:
            action = 'unpublish'
            label = 'Unpublish'
            cn = 'button no button-small button-secondary'
        else:
            action = 'publish'
            label = 'Publish'
            cn = 'button button-small button-secondary'
        return {
            'url': reverse('wagtail_comments_xtd_publication', kwargs={
                'comment_pk': comment.pk,
                'action': action
            }),
            'label': label,
            'classname': cn,
            'title': f'{label} this {self.verbose_name}'
        }

    def clear_flags_button(self, comment):
        if comment.flags.count():
            return {
                'url': reverse('wagtail_comments_xtd_publication', kwargs={
                    'comment_pk': comment.pk,
                    'action': 'clear_flags'
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
        if self.request.user.has_perm('comments.can_moderate_on_admin_panel'):
            buttons.append(self.publish_unpublish_toggle_button(comment=obj))
        buttons.append(self.clear_flags_button(comment=obj))
        buttons.append(self.comment_reply_button(comment=obj))
        return buttons
