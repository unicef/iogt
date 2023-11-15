from django.test import TestCase, override_settings

from matomo.templatetags.matomo_tags import matomo_tag_manager, matomo_tracking_tags


@override_settings(
    MATOMO_TRACKING=True,
    MATOMO_SERVER_URL="https://example.com/",
    MATOMO_SITE_ID=456,
)
class MatomoTrackingTagsTests(TestCase):
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


class MatomoTagManagerTests(TestCase):
    def test_enable_only_when_container_id_and_server_url(self):
        with override_settings(MATOMO_SERVER_URL=None):
            self.assertIsNone(
                matomo_tag_manager(
                    create_context(),
                    container_id="ID",
                ).get("mtm_src")
            )

        with override_settings(MATOMO_SERVER_URL="https://example.com/"):
            self.assertIsNone(
                matomo_tag_manager(
                    create_context(),
                    container_id=None,
                ).get("mtm_src")
            )
            self.assertIsNotNone(
                matomo_tag_manager(
                    create_context(),
                    container_id="ID",
                ).get("mtm_src")
            )

    def test_generate_correct_tag_manager_url(self):
        with override_settings(MATOMO_SERVER_URL="https://example.com/"):
            self.assertEqual(
                matomo_tag_manager(
                    create_context(),
                    container_id="ID",
                ).get("mtm_src"),
                "https://example.com/js/container_ID.js",
            )


class MockRequest:
    def __init__(self):
        self.session = dict()


def create_context():
    return {"request": MockRequest()}
