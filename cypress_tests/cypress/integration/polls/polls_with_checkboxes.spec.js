describe("Poll with checkboxes test", () => {
    const url = "/en/sections/questionnaire-testing/poll-with-checkboxes/";

    it("Visits poll with checkboxes", () => {
        cy.visitUrl(url);
    });

    it("Checks for title text", () => {
        cy.testTitle(
            "Poll with checkboxes",
            ".title.polls-widget__title"
        );
    });

    it("Checks for description text", () => {
        cy.testDescription(
            "Make your choice.",
            ".polls-widget__description>div>p"
        );
    });

    it("Checks for the questions number", () => {
        cy.get(".quest-item__header .quest-item__number")
            .contains("1 of 1 question")
            .should("be.visible");
    });

    it("Checks for empty submission", () => {
        cy.get("[name=poll_checkboxes]").each($el => {
            if ($el.hasOwnProperty("required")) {
                cy.submit(".survey-page__btn", "Submit");
                cy.url().should("include", url);
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
        cy.submit(".survey-page__btn>span", "Submit");
    });

    it("Checks for successful submission", () => {
        cy.url().should(
            "include",
            `/?back_url=${url}`
        );
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