from django.views.generic import TemplateView


class ExternalLink(TemplateView):
    template_name = "external-link.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["next"] = self.request.GET.get("next", "/")
        context["prev"] = self.request.META.get("HTTP_REFERER", "/")
        return context
