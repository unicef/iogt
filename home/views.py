

def render_live_articles(articles):
    live_articles = articles.filter(live=True)
    return live_articles
