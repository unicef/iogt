from django.apps import apps
from django.contrib.admin.utils import flatten


def get_progress_bar_eligible_sections():
    """
    Eligibility criteria:
    Sections whose ancestors don't have show_progress_bar=True are eligible to
    show progress bars.
    :return:e
    """
    Section = apps.get_model('home', 'Section')
    progress_bar_sections = Section.objects.filter(show_progress_bar=True)
    all_descendants = [list(Section.objects.type(Section).descendant_of(section).values_list('pk', flat=True)) for
                       section in
                       progress_bar_sections]
    all_descendants = set(flatten(all_descendants))

    return Section.objects.exclude(pk__in=all_descendants)
