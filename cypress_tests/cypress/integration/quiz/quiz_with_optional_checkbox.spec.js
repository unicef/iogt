describe("Quiz with optional checkbox", () => {
    const url = "/en/sections/questionnaire-testing/quiz-with-optional-checkbox/";

    it("Visits the quiz page", () => {
        cy.visitUrl(url);
        cy.testTitle(
            "Quiz with optional checkbox",
            ".quiz-page__title"
        );
        cy.testDescription(
            "quiz text",
            ".quiz-page__description>.block-paragraph>p"
        );
    });

    it("Submits the form without filling it", () => {
        cy.submit(".survey-page__btn>span", "Submit");
        cy.url().should(
            "include",
            `/?back_url=${url}&form_length=2`
        );

        cy.get(".quiz-answer-banner__counter").contains("0 / 2");
        cy.get("p.quest-item__status").contains("Incorrect");
    });
});
