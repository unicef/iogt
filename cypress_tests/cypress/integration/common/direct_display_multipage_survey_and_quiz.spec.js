describe("Tests for multi-page embedded forms", () => {

    const url = "/en/sections/questionnaire-testing/";

    it("Visits the questionnaire's page", () => {
        cy.visitUrl(url);
        cy.testTitle("Survey (2-pages)", ".title.survey-page__title");
        //cy.get(".quest-item__number").contains("1 of 2 questions");
        cy.get("[name=text_field]").type("test");
        cy.submit(".survey-page__btn", "Submit");
        //cy.get(".quest-item__number").contains("2 of 2 questions");
        cy.get("[id=id_checkbox]").check();
        cy.submit(".survey-page__btn", "Submit");
        cy.thanksText(".block-paragraph", "thanks");

        cy.visitUrl(url);
        cy.testTitle("Quiz (2 pages)", ".title.quiz-page__title");
        //cy.get(".quiz-page__content>div>.quest-item__header>div>p").contains("1 of 2 questions");
        cy.get(".quiz-page__content>div>.quest-item__content>label>input").check();
        cy.get(".quiz-page__btns").last().click();
        cy.submit(".survey-page__btn", "Submit");
        cy.thanksText(".block-paragraph", "thanks");
    });
});
