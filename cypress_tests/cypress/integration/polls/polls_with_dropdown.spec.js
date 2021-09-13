describe("Polls with dropdown tests", () => {
    const url = "/en/sections/questionnaire-testing/sample-poll/";

    it("Visits poll with dropdown", () => {
        cy.visitUrl(url);
    });

    it("Checks for title text", () => {
        cy.testTitle(
            "Poll with Dropdown",
            ".title.polls-widget__title"
        );
    });

    it("Checks for description text", () => {
        cy.testDescription(
            "Poll description",
            ".polls-widget__description>div>p"
        );
    });

    it("Checks for the questions number", () => {
        cy.get(".quest-item__header .quest-item__number")
            .contains("1 of 1 question")
            .should("be.visible");
    });

    it("Checks for empty submission", () => {
        cy.get("select").each($el => {
            if ($el.hasOwnProperty("required")) {
                cy.submit(".survey-page__btn", "Submit");
                cy.url().should("include", url);
            }
        });

    });

    it("Selects the option and submits it", () => {
        cy.get(".quest-item__content>select").select('2');
        cy.submit(".survey-page__btn>span", "Submit");
    });

    it("Checks for successful redirection", () => {
        cy.url().should(
            "include",
            `/?back_url=${url}`
        );
    });

    it("Checks thanks text", () => {
        cy.thanksText(".polls-widget__form-title", "Poll Thank you text");
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