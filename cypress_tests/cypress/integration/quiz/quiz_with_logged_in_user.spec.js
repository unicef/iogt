describe("", () => {
    const url = "/en/sections/questionnaire-testing/sample-quiz/";

    before("Login", () => {
        cy.login("saqlain", "saqlain");
    });

    it("Visits the quiz page", () => {
        cy.visitUrl(url);
        cy.testTitle("Quiz with logged in user", ".quiz-page__title");
        cy.testDescription(
            "quiz intro text",
            ".quiz-page__description>.block-paragraph>p"
        );

        cy.get(".quest-item__number").contains("1 of 2 questions");
        cy.get(".quest-item__number").contains("2 of 2 questions");
        cy.get(".quest-item__step-desc>span").contains("Select one");
        cy.get(".quest-item__step-desc>span").contains("Select one");
    });

    it("Selects the answers and submit them", () => {
        cy.get("[id=id_radio_button_question_0]").click();
        cy.get("select").select("c2");

        cy.submit("button[type=submit]>span", "Submit");
        cy.url().should("include", `/?back_url=${url}&form_length=2`);
    });
});