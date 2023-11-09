from django.test import TestCase, override_settings

from matomo.templatetags.matomo_tags import matomo_tracking_tags


@override_settings(
    MATOMO_TRACKING=True,
    MATOMO_SERVER_URL="https://example.com/",
    MATOMO_SITE_ID=456,
)
class MatomoTagsTests(TestCase):
    def test_only_enabled_when_required_settings_are_set(self):
        self.assertTrue(matomo_tracking_tags(create_context()).get("tracking_enabled"))

    def test_additional_site_id_must_be_positive_integer(self):
        with override_settings(MATOMO_ADDITIONAL_SITE_ID=567):
            context = matomo_tracking_tags(create_context())
            self.assertEqual(context.get("matomo_additional_site_id"), 567)
            self.assertEqual(
                context.get("matomo_additional_image_tracker_url"),
                "https://example.com/matomo.php?idsite=567&rec=1",
            )

        with override_settings(MATOMO_ADDITIONAL_SITE_ID=0):
            context = matomo_tracking_tags(create_context())
            self.assertFalse("matomo_additional_site_id" in context)
            self.assertFalse("matomo_additional_image_tracker_url" in context)

        with override_settings(MATOMO_ADDITIONAL_SITE_ID=None):
            context = matomo_tracking_tags(create_context())
            self.assertFalse("matomo_additional_site_id" in context)
            self.assertFalse("matomo_additional_image_tracker_url" in context)

        with override_settings(MATOMO_ADDITIONAL_SITE_ID="123"):
            context = matomo_tracking_tags(create_context())
            self.assertFalse("matomo_additional_site_id" in context)
            self.assertFalse("matomo_additional_image_tracker_url" in context)

    def test_visitor_id_is_created_for_clients_without_javascript(self):
        with override_settings(MATOMO_CREATE_VISITOR_ID=True):
            self.assertRegexpMatches(
                matomo_tracking_tags(create_context()).get("matomo_image_tracker_url"),
                r"_id=[a-f0-9]{16}",
            )


class MockRequest:
    def __init__(self):
        self.session = dict()


def create_context():
    return {"request": MockRequest()}
