describe("Tests for embedded with article multi pages", () => {
    const url = "/en/sections/questionnaire-testing/article-with-multi-page-survey-and-quiz/";

    it("Visits the site", () => {
        cy.visitUrl(url);
        cy.testTitle("Article with multi page survey and quiz", ".article__content>h1");

        cy.testTitle("Survey (2-pages)", ".title.survey-page__title");
        //cy.get(".quest-item__number").contains("1 of 2 questions");
        cy.get("[name=text_field]").type("test");
        cy.submit(".survey-page__btn", "Next");
        //cy.get(".quest-item__number").contains("2 of 2 questions");
        cy.get("[id=id_checkboxes_0]").check();
        cy.submit(".survey-page__btn", "Submit");

        cy.visitUrl(url);
        cy.testTitle("Quiz (2 pages)", ".title.quiz-page__title");
        //cy.get(".quiz-page__content>div>.quest-item__header>div>p").contains("1 of 2 questions");
        cy.get(".quiz-page__content>div>.quest-item__content>label>input").check();
        cy.get(".quiz-page__btns>.survey-page__btn").last().click();
        cy.submit(".survey-page__btn", "Submit");

    });
});
