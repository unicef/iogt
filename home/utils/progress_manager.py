class ProgressManager:

    def record_article_read(self, request, article):
        if request.user.is_anonymous:
            read_articles = request.session.get('read_articles', [])
            if read_articles:
                if article.pk not in read_articles:
                    # https://code.djangoproject.com/wiki/NewbieMistakes#Appendingtoalistinsessiondoesntwork
                    read_articles = request.session['read_articles']
                    read_articles.append(article.pk)
                    request.session['read_articles'] = read_articles
            else:
                request.session['read_articles'] = [article.pk]
        else:
            raise NotImplementedError

    def get_progress(self, request, section):
        if request.user.is_anonymous:
            read_article_ids = set(request.session.get('read_articles', []))
        else:
            raise NotImplementedError

        progress_enabled_ancestor = section.get_progress_bar_enabled_ancestor()
        if progress_enabled_ancestor:
            section_articles = progress_enabled_ancestor.get_descendant_articles()
            section_article_ids = set(section_articles.values_list('pk', flat=True))

            read_section_articles = read_article_ids.intersection(section_article_ids)

            return len(read_section_articles), len(section_article_ids)
        return None, None
