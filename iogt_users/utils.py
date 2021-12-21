from wagtail.users.forms import standard_fields


def has_completed_registration_survey(user):
    # TODO: Check if survey exists when surveys go live. This method should always return
    #  True if there is no post-registration survey
    return user.has_filled_registration_survey
-
