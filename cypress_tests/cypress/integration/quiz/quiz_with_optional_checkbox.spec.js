describe("Quiz with optional checkbox", () => {

    it("Visits the quiz page", () => {
        cy.visit("/en/sections/questionnaire-testing/quiz-with-optional-checkbox/");
        cy.url().should(
            "include",
            "/en/sections/questionnaire-testing/quiz-with-optional-checkbox/"
        );
    });

    it("Checks for title and description text", () => {
        cy.get(".quiz-page__title")
            .contains("Quiz with optional checkbox")
            .should("be.visible");

        cy.get(".quiz-page__description>.block-paragraph>p")
            .contains("quiz text")
            .should("be.visible");
    });

    it("Submits the form with out filling out", () => {
        cy.get(".survey-page__btn>span")
            .contains("Submit")
            .should("be.visible")
            .click();
    });

    it("Checks for successful redirection", () => {
        cy.url().should(
            "include",
            "/?back_url=/en/sections/questionnaire-testing/quiz-with-optional-checkbox/&form_length=2"
        );
    });

    it("Expects the result to be incorrect", () => {
        cy.get(".quiz-answer-banner__counter").contains("0 / 2");
        cy.get("p.quest-item__status").contains("Incorrect");
    });

});