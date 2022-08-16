const questionSelector = fieldId => {
    return `[id^="inline_child_${fieldId}"`;
}

const addHelperMethods = questionSelector => {
    const question = $(questionSelector);

    question.label = () => question.find('textarea[id$="-label"]');
    question.fieldTypeInput = () => question.find('[id$="-field_type"]');
    question.skipLogicLabel = () => question.find('label[for$="-skip_logic"]').first();
    question.skipLogicChoiceLabels = () => question.find('label[for$="-value-choice"]');
    question.skipLogicChoiceInputs = () => question.find('input[id$="-value-choice"]');
    question.skipLogicTypeLabels = () => question.find('label[for$="-value-skip_logic"]');
    question.skipLogicTypeInputs = () => question.find('select[for$="-value-skip_logic"]');
    question.skipLogicQuestions = () => question.find('[id*="-question_"]');
    question.skipLogicQuestionInputs = () => question.find('[id$="-question_1"]');
    question.skipLogicChoiceHelpText = () => question.find('.skip-logic-stream-block').closest('.skip-logic').find('p.help>strong');
    question.sortOrder = () => parseInt(question.children('[id$="-ORDER"]').val());
    question.filterSelectors = sortOrder => question.skipLogicQuestionInputs().find(`option[value=${sortOrder}]`);
    question.hasSelected = sortOrder => {
        return question.skipLogicQuestionInputs().filter(':visible').is((index, element) => {
            return $(element).val() === sortOrder;
        });
    };
    question.updateSkipLogicLabels = () => {
        const questionType = question.fieldTypeInput().val();
        if (['checkboxes', 'dropdown', 'radio'].includes(questionType)) {
            question.skipLogicLabel().html('Answer options:');
            question.skipLogicChoiceLabels().html('Choice');
        } else {
            question.skipLogicLabel().html('Skip logic options:');
            question.skipLogicChoiceLabels().html('Skip value');
        }
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

const populateAllQuestions = () => {
    const questions = allQuestions('survey_form_fields')
    for (const thisQuestion of questions) {
        thisQuestion.updateSkipLogicLabels();
        const skipLogicQuestions = thisQuestion.skipLogicQuestions();
        for (let i = 0; i < skipLogicQuestions.length; i += 2) { // each question has input and select elements
            const input = $(skipLogicQuestions[i]);
            const select = $(skipLogicQuestions[i + 1]);
            for (let question of questions) {
                const sortOrder = question.sortOrder();
                const label = question.label().val();
                const selected = sortOrder == input.val() ? 'selected' : '';
                if (sortOrder > thisQuestion.sortOrder()) {
                    select.append(
                        `<option value="${sortOrder}" ${selected}>${label}</option>`
                    );
                }
            }
        }
    }
};

$(document).ready(() => {
    populateAllQuestions();
});
