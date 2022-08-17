class SkipLogicBlockDefinition extends window.wagtailStreamField.blocks.StructBlockDefinition {
    render(placeholder, prefix, initialState, initialError) {
        const block = super.render(placeholder, prefix, initialState, initialError);

        const type = $(`#${prefix}-skip_logic`);
        const questionSelect = $(`#${prefix}-question_1`);

        const toggleQuestionInput = () => {
            const questionElement = questionSelect.closest('.skip-logic-block>div:last-child');
            type.val() === 'question' ? questionElement.show() : questionElement.hide();
        };

        type.change(() => {
            toggleQuestionInput();
        });

        toggleQuestionInput();

        return block;
    }
}

window.telepath.register('questionnaires.blocks.SkipLogicBlock', SkipLogicBlockDefinition);
