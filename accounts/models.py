import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.http import HttpResponseRedirect

from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    HelpPanel,
    InlinePanel,
    ObjectList,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.contrib.forms.models import (
    FORM_FIELD_CHOICES,
    AbstractForm,
    AbstractFormField,
    AbstractFormSubmission,
)
from wagtail.core.blocks import RichTextBlock
from wagtail.core.fields import StreamField
from wagtail.core.models import Page


class User(AbstractUser):
    additional_data = models.JSONField(blank=True, null=True)

    def get_additional_data(self):
        return json.loads(self.additional_data)



class UserRegistrationPage(AbstractForm):


    thank_you_text = StreamField([
        ('paragraph', RichTextBlock(required=True))
    ])


    # Only allow one User Registration page to be created
    max_count = 1

    parent_page_types = ['home.HomePage']

    from .forms import RegistrationFormBuilder  # noqa prevent circular imports
    form_builder = RegistrationFormBuilder

    form_panels = [
        HelpPanel(
            content=(
                """
                <b>You can add additional fields for the user registration form by default form display
                the following fields:</b>
                <p>* Name</p>
                <p>* Username</p>
                <p>* Password</p>
                <p>* Confirm password</p>
                """
            ),
        ),
        InlinePanel("form_fields", label="Form Fields")
    ]
    content_panels = Page.content_panels + [
        StreamFieldPanel('thank_you_text'),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Page Content"),
            ObjectList(form_panels, heading="Additional registration fields"),
            ObjectList(Page.promote_panels, heading="Promote"),
            ObjectList(
                Page.settings_panels,
                heading="Settings",
                classname="settings",
            )
        ],
    )
    def process_form_submission(self, form):
        """
        Save the user
        """
        form.save(commit=False)



class FormField(AbstractFormField):
    page = ParentalKey(UserRegistrationPage, on_delete=models.CASCADE, related_name="form_fields")
