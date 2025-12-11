from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView
from home.models import Article, ArticleFeedback, FeedbackSettings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
from django.core.paginator import Paginator
from django.conf import settings

from .models import ManifestSettings


class ServiceWorkerView(TemplateView):
    template_name = "sw.js"
    content_type = "application/javascript"
    name = "sw.js"


def get_manifest(request):
    language = translation.get_language() or settings.LANGUAGE_CODE

    qs = ManifestSettings.objects

    # Try: current language → default LANGUAGE_CODE → any row
    manifest = (
        qs.filter(language=language).first()
        or qs.filter(language=settings.LANGUAGE_CODE).first()
        or qs.first()
    )

    if manifest is None:
        # Last-resort minimal manifest so it never 404s
        response = {
            "name": "Internet of Good Things",
            "short_name": "IoGT",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#493174",
            "icons": [
                {
                    "src": "/static/pwa/icons/icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                },
            ],
            "screenshots": [
                {
                    "src": "/static/pwa/screenshots/home-wide.png",
                    "sizes": "1280x720",
                    "type": "image/png",
                    "form_factor": "wide"
                },
                {
                    "src": "/static/pwa/screenshots/home-narrow.png",
                    "sizes": "540x720",
                    "type": "image/png",
                    "form_factor": "narrow"
                }
            ],
        }
        print("1"*40)
    else:
        response = {
            "name": manifest.name,
            "short_name": manifest.short_name,
            "scope": manifest.scope,
            "background_color": manifest.background_color,
            "theme_color": manifest.theme_color,
            "description": manifest.description,
            "lang": manifest.language,
            "start_url": manifest.start_url,
            "display": manifest.display,
            "icons": [
                {
                    "src": "/static/pwa/icons/icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                },
                {
                    "src": manifest.icon_96_96.file.url,
                    "type": f"image/{manifest.icon_96_96.file.name.split('.')[-1]}",
                    "sizes": f"{manifest.icon_96_96.width}x{manifest.icon_96_96.height}",
                },
                {
                    "src": manifest.icon_512_512.file.url,
                    "type": f"image/{manifest.icon_512_512.file.name.split('.')[-1]}",
                    "sizes": f"{manifest.icon_512_512.width}x{manifest.icon_512_512.height}",
                },
                {
                    "src": manifest.icon_192_192.file.url,
                    "type": f"image/{manifest.icon_192_192.file.name.split('.')[-1]}",
                    "sizes": f"{manifest.icon_192_192.width}x{manifest.icon_192_192.height}",
                    "purpose": "any maskable",
                },
            ],
            "screenshots": [
                {
                    "src": "/static/pwa/screenshots/home-wide.png",
                    "sizes": "1280x720",
                    "type": "image/png",
                    "form_factor": "wide"
                },
                {
                    "src": "/static/pwa/screenshots/home-narrow.png",
                    "sizes": "540x720",
                    "type": "image/png",
                    "form_factor": "narrow"
                }
            ],
        }
        print("2"*40)

    http_response = JsonResponse(
        response,
        content_type="application/manifest+json",
    )
    http_response["Cache-Control"] = "max-age=600, public"

    return http_response


class LogoutRedirectHackView(View):
    def get(self, request):
        return redirect(f'/{request.LANGUAGE_CODE}/')


@csrf_exempt
def submit_feedback(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    # Get feedback settings
    feedback_settings = FeedbackSettings.for_request(request)
    if not feedback_settings.enable_feedback:
        return JsonResponse({"error": "Feedback is disabled globally."}, status=403)

    if request.user.is_authenticated:
        if ArticleFeedback.objects.filter(article=article, user=request.user).exists():
            return JsonResponse({"error": "You have already submitted feedback."}, status=400)

        feedback = ArticleFeedback.objects.create(
            article=article,
            user=request.user,
            rating=int(request.POST.get('rating')),
            feedback=request.POST.get('feedback', '')
        )
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key

        if ArticleFeedback.objects.filter(article=article, session_id=session_id).exists():
            return JsonResponse({"error": "You have already submitted feedback in this session."}, status=400)

        feedback = ArticleFeedback.objects.create(
            article=article,
            session_id=session_id,
            rating=int(request.POST.get('rating')),
            feedback=request.POST.get('feedback', '')
        )

    return JsonResponse({"message": "Feedback submitted successfully!"})

def AdminArticleFeedbackView(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    feedbacks = ArticleFeedback.objects.filter(article=article)

    return render(request, "home/article_feedback_list.html", {"article": article, "feedbacks": feedbacks})


def load_more_reviews(request, article_id):
    article = Article.objects.get(id=article_id)
    page = int(request.GET.get("page", 1))  # Get current page from AJAX
    feedbacks = article.feedbacks.order_by('-created_at')  # All feedbacks
    
    paginator = Paginator(feedbacks, 3)  # Show 5 per page

    if page > paginator.num_pages:
        return JsonResponse({"reviews": [], "has_more": False})

    feedback_page = paginator.get_page(page)
    reviews_data = [
        {
            "rating": feedback.rating,
            "feedback": feedback.feedback,
            "user": feedback.user.username if feedback.user else "Anonymous",
            "created_at": feedback.created_at.strftime("%B %d, %Y at %I:%M %p"),
        }
        for feedback in feedback_page
    ]

    return JsonResponse({"reviews": reviews_data, "has_more": feedback_page.has_next()})
