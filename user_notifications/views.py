# user_notifications/views.py
from notifications.models import Notification
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import NotificationPreference, NotificationTag

@login_required
def latest_notifications(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')[:5]
    return render(request, 'user_notifications/notification_dropdown.html', {'notifications': notifications})

@login_required
def all_notifications(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')
    return render(request, 'user_notifications/notification_list.html', {'notifications': notifications})

@login_required
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, unread=True).update(unread=False)
    return redirect('user_notifications:all')


@login_required
def mark_selected_read(request):
    ids = request.GET.getlist('ids[]')
    if not ids:
        return JsonResponse({'status': 'error', 'message': 'No IDs provided'}, status=400)
    Notification.objects.filter(recipient=request.user, id__in=ids, unread=True).update(unread=False)
    return JsonResponse({'status': 'success', 'message': f'{len(ids)} notifications marked as read'})

@login_required
def toggle_read(request, pk):
    notif = Notification.objects.get(id=pk, recipient=request.user)
    notif.unread = not notif.unread
    notif.save()
    return redirect('user_notifications:all')

@login_required
def unread_count(request):
    count = Notification.objects.filter(recipient=request.user, unread=True).count()
    return JsonResponse({'unread_count': count})


@require_POST
@login_required
def save_notification_preference(request):
    print('request', request)
    if request.method == "POST" and request.user.is_authenticated:
        data = json.loads(request.body)
        print('data', data)
        choice = data.get("choice")  # "yes" or "no"
        language = data.get('language', 'en')
        tag_ids = data.get('tags', [])

        if choice not in [True, False]:
            return JsonResponse({"error": "Invalid choice"}, status=400)

        # receive = (choice == "yes")
        # pref, _ = NotificationPreference.objects.get_or_create(user=request.user)
        # pref.receive_notifications = receive
        # pref.save()
        # choice = 'yes' if choice else 'No'
        print('choice', choice)
        if isinstance(choice, str):
            choice = choice.lower() in ['yes', 'true', '1']
        print('choice-changes', choice)
        preference, created = NotificationPreference.objects.update_or_create(
            user=request.user,
            defaults={
                'receive_notifications': choice,
                'preferred_language': language,
            }
        )

        if tag_ids:
            tags = NotificationTag.objects.filter(id__in=tag_ids)
            preference.content_tags.set(tags)

        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'unauthorized'}, status=403)

