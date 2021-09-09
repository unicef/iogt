describe("Polls with dropdown tests", () => {

    it("Visits poll with dropdown", () => {
        cy.visit("/en/sections/questionnaire-testing/sample-poll/");
        cy.url().should("include", "/en/sections/questionnaire-testing/sample-poll/");
    });

    it("Checks for title text", () => {
        cy.get(".title.polls-widget__title")
            .contains("Poll with Dropdown")
            .should("be.visible")
    });

    it("Checks for description text", () => {
        cy.get(".polls-widget__description>div>p")
            .contains("Poll description")
            .should("be.visible");
    });

    it("Checks for the questions number", () => {
        cy.get(".quest-item__header .quest-item__number")
            .contains("1 of 1 question")
            .should("be.visible");
    });

    it("Checks for empty submission", () => {
        cy.get("select").each($el => {
            if ($el.hasOwnProperty("required")) {
                cy.get(".survey-page__btn")
                    .contains("Submit")
                    .should("be.visible").click()

                cy.url()
                    .should("include", "/en/sections/questionnaire-testing/sample-poll/")
            }
        });

    });

    it("Selects the option and submits it", () => {
        cy.get(".quest-item__content>select").select('2');
        cy.get(".survey-page__btn>span")
            .contains("Submit")
            .should("be.visible")
            .click();
    });

    it("Checks for successful redirection", () => {
        cy.url()
            .should("include", "/?back_url=/en/sections/questionnaire-testing/sample-poll/");
    });

    it("Checks thanks text", () => {
        cy.get(".polls-widget__form-title")
            .contains("Poll Thank you text")
            .should("be.visible");
    });

    it("Checks the result text", () => {
        cy.get(".cust-check__percent")
            .each(($el) => {
                cy.wrap($el)
                    .contains(/\\d+(?:d+)?|%/)
                    .should("be.visible");
            });
    });
});