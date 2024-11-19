from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.contrib.auth import get_user_model


@method_decorator(login_required, name='dispatch')
class UserDetailView(TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        return {'user': self.request.user}


@method_decorator(login_required, name='dispatch')
class UserDetailEditView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email')
    template_name = 'profile_edit.html'

    def get_success_url(self):
        return reverse('user_profile_edit')

    def get_object(self, queryset=None):
        return self.request.user


@method_decorator(csrf_exempt, name='dispatch')  # To allow AJAX requests without CSRF token
@method_decorator(login_required, name='dispatch')
class InviteAdminUserView(View):
    def post(self, request, *args, **kwargs):
        # Retrieve form data
        User = get_user_model()

        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()

        errors = {}

        # Validate form fields
        if not first_name:
            errors['first_name'] = "First Name is required."

        if not last_name:
            errors['last_name'] = "Last Name is required."

        if not email:
            errors['email'] = "Email is required."
        else:
            # Basic email format validation
            if '@' not in email or '.' not in email.split('@')[-1]:
                errors['email'] = "Please enter a valid email address."

        # If there are errors, return them as JSON
        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        from django.core.mail import send_mail

        # If no errors, proceed with sending the invitation email
        # Assume `User` is your user model and email is unique
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'first_name': first_name, 'last_name': last_name},
            username=email
        )

        from django.conf import settings
        subject = "You are Invited as Admin"
        message = 'hiiiii'
        from_email = settings.DEFAULT_FROM_EMAIL

        try:
            send_mail(subject, message, from_email, [email])
            return
        # Return a success response
        except Exception as e:
            print(e, "))))))))))))))")
            return
