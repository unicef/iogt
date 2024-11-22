from http.client import HTTPResponse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import UpdateView, TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.contrib.auth import get_user_model
from django.http import JsonResponse

from iogt import settings

from email_service.mailjet_email_sender import send_email_via_mailjet


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

        # If no errors, proceed with sending the invitation email
        # Assume `User` is your user model and email is unique
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'first_name': first_name, 'last_name': last_name},
            username=email
        )

        template_name = "email_service/invite_admin.html"  # Your template name
        invitation_link = request.build_absolute_uri('/admin/login/')

        context = {
            'first_name': first_name,
            'invitation_link': invitation_link,  # Example link
        }

        from django.conf import settings

        try:
            send_email_via_mailjet(api_key=settings.MAILJET_API_KEY,
                               api_secret=settings.MAILJET_API_SECRET,
                               from_email=settings.MAILJET_FROM_EMAIL,
                               from_name=settings.MAILJET_FROM_NAME,
                               to_email=email,
                               to_name=first_name,
                               subject='Invitation to join IOGT as an admin',
                               template_name=template_name,
                               context=context,
                               )
        except Exception as e:
            # Handle any email sending errors
            return JsonResponse({'success': False, 'message': 'Failed to send invitation.', 'error': str(e)},
                                status=500)

            # If email is sent successfully
        return JsonResponse({'success': True, 'message': 'Invitation sent successfully!'})