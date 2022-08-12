class SkipLogicBlockDefinition extends window.wagtailStreamField.blocks.StructBlockDefinition {
    render(placeholder, prefix, initialState, initialError) {
        const block = super.render(placeholder, prefix, initialState, initialError);
        const splitPrefix = prefix.split('-');
        const fieldPrefix = splitPrefix[0];
        const fieldId = `${splitPrefix[0]}-${splitPrefix[1]}`;

        const choice = $(`#${prefix}-choice`);
        const type = $(`#${prefix}-skip_logic`);
        const questionId = $(`#${prefix}-question_0`);
        const questionSelect = $(`#${prefix}-question_1`);

        const thisQuestion = question(fieldId);

        const showQuestionSelect = () => questionSelect.closest('.skip-logic-block>div:last-child').show();
        const hideQuestionSelect = () => questionSelect.closest('.skip-logic-block>div:last-child').hide();
        const updateQuestionSelectDisplay = () => type.val() === 'question' ? showQuestionSelect() : hideQuestionSelect();

        const populateQuestions = () => {
            questionSelect.html('');
            for (let question of allQuestions(fieldPrefix)) {
                const sortOrder = question.sortOrder();
                const label = question.label().val();
                const selected = sortOrder === questionId.val() ? 'selected' : '';
                if (thisQuestion.sortOrder() < sortOrder) {
                    questionSelect.append(
                        `<option value="${sortOrder}" ${selected}>${label}</option>`
                    );
                }
            }
        };

        type.change(() => {
            updateQuestionSelectDisplay();
            populateQuestions();
        });

        updateQuestionSelectDisplay();
        populateQuestions();

        return block;
    }
}

window.telepath.register('questionnaires.blocks.SkipLogicBlock', SkipLogicBlockDefinition);
