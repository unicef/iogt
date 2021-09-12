describe("Quiz with required checkbox tests", () => {

    it("Visits the quiz page", () => {
        cy.visit("/en/sections/questionnaire-testing/quiz-with-checkbox/");
        cy.url().should(
            "include",
            "/en/sections/questionnaire-testing/quiz-with-checkbox/"
        );
    });

    it("Checks for title, description, help text", () => {
        cy.get(".quiz-page__title")
            .contains("Quiz with checkbox")
            .should("be.visible");

        cy.get(".quiz-page__description>.block-paragraph>p")
            .contains("quiz intro")
            .should("be.visible");

        cy.get(".quest-item__step-desc>span")
            .contains("Check if apply")
            .should("be.visible");
    });

    it("Submits the empty forum", () => {
        cy.get(".survey-page__btn>span")
            .contains("Submit")
            .should("be.visible")
            .click();

        cy.url().should(
            "include",
            "/en/sections/questionnaire-testing/quiz-with-checkbox/"
        );
    });

    it("Checks the checkbox", () => {
        cy.get("[name=checkbox]").check();
    });

    it("Submits the form with required field", () => {
        cy.get(".survey-page__btn>span")
            .contains("Submit")
            .should("be.visible")
            .click();
    })

    it("Checks for successful redirection", () => {
        cy.url().should(
            "include",
            "/?back_url=/en/sections/questionnaire-testing/quiz-with-checkbox/&form_length=1"
        );
    });

    it("Expects the result to be correct", () => {
        cy.get(".quiz-answer-banner__counter").contains("1 / 1");
        cy.get("p.quest-item__status").contains("Correct");
    });

});