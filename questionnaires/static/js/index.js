$(document).ready(() => {
    const handleQuizChoicesField = question => {
        const choicesField = question.find('.formbuilder-choices').first();
        const fieldType = question.find('[id$=-field_type]').first();
        if (['hidden', ''].includes(fieldType.val())) {
            choicesField.css('display', 'none');
        }
        fieldType.change(e => {
            if (['hidden', ''].includes(fieldType.val())) {
                choicesField.css('display', 'none');
            } else {
                choicesField.css('display', 'block');
            }
            if (e.target.value === 'checkbox') {
                question.find('[id$=-choices]').first().val('true|false');
            } else {
                question.find('[id$=-choices]').first().val('');
            }
        });
    };

    $('[id^="inline_child_quiz_form_fields-').each((index, question) => {
        handleQuizChoicesField($(question));
    });

    $('#id_quiz_form_fields-ADD').click(e => {
        const latestQuestion = $('[id^="inline_child_quiz_form_fields-').last();
        handleQuizChoicesField(latestQuestion);
    });

    const handleSurveyChoicesField = question => {
        const skipLogicField = question.find('.stream-field').first();
        const fieldType = question.find('[id$=-field_type]').first();
        if (['hidden', ''].includes(fieldType.val())) {
            skipLogicField.css('display', 'none');
        }
        fieldType.change(e => {
            if (['hidden', ''].includes(fieldType.val())) {
                skipLogicField.css('display', 'none');
            } else {
                skipLogicField.css('display', 'block');
            }
            if (e.target.value === 'checkbox') {
                const addChoiceButton = question.find('.action-add-block-skip_logic').last();
                let choices = question.find('[id$=value-choice]');
                if (choices.length === 0) {
                    addChoiceButton.click();
                    addChoiceButton.click();
                    choices = question.find('[id$=value-choice]');
                    choices.first().val('true');
                    choices.last().val('false');
                }
            }
        });
    };

    $('[id^="inline_child_survey_form_fields-').each((index, question) => {
        handleSurveyChoicesField($(question));
    });

    $('#id_survey_form_fields-ADD').click(e => {
        const latestQuestion = $('[id^="inline_child_survey_form_fields-').last();
        handleSurveyChoicesField(latestQuestion);
    });
});