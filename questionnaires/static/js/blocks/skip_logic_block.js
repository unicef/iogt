class SkipLogicBlockDefinition extends window.wagtailStreamField.blocks.StructBlockDefinition {
    render(placeholder, prefix, initialState, initialError) {
        const block = super.render(placeholder, prefix, initialState, initialError);
        const splitPrefix = prefix.split('-');
        const fieldId = `${splitPrefix[0]}-${splitPrefix[1]}`;

        const type = $(`#${prefix}-skip_logic`);
        const questionSelect = $(`#${prefix}-question_1`);

        const showQuestionSelect = () => questionSelect.closest('.skip-logic-block>div:last-child').show();
        const hideQuestionSelect = () => questionSelect.closest('.skip-logic-block>div:last-child').hide();
        const updateQuestionSelectDisplay = () => type.val() == 'question' ? showQuestionSelect() : hideQuestionSelect();

        type.change(() => {
            updateQuestionSelectDisplay();
            populateQuestions();
        });

        updateQuestionSelectDisplay();

        return block;
    }
}

window.telepath.register('questionnaires.blocks.SkipLogicBlock', SkipLogicBlockDefinition);
