class ProgressManager:

    def __init__(self, request):
        self.request = request

    def record_article_read(self, article):
        user = self.request.user
        if user.is_anonymous:
            read_articles = self.request.session.get('read_articles', [])
            if read_articles:
                if article.pk not in read_articles:
                    # https://code.djangoproject.com/wiki/NewbieMistakes#Appendingtoalistinsessiondoesntwork
                    read_articles = self.request.session['read_articles']
                    read_articles.append(article.pk)
                    self.request.session['read_articles'] = read_articles
            else:
                self.request.session['read_articles'] = [article.pk]
        else:
            if not user.viewed_articles.filter(id=article.id).exists():
                user.viewed_articles.add(article)


    def get_progress(self, section):
        user = self.request.user
        if self.request.user.is_anonymous:
            read_article_ids = set(self.request.session.get('read_articles', []))
        else:
            read_article_ids = set(user.viewed_articles.values_list('pk', flat=True))

        progress_enabled_ancestor = section.get_progress_bar_enabled_ancestor()
        if progress_enabled_ancestor:
            section_articles = progress_enabled_ancestor.get_descendant_articles()
            section_article_ids = set(section_articles.values_list('pk', flat=True))

            read_section_articles = read_article_ids.intersection(section_article_ids)

            return len(read_section_articles), len(section_article_ids)
        return None, None
