describe("Poll with checkbox tests", () => {
    const url = "/en/sections/questionnaire-testing/poll-with-checkbox/";

    it("Visits the poll with checkbox page", () => {
        cy.visitUrl(url);
    });

    it("Checks for title text", () => {
        cy.testTitle(
            "Poll with checkbox",
            ".title.polls-widget__title"
        );
    });

    it("Checks for description text", () => {
        cy.testDescription(
            "Make your choice.",
            ".polls-widget__description>div>p"
        );
    });

    it("Checks for empty submission", () => {
        cy.get("[name=poll_checkbox]").each($el => {
            if ($el.hasOwnProperty("required")) {
                cy.get(".survey-page__btn")
                    .contains("Submit")
                    .should("be.visible").click();

                cy.url().should("include", url);
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
        cy.submit(".survey-page__btn>span","Submit");
    });

    it("Checks for successful redirection after submit", () => {
        cy.url().should(
            "include",
            `/?back_url=${url}`
        );
    });

    it("Checks thanks text", () => {
        cy.thanksText(".polls-widget__form-title", "thanks");
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