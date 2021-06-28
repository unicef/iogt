from wagtail.users.forms import standard_fields


def has_completed_registration_survey(user):
    # TODO: Check if survey exists when surveys go live. This method should always return
    #  True if there is no post-registration survey
    return user.has_filled_registration_survey


def get_wagtail_admin_user_standard_fields():
    """
    Gets the standard_fields from wagtail.users.forms and removes unused fields.This method is made for a very specific
     case in the WagtailAdminUserCreateForm and WagtailAdminUserEditForm.
    Warning: Do not modify it unless you are sure
    :return:
    """
    return standard_fields - set(['first_name', 'last_name'])
