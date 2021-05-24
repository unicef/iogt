from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super(AccountAdapter, self).save_user(request, user, form, commit)
        data = form.cleaned_data
        user.display_name = data.get('display_name')
        user.terms_accepted = data.get('terms_accepted', False)
        user.save(update_fields=['display_name', 'terms_accepted'])
        return user
