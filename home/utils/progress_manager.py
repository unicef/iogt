class ProgressManager:

    def __init__(self, request):
        self.request = request

    def _get_read_articles_ids(self):
        if self.request.user.is_anonymous:
            read_article_ids = set(self.request.session.get('read_articles', []))
        else:
            read_article_ids = set(self.request.user.read_articles.values_list('pk', flat=True))

        return read_article_ids

    def _get_progress(self, section):
        read_article_ids = self._get_read_articles_ids()
        section_articles = section.get_descendant_articles()
        section_article_ids = set(section_articles.values_list('pk', flat=True))

        read_section_articles = read_article_ids.intersection(section_article_ids)

        return len(read_section_articles), len(section_article_ids)

    def get_progress(self, section):
        progress_enabled_ancestor = section.get_progress_bar_enabled_ancestor()
        if progress_enabled_ancestor:
            return self._get_progress(progress_enabled_ancestor)

        return None, None

    def is_completed(self, section):
        progress_enabled_ancestor = section.get_progress_bar_enabled_ancestor()
        if progress_enabled_ancestor:
            read_article_count, total_article_count = self._get_progress(section)

            return read_article_count == total_article_count

        return False
