describe("Survey skip logic tests", () => {
    const url = "/en/sections/questionnaire-testing/multi-page-survey-with-skip-logic/";

    it("Visits the survey and check for 'survey end' logic", () => {
        cy.visitUrl(url);
        cy.get("[id=id_radio_0]").check();
        cy.submit(".survey-page__btn>span", "Next");
        cy.url().should("include", `/?p=2&back_url=${url}&form_length=1`);
        cy.get("[name=single_line]").type("hello");
        cy.submit(".survey-page__btn>span", "Next");
        cy.submit(".survey-page__btn>span", "Back");
    });

    it("It checks for the survey 'next default question' ", () => {
        cy.get("[id=id_radio_1]").check();
        cy.submit(".survey-page__btn>span", "Next");
        cy.url().should("include", `/?p=2&back_url=${url}&form_length=1`);
        cy.get("[name=checkbox]").check();
        cy.submit(".survey-page__btn>span", "Next");
        cy.get("[id=id_checkboxes_0]").check();
        cy.submit(".survey-page__btn>span", "Next");
        cy.get("[name=single_line]").type("test");
        cy.submit(".survey-page__btn>span", "Next");
        cy.get("[name=multiline]").type("test");
        cy.submit(".survey-page__btn>span", "Submit");
        cy.submit(".survey-page__btn>span", "Back");
    });

    it("It checks for the 'another question logic'", () => {
        cy.get("[id=id_radio_2]").check();
        cy.submit(".survey-page__btn>span", "Next");
        cy.url().should("include", `/?p=2&back_url=${url}&form_length=1`);
        cy.get("[id=id_checkboxes_2]").check();
        cy.submit(".survey-page__btn>span", "Next");
        cy.get("[name=single_line]").type("hello");
        cy.submit(".survey-page__btn>span", "Next");
    });
});
