describe("Survey with optional checkbox tests", () => {
    const url = "/en/sections/questionnaire-testing/survey-with-checkbox/";

    it("Checks for the login button and logs in the user", () => {
        cy.visitUrl(url);
        cy.submit(".survey-page__btn", "Log in to participate");
        cy.login("saqlain", "saqlain");
    });

    it("Visits the survey page", () => {
        cy.get(".quest-item__step-desc span")
            .contains("Optional")
            .should("be.visible");
    });

    it("Submits the form", () => {
        cy.get("[name=checkbox]").check();
        cy.submit(".survey-page__btn>span", "Submit");
        cy.url().should("include", `/?back_url=${url}&form_length=1`);
    });
});
