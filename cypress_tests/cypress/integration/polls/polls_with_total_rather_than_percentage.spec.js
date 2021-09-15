describe("Polls with total rather than percentage tests", () => {
    const url = "/en/sections/questionnaire-testing/poll-with-results-as-totals-rather-than-percentage/";

    it("Visits the polls page and submits it", () => {
        cy.visitUrl(url);

        cy.submit(".survey-page__btn", "Submit");
        cy.url().should("include", `/?back_url=${url}`);

        cy.thanksText(".block-paragraph > p", "thanks");
        cy.get(".cust-check__percent")
            .each(($el) => {
                cy.wrap($el)
                    .should("be.visible")
                    .contains(/^[0-9]*$/)
            });
    });
});
