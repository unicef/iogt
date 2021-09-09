describe("Poll with checkboxes test", () => {

    it("Visits poll with checkboxes", () => {
        cy.visit("/en/sections/questionnaire-testing/poll-with-checkboxes/");
        cy.url().should("include", "/en/sections/questionnaire-testing/poll-with-checkboxes/");
    });

    it("Checks for title text", () => {
        cy.get(".title.polls-widget__title")
            .contains("Poll with checkboxes")
            .should("be.visible")
    });

    it("Checks for description text", () => {
        cy.get(".polls-widget__description>div>p")
            .contains("Make your choice.")
            .should("be.visible");
    });

    it("Checks for the questions number", () => {
        cy.get(".quest-item__header .quest-item__number")
            .contains("1 of 1 question")
            .should("be.visible");
    });

    it("Checks for empty submission", () => {
        cy.get("[name=poll_checkboxes]").each($el => {
            if ($el.hasOwnProperty("required")) {
                cy.get(".survey-page__btn")
                    .contains("Submit")
                    .should("be.visible").click();

                cy.url()
                    .should("include", "/en/sections/questionnaire-testing/poll-with-checkboxes/");
            }
        });
    });

    it("Selects the multiple checkboxes and checks the text", () => {
        cy.get("[name=poll_checkboxes]")
            .each($element => {
                cy.wrap($element).should("be.visible").click()
                cy.get(".quest-item__label")
                    .should("be.visible");
            });
    });

    it("Checks for submit text and button", () => {
        cy.get(".survey-page__btn>span")
            .contains("Submit")
            .should("be.visible")
            .click();
    });

    it("Checks for successful submission", () => {
        cy.url()
            .should("include", "/?back_url=/en/sections/questionnaire-testing/poll-with-checkboxes/")
    })

    it("Checks the result text", () => {
        cy.get(".cust-check__percent")
            .each(($el) => {
                cy.wrap($el)
                    .should("be.visible")
                    .contains(/\\d+(?:d+)?|%/)
            });
    });

});