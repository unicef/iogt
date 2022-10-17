class Dashboard:
    def __init__(self, dashboard_title):
        self.dashboard_title = dashboard_title

    def post_body(self):
        return {
            'dashboard_title': self.dashboard_title,
            'published': True,
        }
