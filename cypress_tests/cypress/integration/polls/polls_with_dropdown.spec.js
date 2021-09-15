describe("Polls with dropdown tests", () => {
    const url = "/en/sections/questionnaire-testing/sample-poll/";

    it("Visits polls with dropdown", () => {
        cy.visitUrl(url);

        cy.get(".quest-item__content>select").select('2');
        cy.submit(".survey-page__btn>span", "Submit");
        cy.url().should(
            "include",
            `/?back_url=${url}`
        );

        cy.get(".cust-check__percent")
            .each(($el) => {
                cy.wrap($el)
                    .contains(/\\d+(?:d+)?|%/)
                    .should("be.visible");
            });
    });
});
