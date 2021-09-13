describe("Polls for logged in users tests", () => {
    const url = "/en/sections/questionnaire-testing/poll-only-for-logged-in-users/";

    before("Login the user", () => {
        cy.login("saqlain", "saqlain");
    });

    it("Visits the polls for logged in users page", () => {
        cy.visitUrl(url);
    });

    it("Checks for title text", () => {
        cy.testTitle(
            "Poll only for logged in users",
            ".title.polls-widget__title"
        );
    });

    it("Checks for description text", () => {
        cy.testDescription(
            "Make your choice.",
            ".polls-widget__description>div>p"
        );
    });

    it("Selects the checkboxes", () => {
        cy.get("[name=poll_logged_in]").each($el => {
            cy.wrap($el)
                .should("be.visible")
                .check();
        });
    });

    it("Submits the form", () => {
        cy.submit(".survey-page__btn>span","Submit");
        cy.url().should(
            "include",
            `/?back_url=${url}`
        );
    });

});