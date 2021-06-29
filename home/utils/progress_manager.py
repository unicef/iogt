class ProgressManager:

    def __init__(self, request):
        self.request = request

    def get_progress(self, section):
        user = self.request.user
        if self.request.user.is_anonymous:
            read_article_ids = set(self.request.session.get('read_articles', []))
        else:
            read_article_ids = set(user.read_articles.values_list('pk', flat=True))

        progress_enabled_ancestor = section.get_progress_bar_enabled_ancestor()
        if progress_enabled_ancestor:
            section_articles = progress_enabled_ancestor.get_descendant_articles()
            section_article_ids = set(section_articles.values_list('pk', flat=True))

            read_section_articles = read_article_ids.intersection(section_article_ids)

            return len(read_section_articles), len(section_article_ids)
        return None, None
