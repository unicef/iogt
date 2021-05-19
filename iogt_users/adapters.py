from allauth.account.adapter import DefaultAccountAdapter


class IogtAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super(IogtAccountAdapter, self).save_user(request, user, form, commit)
        data = form.cleaned_data
        user.display_name = data.get('display_name')
        user.has_accepted_terms_and_conditions = data.get('has_accepted_terms_and_conditions', False)
        user.save(update_fields=['display_name', 'has_accepted_terms_and_conditions'])
        return user
