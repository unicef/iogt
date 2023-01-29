

class DisplayViewLiveOnAdminMixin:
    """Using this class you will be able to restrict the visibility of view live and preview button."""
    def should_display_view_live_on_admin(self):
        return False
