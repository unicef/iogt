---
title: Question Types
permalink: /cms-manual/surveys/question-types/
---

There are various types of survey questions you can use depending on your needs:

- Single-line text - for short free-form responses
- Multi-line text - for longer free-form responses
- Email - email values only
- Number - numerical values only
- URL - a URL to another webpage
- Checkbox - a single checkbox, can be unselected
- Checkboxes - multiple checkboxes, can be unselected
- Dropdown - choose one option from a list of options
- Multiple Select - choose multiple options from a list of options
- Radio - choose one option from a list of options, _cannot be unselected_
- Date - Year, month, day
- Datetime - Year, month, day _and_ hour, minute, second
- Hidden - This question will not be shown (for example, the question is still in a draft state)

## About Skip Logic

Questions that take multiple choice answers (checkboxes, dropdown, multiple select, and radio) also have the ability to redirect the user to a different question based on their answer. The skip logic is configured in the question's Answer Option section, below the Field Type. You can configure as many skip logic conditions as you have answer choices for that question.

There are three parts to configuring a skip logic condition:
- Choice - what did the user select
- Skip Logic - one of three options:
  - Next default question - this will be the question immediately below this one in the Wagtail survey setup
  - End of survey - end the survey for the user and submit their results
  - Another Question - redirect the user to another question. This allows for custom flow for the survey.
- Question - If "Another Question" is selected for the Skip Logic, then this field needs to be populated with the question number to redirect to by counting off the questions in the Wagtail survey setup

{% include figure.html src="/assets/img/docs/skip-logic.png" alt="Skip Logic" caption="The skip logic setup. Additional skip logic conditions can be configured by clicking the plus buttons above or below the default skip logic box." %}