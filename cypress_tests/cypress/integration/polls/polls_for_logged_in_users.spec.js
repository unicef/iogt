describe("Polls for logged in users tests", () => {

    beforeEach("Login the user", () => {
        cy.login("saqlain", "saqlain");
        cy.visit("/en/sections/questionnaire-testing/poll-only-for-logged-in-users/")
    });

    it("Visits the polls for logged in users page", () => {
        cy.visit("/en/sections/questionnaire-testing/poll-only-for-logged-in-users/");
        cy.url()
            .should("include", "/en/sections/questionnaire-testing/poll-only-for-logged-in-users/");
    });

    it("Checks for title text", () => {
        cy.get(".title.polls-widget__title")
            .contains("Poll only for logged in users")
            .should("be.visible");
    });

    it("Checks for description text", () => {
        cy.get(".polls-widget__description>div>p")
            .contains("Make your choice.")
            .should("be.visible");
    });

    it("Selects the checkboxes", () => {
        cy.get("[name=poll_logged_in]").each($el => {
            cy.wrap($el)
                .should("be.visible")
                .check();
        });
    });

    it("Submits the form", () => {
        cy.get(".survey-page__btn>span")
            .contains("Submit")
            .should("be.visible")
            .click();
        cy.url()
            .should("include", "/?back_url=/en/sections/questionnaire-testing/poll-only-for-logged-in-users/");
    });

});