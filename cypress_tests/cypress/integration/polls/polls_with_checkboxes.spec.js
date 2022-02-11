describe.skip("Poll with checkboxes test", () => {
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

        cy.checkPollResults(".cust-check__percent");

        cy.submit(".btn-back__title", "BACK");
        cy.wait(500);
        cy.get(".survey-page__already-completed")
            .contains("You have already completed this survey.").should("be.visible");

        cy.checkPollResults(".cust-check__percent");

        cy.url().should("include", url)
    })
});
