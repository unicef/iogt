describe("2 pages survey tests", () => {
    const url = "/en/sections/questionnaire-testing/2-page-survey/";

    it("Visits the survey page", () => {
        cy.visitUrl(url)
        cy.get("[name=text_field]")
            .should("have.attr", "type", "text")
            .should("have.attr", "required", "required")
            .type("test");
    });

    it.skip("Goes to next page", () => {
        cy.submit("button", "Next");
        cy.url().should("include", `/?p=2&back_url=${url}&form_length=1`);
        cy.get("[name=checkboxes]").each($el => {
            cy.wrap($el).should("have.attr", "type", "checkbox");
        });
        cy.get("[id=id_checkboxes_0]").check();
        cy.submit(".survey-page__btn>span", "Submit");
        cy.url().should("include", `/?p=3&back_url=${url}&form_length=1`);

        cy.submit(".survey-page__btn>span", "Back")
    });
});
