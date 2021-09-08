describe("Polls with radio tests", () => {
    it("Visits poll with radio", () => {
        cy.visit("/en/sections/questionnaire-testing/poll-with-radio");
        cy.url().should("include", "/en/sections/questionnaire-testing/poll-with-radio");
    });

    it("Checks for title text", () => {
        cy.get("h1.polls-widget__title")
            .contains("Poll with Radio").should("be.visible");
    });

    it("Checks for description text", () => {
        cy.get(".polls-widget__description>div>p")
            .contains("Make your choice.").should("be.visible");
    });

    it("Checks for the questions number", () => {
        cy.get(".quest-item__header .quest-item__number")
            .contains("1 of 1 question").should("be.visible");
    });

    it("Checks for empty submission", () => {
        cy.get(".survey-page__btn")
            .contains("Submit").should("be.visible").click()
        cy.url()
            .should("include", "/en/sections/questionnaire-testing/poll-with-radio")
    });

    it("Selects the check box for option 1 submission", () => {
        cy.get("[id=id_poll_radio_0]").check();
        cy.get(".survey-page__btn")
            .contains("Submit").should("be.visible").click();
        cy.url()
            .should("include", "/en/sections/questionnaire-testing/poll-with-radio/?back_url=/en/sections/questionnaire-testing/poll-with-radio/");
    });

    it("Checks for thank you text", () => {
        cy.get(".block-paragraph > p")
            .contains("Thank you.").should("be.visible");
    });

    it("Checks the result text", () => {
        cy.get(".cust-check__percent").each(($el) => {
            cy.wrap($el).should("be.visible").contains(/\\d+(?:d+)?|%/)
        });
    });
});