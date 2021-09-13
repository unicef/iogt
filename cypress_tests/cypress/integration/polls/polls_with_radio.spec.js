describe("Polls with radio tests", () => {
    const url = "/en/sections/questionnaire-testing/poll-with-radio";

    it("Visits poll with radio", () => {
        cy.visitUrl(url);
        cy.testTitle("Poll with Radio", "h1.polls-widget__title");
        cy.testDescription("Make your choice.", ".polls-widget__description>div>p");
        cy.get(".quest-item__header .quest-item__number")
            .contains("1 of 1 question")
            .should("be.visible");
    });

    it("Checks for empty submission", () => {
        cy.get("[name=poll_radio]").each($el => {
            if ($el.hasOwnProperty("required")) {
                cy.submit(".polls-page__btn", "Submit");
                cy.url().should("include", url);
            }
        });
    });

    it("Selects the radio for option 1 submission", () => {
        cy.get("[id=id_poll_radio_0]").click();

        cy.submit(".survey-page__btn", "Submit");
        cy.url().should("include", `/?back_url=${url}`);

        cy.thanksText(".block-paragraph > p", "Thank you.");
        cy.get(".cust-check__percent")
            .each(($el) => {
                cy.wrap($el)
                    .should("be.visible")
                    .contains(/\\d+(?:d+)?|%/)
            });
    });
});
