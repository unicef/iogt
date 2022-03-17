(function($) {
    var questionSelector = function(field) {
        return '[id^="inline_child_' + field + '"]';
    };

    var addHelperMethods = function (question) {
        question = $(question);
        question.choices = () => question.find('[id$="-skip_logic-list"]').closest('.skip-logic');
        question.fieldSelect = () => question.find('[id$="-field_type"]');
        question.sortOrder = () => parseInt(question.children('[id$="-ORDER"]').val());
        question.quesiontID = () => question.children('[id$="-id"]').val();
        question.label = () => question.find('input[id$="-label"]');
        question.questionSelectors = () => question.find('[id$="-question_1"]');
        question.questionSelectors = () => question.find('[id$="-question_1"]');
        question.answerHelpText = () => question.choices().find('.help');
        question.questionHelpText = () => question.find('[id$=-help_text]');
        question.addBlockLabel = () => question.find('.action-add-block-skip_logic').children('span');
        question.filterSelectors = sortOrder => question.questionSelectors().find(`option[value=${sortOrder}]`);
        question.hasSelected = sortOrder => {
            return question.questionSelectors().filter(':visible').is( function(index, element) {
                return $(element).val() == sortOrder;
            } );
        };
        question.setAddBlockLabel = newLabel => question.addBlockLabel().text(newLabel);
        question.setAnswerLabel = (newAnswerOptionLabel, newAnswerChoiceLabel) => {
            question.choices().find('label').first().html(newAnswerOptionLabel);
            question.choices().find('.struct-block').each((index, element) => {
                $(element).find('label').first().html(newAnswerChoiceLabel)
            })
        };
        question.setQuestionHelpText = (helpText) => {
            if (!question.questionHelpText().val()) {
                question.questionHelpText().val(helpText);
            }
        };
        question.updateAnswerOptionLabel = () => {
            if (['checkboxes', 'dropdown', 'radio'].includes(question.fieldSelect().val())) {
                question.setAnswerLabel('Answer Options', 'Choice')
            } else {
                question.setAnswerLabel('Skip Logic Options', 'Skip Value')
            }
        };
        question.updateQuestionHelpText = () => {
            if (question.fieldSelect().val() ==='date') {
                question.setQuestionHelpText('Date must be in this (YYYY-MM-DD) format');
            } else if (question.fieldSelect().val() === 'datetime') {
                question.setQuestionHelpText('Datetime must be in this YYYY-MM-DDTHH:SS format');
            }
        };
        return question;
    };

    window.question = function(id) {
        this.fieldID = id;
        return addHelperMethods(questionSelector(this.fieldID));
    };

    window.allQuestions = function(id) {
        var allQuestions = $(questionSelector(id)).not('.deleted');
        allQuestions = $.map(allQuestions, addHelperMethods);
        return allQuestions;
    };

    window.SkipLogicStreamBlock = function(opts) {
        var initializer = StreamBlock(opts);
        var validSelectors = [
            'checkbox', 'checkboxes', 'date', 'datetime', 'dropdown', 'email', 'singleline', 'multiline', 'number',
            'positivenumber', 'radio', 'url'
        ];
        return function(elementPrefix) {
            initializer(elementPrefix);
            var splitPrefix = elementPrefix.split('-');
            var fieldID = splitPrefix[0] + '-' + splitPrefix[1];
            var thisQuestion = question(fieldID);

            var allQuestionSelectors = () => $('[id$="-question_1"]');

            var updateAnswerDisplay = function(duration) {
                if (shouldHide()) {
                    hideChoices(duration);
                } else {
                    showChoices(duration);
                }
                if (thisQuestion.fieldSelect().val() === 'checkbox') {
                    const addChoiceButton = thisQuestion.find('.action-add-block-skip_logic').last();
                    let choices = thisQuestion.find('[id$=value-choice]');
                    if (choices.length === 0) {
                        addChoiceButton.click();
                        addChoiceButton.click();
                        choices = thisQuestion.find('[id$=value-choice]');
                        choices.first().val('true');
                        choices.last().val('false');
                    }
                    thisQuestion.answerHelpText().show();
                } else {
                    thisQuestion.answerHelpText().hide();
                }
                thisQuestion.updateAnswerOptionLabel();
            };

            var shouldHide = function () {
                return validSelectors.indexOf(thisQuestion.fieldSelect().val()) < 0;
            };

            var showChoices = function(duration) {
                thisQuestion.choices().show(duration);
            };

            var hideChoices = function(duration) {
                thisQuestion.choices().hide(duration);
            };

            updateAnswerDisplay(0);
            thisQuestion.updateQuestionHelpText();

            thisQuestion.fieldSelect().change( function () {
                updateAnswerDisplay(250);
                thisQuestion.updateQuestionHelpText();
            });

            var wrapAction = function (element, cb) {
                var nativeEvent = $._data(element[0], 'events');
                var opts = {};
                if (typeof nativeEvent == "undefined") {
                    opts.nativeHandler = function(event){
                        // Event was bound after we bind our click
                        // so defer accessing it until it exists
                        var nativeEvent = $._data(element[0], 'events');
                        nativeEvent.click[1].handler(event);
                    };
                } else {
                    opts.nativeHandler = nativeEvent.click[0].handler;
                }
                element.unbind('click', opts.nativeHandler);
                element.click(function(event) {
                    event.stopImmediatePropagation();
                    var shouldEnd = false;
                    var questions = allQuestions(splitPrefix[0]);
                    opts.questionOrder = questions.map(question => question.sortOrder());
                    for (let question of questions) {
                        if (!shouldEnd && question.sortOrder() !== thisQuestion.sortOrder()) {
                            shouldEnd = cb.bind(opts)(event, question);
                        }
                    }
                });
            };

            thisQuestion.label().change( function(event) {
                var sortOrder = thisQuestion.sortOrder();
                allQuestionSelectors().find(`option[value=${sortOrder}]`).text(event.target.value);
            });

            var wrapAddQuestion = function() {
                var addQuestion = $('[id$="' + splitPrefix[0] + '-ADD"]');
                var nativeEvent = $._data(addQuestion[0], 'events');
                var nativeHandler = nativeEvent.click[0].handler;
                addQuestion.unbind('click', nativeHandler);

                addQuestion.click(function (event) {
                    nativeHandler(event);
                    var latestQuestion = allQuestions(splitPrefix[0]).pop();
                    var sortOrder = latestQuestion.sortOrder();
                    var label = `[Please update question ${sortOrder}]`;
                    thisQuestion.questionSelectors().append(
                        `<option value="${sortOrder}">${label}</option>`
                    );
                });
            };

            wrapAddQuestion();

            var swapSortOrder = function (from, to) {
                var fromSelectors = allQuestionSelectors().find(`option[value=${from}]`);
                var toSelectors = allQuestionSelectors().find(`option[value=${to}]`);
                fromSelectors.val(to);
                toSelectors.val(from);
            };

            var questionUp = thisQuestion.find('[id$="-move-up"]');
            var questionDown = thisQuestion.find('[id$="-move-down"]');
            var questionDelete = thisQuestion.find('[id$="-DELETE-button"]');

            wrapAction(questionDelete, function(event, question) {
                var sortOrder = thisQuestion.sortOrder();
                if ( question.hasSelected(sortOrder) ) {
                    var questionLabel = question.label().val();
                    alert(`Cannot delete, referenced by skip logic in question "${questionLabel}".`);
                    return true;
                } else {
                    this.nativeHandler(event);
                    question.filterSelectors(sortOrder).remove();
                }
            });
            wrapAction(questionUp, function(event, question) {
                var sortOrder = thisQuestion.sortOrder();
                var targetSortOrder = question.sortOrder();
                var questionIndex = this.questionOrder.indexOf(sortOrder);
                if ( this.questionOrder[questionIndex - 1]  == targetSortOrder ) {
                    if ( question.hasSelected(sortOrder) ) {
                        var questionLabel = question.label().val();
                        alert(`Cannot move above "${questionLabel}", please change the logic.`);
                        return true;
                    } else {
                        question.filterSelectors(sortOrder).remove();
                        // There is a bug in wagtail preventing ordering past deleted elements
                        // fixed in 1.10 & 1.13
                        this.nativeHandler(event);
                        swapSortOrder(sortOrder, targetSortOrder);
                        return true;
                    }
                }
            });
            wrapAction(questionDown, function(event, question) {
                var sortOrder = thisQuestion.sortOrder();
                var targetSortOrder = question.sortOrder();
                var questionIndex = this.questionOrder.indexOf(sortOrder);
                if ( this.questionOrder[questionIndex + 1]  == targetSortOrder) {
                    if ( thisQuestion.hasSelected(targetSortOrder) ) {
                        var questionLabel = question.label().val();
                        alert(`Cannot move below "${questionLabel}", please change the logic.`);
                        return true;
                    } else {
                        thisQuestion.filterSelectors(targetSortOrder).remove();
                        this.nativeHandler(event);
                        swapSortOrder(sortOrder, targetSortOrder);

                        var label = thisQuestion.label().val();
                        question.questionSelectors().prepend(
                            `<option value="${sortOrder}">${label}</option>`
                        );
                        return true;
                    }
                }
            });
        };
    };
})(jQuery);
