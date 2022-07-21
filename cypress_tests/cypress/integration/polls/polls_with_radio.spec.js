describe("Polls with radio tests", () => {
    const url = "/en/sections/questionnaire-testing/poll-with-radio/";

    it("Visits poll with radio", () => {
        cy.visitUrl(url);

        cy.get("[name=poll_radio]").each($el => {
            if ($el.hasOwnProperty("required")) {
                cy.submit(".polls-page__btn", "Submit");
                cy.url().should("include", url);
            }
        });
    });

    it("Selects the radio for option 1 and submits it", () => {
        cy.get("[id=id_poll_radio_0]").click();

        cy.submit(".survey-page__btn", "Submit");
        cy.url().should("include", `/?back_url=${url}`);

        cy.get(".cust-check__percent")
            .each(($el) => {
                cy.wrap($el)
                    .should("be.visible")
                    .contains(/\\d+(?:d+)?|%/)
            });
    });

    it("Checks for multiple allowed submission", () => {
        cy.submit(".icon-btn__title", "Back");
        cy.get("[id=id_poll_radio_1]").click();
        cy.submit(".survey-page__btn", "Submit");
    })
});
