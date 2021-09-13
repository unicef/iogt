describe("Polls with dropdown tests", () => {
    const url = "/en/sections/questionnaire-testing/sample-poll/";

    it("Visits polls with dropdown", () => {
        cy.visitUrl(url);
        cy.testTitle("Poll with Dropdown", ".title.polls-widget__title");
        cy.testDescription("Poll description", ".polls-widget__description>div>p");
        cy.get(".quest-item__header .quest-item__number")
            .contains("1 of 1 question")
            .should("be.visible");
    });

    it("Submits the empty form", () => {
        cy.get("select").each($el => {
            if ($el.hasOwnProperty("required")) {
                cy.submit(".survey-page__btn", "Submit");
                cy.url().should("include", url);
            }
        });

        cy.get(".quest-item__content>select").select('2');
        cy.submit(".survey-page__btn>span", "Submit");
        cy.url().should(
            "include",
            `/?back_url=${url}`
        );

        cy.thanksText(".polls-widget__form-title", "Poll Thank you text");

        cy.get(".cust-check__percent")
            .each(($el) => {
                cy.wrap($el)
                    .contains(/\\d+(?:d+)?|%/)
                    .should("be.visible");
            });
    });
});
