const questionSelector = fieldId => {
    return `[id^="inline_child_${fieldId}"`;
}

const addHelperMethods = questionSelector => {
    const question = $(questionSelector);

    question.skipLogicChoiceLabels = () => question.find('label[for$="-value-choice"]');
    question.skipLogicLabel = () => question.find('label[for$="-skip_logic"]').first();
    question.fieldSelect = () => question.find('[id$="-field_type"]');
    question.sortOrder = () => parseInt(question.children('[id$="-ORDER"]').val());
    question.label = () => question.find('textarea[id$="-label"]');
    question.skipLogicChoiceHelpText = () => question.find('.skip-logic-stream-block').closest('.skip-logic').find('.help');
    question.skipLogicQuestionSelectors = () => question.find('[id$="-question_1"]');
    question.filterSelectors = sortOrder => question.skipLogicQuestionSelectors().find(`option[value=${sortOrder}]`);
    question.hasSelected = sortOrder => {
        return question.skipLogicQuestionSelectors().filter(':visible').is((index, element) => {
            return $(element).val() === sortOrder;
        });
    };
    question.updateSkipLogicLabel = () => {
        const questionType = question.fieldSelect().val();
        const newLabel = ['checkboxes', 'dropdown', 'radio'].includes(questionType) ? 'Answer options:' : 'Skip logic options:';
        question.skipLogicLabel().html(newLabel);
    };
    question.updateSkipLogicChoiceLabels = () => {
        const questionType = question.fieldSelect().val();
        const newLabel = ['checkboxes', 'dropdown', 'radio'].includes(questionType) ? 'Choice' : 'Skip value';
        question.skipLogicChoiceLabels().html(newLabel);
    };

    question.updateSkipLogicChoiceHelpText = () => {
        const questionType = question.fieldSelect().val();
        questionType === 'checkbox' ? question.skipLogicChoiceHelpText().show() : question.skipLogicChoiceHelpText().hide();
    };

    return question;
}

const question = fieldId => {
    return addHelperMethods(questionSelector(fieldId));
}

const allQuestions = fieldId => {
    return $.map($(questionSelector(fieldId)).not('.deleted'), addHelperMethods);
};

const allQuestionSelectors = () => $('[id$="-question_1"]');
