describe("Polls for logged in users tests", () => {
    const url = "/en/sections/questionnaire-testing/poll-only-for-logged-in-users/";

    before("Login the user", () => {
        cy.login("saqlain", "saqlain");
    });

    it("Visits the polls page and check texts", () => {
        cy.visitUrl(url);
        cy.testTitle("Poll only for logged in users", ".title.polls-widget__title");
        cy.testDescription("Make your choice.", ".polls-widget__description>div>p");

        cy.get(".quest-item__header .quest-item__number")
            .contains("1 of 1 question")
            .should("be.visible");
    });

    it("Selects the checkbox and submits it", () => {
        cy.get("[name=poll_logged_in]").each($el => {
            cy.wrap($el).should("be.visible").check();
        });

        cy.submit(".survey-page__btn>span", "Submit");
        cy.url().should("include", `/?back_url=${url}`);
    });
});
