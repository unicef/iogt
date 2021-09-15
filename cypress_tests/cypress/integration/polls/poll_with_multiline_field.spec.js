describe("Poll with multiline field tests", () => {
    const url = "/en/sections/questionnaire-testing/poll-multiline-field/";

    it("Visits the poll page", () => {
        cy.visitUrl(url);

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
        cy.get(".cust-check__percent")
            .each(($el) => {
                cy.wrap($el)
                    .should("be.visible")
                    .contains(/\\d+(?:d+)?|%/)
            });
    });
});