describe("Polls for logged in users tests", () => {
    const url = "/en/sections/questionnaire-testing/poll-only-for-logged-in-users/";

    before("Login the user", () => {
        cy.login("saqlain", "saqlain");
    });

    it("Visits the polls page and submits it", () => {
        cy.visitUrl(url);

        cy.get("[name=poll_logged_in]").each($el => {
            cy.wrap($el).should("be.visible").check();
        });

        cy.submit(".survey-page__btn>span", "Submit");
        cy.url().should("include", `/?back_url=${url}`);
    });
});
