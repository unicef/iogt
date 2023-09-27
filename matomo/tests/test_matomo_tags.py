from django.test import TestCase, override_settings

from matomo.templatetags.matomo_tags import matomo_tracking_tags


@override_settings(
    MATOMO_TRACKING=True,
    MATOMO_SERVER_URL="https://example.com/",
    MATOMO_SITE_ID=456,
)
class MatomoTagsTests(TestCase):
    def test_only_enabled_when_required_settings_are_set(self):
        self.assertTrue(matomo_tracking_tags(dict()).get("tracking_enabled"))

    def test_additional_site_id_must_be_positive_integer(self):
        with override_settings(MATOMO_ADDITIONAL_SITE_ID=567):
            self.assertEqual(
                matomo_tracking_tags(dict()).get("matomo_additional_site_id"),
                567,
            )

        with override_settings(MATOMO_ADDITIONAL_SITE_ID=0):
            self.assertFalse(
                "matomo_additional_site_id" in matomo_tracking_tags(dict())
            )

        with override_settings(MATOMO_ADDITIONAL_SITE_ID=None):
            self.assertFalse(
                "matomo_additional_site_id" in matomo_tracking_tags(dict())
            )

        with override_settings(MATOMO_ADDITIONAL_SITE_ID='123'):
            self.assertFalse(
                "matomo_additional_site_id" in matomo_tracking_tags(dict())
            )
