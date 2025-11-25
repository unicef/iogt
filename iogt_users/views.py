import logging
import os, shutil
from http.client import HTTPResponse

from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Max, Avg
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import UpdateView, TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from wagtail.models import Locale, Page
from django.utils import timezone
from django.contrib.auth import logout
from django import forms
from .models import DeletedUserLog, PageVisit, QuizAttempt
from wagtail.documents import get_document_model
from wagtail.images import get_image_model
from wagtailmedia.models import Media
from iogt import settings

from email_service.mailjet_email_sender import send_email_via_mailjet
from user_notifications.models import NotificationPreference, NotificationTag

logger = logging.getLogger(__name__)
User = get_user_model()

class UserNotificationView(TemplateView):
    template_name = 'user_notification.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            notification_pref = NotificationPreference.objects.filter(user=self.request.user).first()
            context['notification_preference'] = notification_pref
            context['selected_tag_ids'] = list(
                notification_pref.content_tags.values_list('id', flat=True)
            ) if notification_pref else []
            context['selected_language_code'] = (
                notification_pref.preferred_language
                if notification_pref and notification_pref.preferred_language else 'en')
        else:
            context['notification_preference'] = None
        context['notification_tags'] = NotificationTag.objects.all()
        context['available_languages'] = Locale.objects.all()
        context['user'] = self.request.user
        return context


@method_decorator(login_required, name='dispatch')
class UserDetailView(TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        return {'user': self.request.user}
    

@method_decorator(login_required, name='dispatch')
class UserDetailEditView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'username', 'date_of_birth', 'gender','location' )
    template_name = 'profile_edit.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date_of_birth'].widget = forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
        return form
    
    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            if form.has_changed():
                return JsonResponse({"success": True, "message": "✅ Profile updated successfully!"})
            else:
                return JsonResponse({"success": False, "message": "ℹ️ No changes made."})
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "success": False,
                "message": "❌ Invalid data submitted.",
                "errors": form.errors
            }, status=400)

        return super().form_invalid(form)

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
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True,
                    'is_superuser': True
                },
            )

            if not created:
                user.is_active = True
                user.is_superuser = True
                user.save()

        except Exception as e:
            # Handle any email sending errors
            return JsonResponse({'success': False, 'message': 'Failed to send invitation.', 'error': str(e)},
                                status=500)

            # If email is sent successfully

        return JsonResponse({'success': True, 'message': 'Invitation sent successfully!'})
    
@method_decorator(login_required, name='dispatch')
class MyActivityView(TemplateView):
    template_name = "my_activity.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        visits = PageVisit.objects.filter(user=user)
        context.update({
            "pages_visited": visits.count(),
            "unique_pages": visits.values("page_slug").distinct().count(),
            "visits": visits.count(),
            "last_visit": visits.first().timestamp if visits.exists() else None,
            "date_joined": user.date_joined,
            "last_login": user.last_login,
        })
        return context


@method_decorator(login_required, name='dispatch')
class DeleteAccountView(View):
    """Handles full account deletion including all related Wagtail data."""

    def post(self, request, *args, **kwargs):
        """Handle confirmed deletion."""
        from django.conf import settings
        try:
            user = request.user
            logger.info(
                f"User deletion requested by user_id={user.id}, email={user.email}, at {timezone.now()}"
            )
            from iogt_users.models import DeletedUserLog  # adjust import to your actual model path
            DeletedUserLog.objects.create(
                user_id=user.id,
                reason="User requested account deletion"
            )
            self.delete_user_data(user)
            logout(request)
            user.delete()
            return JsonResponse({"success": True})
        except Exception as e:
            logger.error(f"Error deleting account for user_id={user.id}: {e}", exc_info=True)
            return JsonResponse({"success": False}, status=500)

    def delete_user_data(self, user):
        """Delete all Wagtail-related and media data for a user."""
        Page.objects.filter(owner=user).delete()
        Document = get_document_model()
        Image = get_image_model()
        Document.objects.filter(uploaded_by_user=user).delete()
        Image.objects.filter(uploaded_by_user=user).delete()
        Media.objects.filter(uploaded_by_user=user).delete()
        for model in apps.get_models():
            for field in model._meta.get_fields():
                if field.is_relation and field.remote_field and field.remote_field.model == User:
                    model.objects.filter(**{field.name: user}).delete()

        from django.conf import settings
        user_media_dir = os.path.join(settings.MEDIA_ROOT, f"users/{user.id}")
        if os.path.exists(user_media_dir):
            shutil.rmtree(user_media_dir, ignore_errors=True)
        for folder in ["images", "documents", "svg"]:
            path = os.path.join(settings.MEDIA_ROOT, folder, str(user.id))
            if os.path.exists(path):
                shutil.rmtree(path, ignore_errors=True)

@method_decorator(login_required, name='dispatch')
class QuizResultView(TemplateView):
    template_name = 'quiz_result.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        latest_attempts = (
            QuizAttempt.objects.filter(user=user)
            .values('quiz')
            .annotate(latest_attempt=Max('completed_at'))
        )
        quiz_results = QuizAttempt.objects.filter(
            user=user,
            completed_at__in=[item['latest_attempt'] for item in latest_attempts]
        ).select_related('quiz')
        avg_scores = (
            QuizAttempt.objects.filter(user=user)
            .values('quiz')
            .annotate(avg_score=Avg('score'))
        )
        avg_score_map = {item['quiz']: item['avg_score'] for item in avg_scores}
        for attempt in quiz_results:
            attempt.avg_score = avg_score_map.get(attempt.quiz.id, 0)
        context['quiz_results'] = quiz_results
        return context