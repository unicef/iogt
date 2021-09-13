describe("Polls with radio tests", () => {
    const url = "/en/sections/questionnaire-testing/poll-with-radio";

    it("Visits poll with radio", () => {
        cy.visitUrl(url);
    });

    it("Checks for title text", () => {
        cy.testTitle(
            "Poll with Radio",
            "h1.polls-widget__title"
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
        cy.get("[name=poll_radio]").each($el => {
            if ($el.hasOwnProperty("required")) {
                cy.submit(".polls-page__btn", "Submit");
                cy.url().should("include", url);
            }
        });
    });

    it("Selects the check box for option 1 submission", () => {
        cy.get("[id=id_poll_radio_0]").check();
    });

    it("Submits the poll", () => {
        cy.submit(".survey-page__btn", "Submit");
        cy.url().should(
            "include",
            `/?back_url=${url}`
        );
    })

    it("Checks for thank you text", () => {
        cy.thanksText(".block-paragraph > p", "Thank you.");
    });

    it("Checks the result text", () => {
        cy.get(".cust-check__percent")
            .each(($el) => {
                cy.wrap($el)
                    .should("be.visible")
                    .contains(/\\d+(?:d+)?|%/)
            });
    });
});