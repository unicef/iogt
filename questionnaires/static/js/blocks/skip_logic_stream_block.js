class SkipLogicStreamBlockDefinition extends window.wagtailStreamField.blocks.StreamBlockDefinition {
    render(placeholder, prefix, initialState, initialError) {
        const block = super.render(placeholder, prefix, initialState, initialError);

        const splitPrefix = prefix.split('-');
        const fieldId = `${splitPrefix[0]}-${splitPrefix[1]}`;
        const thisQuestion = question(fieldId);

        thisQuestion.fieldTypeInput().change(() => {
            if (thisQuestion.fieldTypeInput().val() == 'checkbox') {
                const addChoiceButton = thisQuestion.find('.action-add-block-skip_logic').last();
                let choices = thisQuestion.find('[id$=value-choice]');
                if (choices.length == 0) {
                    addChoiceButton.trigger('click');
                    addChoiceButton.trigger('click');
                    choices = thisQuestion.find('[id$=value-choice]');
                    choices.first().val('true');
                    choices.last().val('false');
                }
            }
            thisQuestion.updateSkipLogicLabel();
            thisQuestion.updateSkipLogicChoiceLabels();
            thisQuestion.toggleSkipLogicChoiceHelpText();
        });

        thisQuestion.updateSkipLogicLabel();
        thisQuestion.updateSkipLogicChoiceLabels();
        thisQuestion.toggleSkipLogicChoiceHelpText();

        thisQuestion.label().change(e => {
            const sortOrder = thisQuestion.sortOrder();
            allQuestionSelectors().find(`option[value=${sortOrder}]`).text(e.target.value);
        });

        const questionAdd = $(`[id$="${splitPrefix[0]}-ADD"]`);
        const questionUp = thisQuestion.find('[id$="-move-up"]');
        const questionDown = thisQuestion.find('[id$="-move-down"]');
        const questionDelete = thisQuestion.find('[id$="-DELETE-button"]');

        const wrapAddQuestion = () => {
            const nativeEvent = $._data(questionAdd[0], 'events');
            const nativeHandler = nativeEvent.click[0].handler;
            questionAdd.unbind('click', nativeHandler);

            questionAdd.click(e => {
                nativeHandler(e);
                const latestQuestion = allQuestions(splitPrefix[0]).pop();
                const sortOrder = latestQuestion.sortOrder();
                const label = `[Please update question ${sortOrder}]`;
                thisQuestion.skipLogicQuestionInputs().append(
                    `<option value="${sortOrder}">${label}</option>`
                );
            });
        };

        if (questionAdd.length == 1) {
            wrapAddQuestion();
        }

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
                opts.questionOrder = questions.map(question => question.sortOrder());
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
            const questionIndex = opts.questionOrder.indexOf(sortOrder);
            if (opts.questionOrder[questionIndex - 1] == targetSortOrder) {
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
            const questionIndex = opts.questionOrder.indexOf(sortOrder);
            if (opts.questionOrder[questionIndex + 1] == targetSortOrder) {
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
