describe("Poll with multiline field tests", () => {
    const url = "/en/sections/questionnaire-testing/poll-multiline-field/";

    it("Visits the poll with checkbox page", () => {
        cy.visitUrl(url);
        cy.testTitle("Poll multiline field", ".title.polls-widget__title");
        cy.testDescription("text", ".polls-widget__description>div>p");
        cy.get(".quest-item__header .quest-item__number")
            .contains("1 of 1 question")
            .should("be.visible");
    });

    it("Checks for empty submission", () => {
        cy.get("[name=poll_multiline]").each($el => {
            if ($el.hasOwnProperty("required")) {
                cy.submit(".survey-page__btn", "Submit");
                cy.url().should("include", url);
            }
        });
    });

    it("Submits the form", () => {
        cy.get("[name=poll_multiline]").should("be.visible").type("Hello");
        cy.submit(".survey-page__btn>span", "Submit");

        cy.url().should("include", `/?back_url=${url}`);
        cy.thanksText(".polls-widget__form-title", "thanks");
        cy.get(".cust-check__percent")
            .each(($el) => {
                cy.wrap($el)
                    .should("be.visible")
                    .contains(/\\d+(?:d+)?|%/)
            });
    });
});