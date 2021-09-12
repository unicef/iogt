describe("Poll with checkbox tests", () => {

    it("Visits the poll with checkbox page", () => {
        cy.visit("/en/sections/questionnaire-testing/poll-with-checkbox/");
        cy.url().should(
            "include",
            "/en/sections/questionnaire-testing/poll-with-checkbox/"
        );
    });

    it("Checks for title text", () => {
        cy.get(".title.polls-widget__title")
            .contains("Poll with checkbox")
            .should("be.visible")
    });

    it("Checks for description text", () => {
        cy.get(".polls-widget__description>div>p")
            .contains("Make your choice.")
            .should("be.visible");
    });

    it("Checks for empty submission", () => {
        cy.get("[name=poll_checkbox]").each($el => {
            if ($el.hasOwnProperty("required")) {
                cy.get(".survey-page__btn")
                    .contains("Submit")
                    .should("be.visible").click();

                cy.url().should(
                    "include",
                    "/en/sections/questionnaire-testing/poll-with-checkbox/"
                );
            }
        });
    });

    it("Checks for the questions number", () => {
        cy.get(".quest-item__header .quest-item__number")
            .contains("1 of 1 question")
            .should("be.visible");
    });

    it("Clicks on the checkbox and checks the text", () => {
        cy.get("[name=poll_checkbox]")
            .should("be.visible")
            .click();

        cy.get(".quest-item__label")
            .contains("poll-checkbox")
            .should("be.visible");
    });

    it("Checks for submit text and button", () => {
        cy.get(".survey-page__btn>span")
            .contains("Submit")
            .should("be.visible")
            .click();
    });

    it("Checks for successful redirection after submit", () => {
        cy.url()
            .should(
                "include",
                "/?back_url=/en/sections/questionnaire-testing/poll-with-checkbox/"
            );
    });

    it("Checks thanks text", () => {
        cy.get(".polls-widget__form-title")
            .contains("thanks")
            .should("be.visible");
    });

    it("Checks the result text", () => {
        cy.get(".cust-check__percent")
            .each(($el) => {
                cy.wrap($el)
                    .should("be.visible")
                    .contains(/\\d+(?:d+)?|%/)
            });
    });
});