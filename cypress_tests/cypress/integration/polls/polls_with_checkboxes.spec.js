describe("Poll with checkboxes test", () => {
    const url = "/en/sections/questionnaire-testing/poll-with-checkboxes/";

    it("Visits poll with checkboxes", () => {
        cy.visitUrl(url);
        cy.testTitle("Poll with checkboxes", ".title.polls-widget__title");
        cy.testDescription(
            "Make your choice.",
            ".polls-widget__description>div>p"
        );
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

    it("Selects the multiple checkboxes and submits it", () => {
        cy.get("[name=poll_checkboxes]")
            .each($element => {
                cy.wrap($element).should("be.visible").click()
                cy.get(".quest-item__label")
                    .should("be.visible");
            });

        cy.submit(".survey-page__btn>span", "Submit");
        cy.url().should("include", `/?back_url=${url}`);

        cy.get(".cust-check__percent").each(($el) => {
            cy.wrap($el)
                .should("be.visible")
                .contains(/\\d+(?:d+)?|%/)
        });
    });
});
