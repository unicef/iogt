describe("Tests for embedded poll, survey, and quiz", () => {
    const url = "/en/sections/questionnaire-testing/article-with-poll-survey-and-quiz/";

    it("Visits the article page", () => {
        cy.visitUrl(url);
        cy.testTitle("Article with poll, survey, and quiz", ".article__content>h1");

        cy.get("[id=id_poll_radio_1]").check()
        cy.submit(".polls-widget__submit", "Submit");
        cy.submit(".btn-back__title", "BACK")

        cy.get(".survey-page__content>div>label>input").check();
        cy.submit(".survey-page__btn", "Submit")
        cy.visitUrl(url);

        cy.get(".quiz-page__content>div>label>input").check();
        cy.submit(".quiz-page__btn>span", "Submit");
    });

});