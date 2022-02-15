describe("Checks for all the text present on quiz, polls, and surveys", () => {

    it("Check polls commons", () => {
        cy.visitUrl("/en/sections/questionnaire-testing/poll-with-checkboxes/");
        cy.testTitle("Poll with checkboxes", ".title.polls-widget__title");
        cy.testDescription("Make your choice.", ".polls-widget__description>div>p");
        //cy.testQuestions(".quest-item__header .quest-item__number"), believe this text (eg. 1 of 1) has been removed from latest build
        cy.submit(".survey-page__btn", "Submit");
        cy.get(".cust-input__error").contains("This field is required.");
        cy.get("[id=id_poll_checkboxes_0]").check();
        cy.submit(".survey-page__btn", "Submit");
        cy.thanksText(".polls-widget__description", "thanks.");
    });

    it("Checks survey commons", () => {
        cy.visitUrl("/en/surveys/survey-title/");
        cy.testTitle("Survey title", ".title.survey-page__title");
        cy.testDescription("text", ".survey-page__description>div>p");
        //cy.testQuestions(".quest-item__header .quest-item__number"), believe this text (eg. 1 of 1) has been removed from the latest build
        cy.submit(".survey-page__btn", "Submit");
        cy.thanksText(".survey-page__description>div>p", "thanks");
    });

    it("Checks quiz commons", () => {
        cy.visitUrl("/en/sections/questionnaire-testing/quiz-with-optional-checkbox/");
        cy.testTitle("Quiz with optional checkbox", ".title.quiz-page__title");
        cy.testDescription("quiz text", ".quiz-page__description>div>p");
        //cy.testQuestions(".quest-item__header .quest-item__number"), believe this text (eg. 1 of 1) has been removed from the latest build
        cy.submit(".survey-page__btn", "Submit");
        cy.thanksText(".quiz-page__description>div>p", "thanks for quizzing");
    });
});
