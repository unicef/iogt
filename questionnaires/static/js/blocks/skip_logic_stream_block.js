class SkipLogicStreamBlockDefinition extends window.wagtailStreamField.blocks.StreamBlockDefinition {
    render(placeholder, prefix, initialState, initialError) {
        const block = super.render(placeholder, prefix, initialState, initialError);

        const splitPrefix = prefix.split('-');
        const fieldId = `${splitPrefix[0]}-${splitPrefix[1]}`;
        const thisQuestion = question(fieldId);

        thisQuestion.fieldTypeInput().change(() => {
            const fieldType = thisQuestion.fieldTypeInput().val();
            if (fieldType === 'checkbox') {
                const addSkipLogicBtn = thisQuestion.addSkipLogicBtn();
                let skipLogicChoices = thisQuestion.skipLogicChoiceInputs();
                if (skipLogicChoices.length === 0) {
                    addSkipLogicBtn.trigger('click');
                    addSkipLogicBtn.trigger('click');
                    skipLogicChoices = thisQuestion.skipLogicChoiceInputs();
                    skipLogicChoices.first().val('true');
                    skipLogicChoices.last().val('false');
                }
            }
            thisQuestion.updateSkipLogicLabels();
        });

        thisQuestion.updateSkipLogicLabels();

        const allQuestionSelectors = () => $('[id$="-question_1"]');

        thisQuestion.label().change(e => {
            const sortOrder = thisQuestion.sortOrder();
            allQuestionSelectors().find(`option[value=${sortOrder}]`).text(e.target.value);
        });

        const questionUp = thisQuestion.find('[id$="-move-up"]');
        const questionDown = thisQuestion.find('[id$="-move-down"]');
        const questionDelete = thisQuestion.find('[id$="-DELETE-button"]');

        const wrapAction = (element, cb) => {
            const nativeEvent = $._data(element[0], 'events');
            const opts = {};
            if (typeof nativeEvent == "undefined") {
                opts.nativeHandler = e => {
                    // Event was bound after we bind our click
                    // so defer accessing it until it exists
                    const nativeEvent = $._data(element[0], 'events');
                    nativeEvent.click[1].handler(e);
                };
            } else {
                opts.nativeHandler = nativeEvent.click[0].handler;
            }
            element.unbind('click', opts.nativeHandler);
            element.click(e => {
                e.stopImmediatePropagation();
                let shouldEnd = false;
                const questions = allQuestions(splitPrefix[0]);
                opts.questionsOrder = questions.map(question => question.sortOrder());
                for (let question of questions) {
                    if (!shouldEnd && question.sortOrder() !== thisQuestion.sortOrder()) {
                        shouldEnd = cb(e, opts, question);
                    }
                }
            });
        };

        wrapAction(questionUp, (e, opts, question) => {
            const sortOrder = thisQuestion.sortOrder();
            const targetSortOrder = question.sortOrder();
            const questionIndex = opts.questionsOrder.indexOf(sortOrder);
            if (opts.questionsOrder[questionIndex - 1] == targetSortOrder) {
                if (question.hasSelected(sortOrder)) {
                    const questionLabel = question.label().val();
                    alert(`Cannot move above "${questionLabel}", please change the logic.`);
                    return true;
                } else {
                    question.filterSelectors(sortOrder).remove();
                    // There is a bug in wagtail preventing ordering past deleted elements
                    // fixed in 1.10 & 1.13
                    opts.nativeHandler(e);
                    swapSortOrder(sortOrder, targetSortOrder);
                    return true;
                }
            }
        });

        wrapAction(questionDown, (e, opts, question) => {
            const sortOrder = thisQuestion.sortOrder();
            const targetSortOrder = question.sortOrder();
            const questionIndex = opts.questionsOrder.indexOf(sortOrder);
            if (opts.questionsOrder[questionIndex + 1] == targetSortOrder) {
                if (thisQuestion.hasSelected(targetSortOrder)) {
                    const questionLabel = question.label().val();
                    alert(`Cannot move below "${questionLabel}", please change the logic.`);
                    return true;
                } else {
                    thisQuestion.filterSelectors(targetSortOrder).remove();
                    opts.nativeHandler(e);
                    swapSortOrder(sortOrder, targetSortOrder);

                    const label = thisQuestion.label().val();
                    question.skipLogicQuestionInputs().prepend(
                        `<option value="${sortOrder}">${label}</option>`
                    );
                    return true;
                }
            }
        });

        wrapAction(questionDelete, (e, opts, question) => {
            const sortOrder = thisQuestion.sortOrder();
            if (question.hasSelected(sortOrder)) {
                const questionLabel = question.label().val();
                alert(`Cannot delete, referenced by skip logic in question "${questionLabel}".`);
                return true;
            } else {
                opts.nativeHandler(e);
                question.filterSelectors(sortOrder).remove();
            }
        });

        const swapSortOrder = (from, to) => {
            const fromSelectors = allQuestionSelectors().find(`option[value=${from}]`);
            const toSelectors = allQuestionSelectors().find(`option[value=${to}]`);
            fromSelectors.val(to);
            toSelectors.val(from);
        };

        return block;
    }
}

window.telepath.register('questionnaires.blocks.SkipLogicStreamBlock', SkipLogicStreamBlockDefinition);
