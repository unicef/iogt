---
title: Creating Polls
permalink: /cms-manual/content/polls/
---

Home page polls are a great way to get feedback and information about your end user. They can also be used to generate interest in your site, if you make these topical and engaging.

There are a number of different poll types available:

- Select an answer from a list of pre-determined answer choices
- Select more than one answer poll answer
- Free-response text answers to a question

## How to create a poll

There are two main ways to create a poll. The first involves selecting "Polls" directly from the main menu. The second, and perhaps more intuitive, is to create the poll through the Pages menu and navigating to where the poll should be placed. We will cover both cases.

### Creating a poll from the Polls Menu

Select "Polls" from the main menu. Then select `Add Poll` in the top right corner of the page. Then select the parent page for the new Poll. Click the `Continue` button on the bottom of the page.

Skip to the "Configuring the new poll" section below to continue.

{% include figure.html src="/assets/img/docs/polls-menu.png" alt="Polls Menu" caption="The Polls Menu. To create a poll, select 'Add Poll' in the top right corner of the page. To edit an existing poll, simply click on the Edit button by hovering over the poll name." %}

### Creating a poll from the Pages Menu

Using the Pages menu, navigate to the subsection/category you would like to create the new poll in. Clikc `Add Child Page` below the subsection title. Then click the `Poll` option. Skip to the "Configuring the new poll" section below to continue.

### Configuring the new poll

On the New Poll page, fill out the Poll title. There are a number of options that you can configure for the poll. These options pertain to the frontend _only_ and will not affect how the admins see or edit the poll through Wagtail:

- Allow anonymous submissions
    - Users who are not logged in will be allowed to submit an answer
- Show results
    - Allow users to view the results of the poll after answering
- Results as a percentage
    - Show poll results as a percentage instead of a raw count. _This only has an affect if `Show results` is enabled.
- Allow multiple submissions
    - Allow users to submit multiple answers

Then, edit the text that will appear on the button to submit. By default, it is "Submit". After this, edit the Poll description and the Thank You page message. The Thank You page message is usually along the lines of "Thank you for submitting your answers" or "Your response has been recorded".

{% include figure.html src="/assets/img/docs/new-poll.png" alt="New Poll" caption="Creating a new poll. See the bulleted list above for help on the various configuration options for the new poll." %}

You will then be able to enter the questions and possible answers:

- Label
    - This is the name of the question
- Help text
    - An optional field that provides additional context for the question to the user
- Required
    - Select this checkbox if the user is required to answer the question before submitting the poll
- Field type
    - Checkbox: User can select and unselect a single checkbox for the question. An example use case is user acknowledgement of terms and conditions
    - Checkboxes: User can select and unselect a group of checkboxes for the question.
    - Multiple Select: User selects multiple choices from a list of pre-determined answers
    - Radio Buttons: User can only select one answer from a list of pre-determined answers
- Choices
    - For questions that support multiple choices, these are the available answers to choose from
- Default value
    - A single or multiple options that are pre-selected

Selecting `Add Poll Form Fields` will create a new question within the poll.