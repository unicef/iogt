from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super(AccountAdapter, self).save_user(request, user, form, commit)
        data = form.cleaned_data
        user.moyapay_username = data.get('moyapay_username')
        user.display_name = data.get('display_name') or data.get('username')
        user.first_name = data.get('first_name')
        user.last_name = data.get('last_name')
        user.terms_accepted = data.get('terms_accepted', False)
        user.save(update_fields=['display_name', 'first_name', 'last_name', 'terms_accepted', 'moyapay_username'])
        return user
