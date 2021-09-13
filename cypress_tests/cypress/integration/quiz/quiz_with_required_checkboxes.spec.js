describe("Quiz with required checkbox tests", () => {
    const url = "/en/sections/questionnaire-testing/quiz-with-checkbox/";

    it("Visits the quiz page", () => {
        cy.visitUrl(url);
    });

    it("Checks for title, description, help text", () => {
        cy.testTitle("Quiz with checkbox", ".quiz-page__title");
        cy.testDescription(
            "quiz intro",
            ".quiz-page__description>.block-paragraph>p"
        );

        cy.get(".quest-item__step-desc>span")
            .contains("Check if apply")
            .should("be.visible");
    });

    it("Submits the empty forum", () => {
        cy.submit(".survey-page__btn>span", "Submit");

        cy.url().should(
            "include",
            "/en/sections/questionnaire-testing/quiz-with-checkbox/"
        );
    });

    it("Checks the checkbox", () => {
        cy.get("[name=checkbox]").check();
    });

    it("Submits the form with required field", () => {
        cy.submit(".survey-page__btn>span", "Submit");
    })

    it("Checks for successful redirection", () => {
        cy.url().should(
            "include",
            `/?back_url=${url}&form_length=1`
        );
    });

    it("Expects the result to be correct", () => {
        cy.get(".quiz-answer-banner__counter").contains("1 / 1");
        cy.get("p.quest-item__status").contains("Correct");
    });

});