describe("Polls with total rather than percentage tests", () => {
    const url = "/en/sections/questionnaire-testing/poll-with-results-as-totals-rather-than-percentage/";

    it("Visits the polls page", () => {
        cy.visitUrl(url);
        cy.testTitle(
            "Poll with results as totals rather than percentage",
            "h1.polls-widget__title"
        );
        cy.testDescription(
            "Make your choice.",
            ".polls-widget__description>div>p"
        );
        cy.get(".quest-item__header .quest-item__number")
            .contains("1 of 1 question")
            .should("be.visible");
    });

    it("Submits the poll", () => {
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
