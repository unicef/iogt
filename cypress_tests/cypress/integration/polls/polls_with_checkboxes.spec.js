describe("Poll with checkboxes test", () => {
    const url = "/en/sections/questionnaire-testing/poll-with-checkboxes/";

    it("Visits poll with checkboxes submits it", () => {
        cy.visitUrl(url);

        cy.get("[name=poll_checkboxes]")
            .each($element => {
                cy.wrap($element).should("be.visible").click()
                cy.get(".quest-item__label")
                    .should("be.visible");
            });

        cy.submit(".survey-page__btn>span", "Submit");
        cy.url().should("include", `/?back_url=${url}`);

        cy.get(".cust-check__percent").each(($el) => {
            cy.wrap($el)
                .should("be.visible")
                .contains(/\\d+(?:d+)?|%/)
        });

        cy.submit(".btn-back__title", "BACK");
        cy.wait(500);
        cy.submit(".survey-page__btn>span", "Submit");
        cy.url().should("include", `/?back_url=${url}`)
    })
});
