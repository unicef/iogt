describe("Survey with text field tests", () => {
    const url = "/en/sections/questionnaire-testing/survey-with-text-fields/";

    it("Visits the survey page", () => {
        cy.visitUrl(url);
        cy.wait(500);

        cy.get("[name=single]").should("have.attr", "type", "text");
        cy.get("[name=multiline]").should("be.visible",);
        cy.get("[name=email]").should("have.attr", "type", "email");
        cy.get("[name=url]").should("have.attr", "type", "url");
        cy.get("[name=date]").should("have.attr", "type", "date");
        cy.get("[name=datetime]").should("have.attr", "type", "datetime-local");
        cy.get("[name=number]").should("have.attr", "type", "number");
        cy.get("[name=positive_number]").should("have.attr", "type", "number");
        cy.get("[name=radio]").should("have.attr", "type", "radio");
        cy.get("[name=checkbox]").should("have.attr", "type", "checkbox");
        cy.get("[name=checkboxes]").each($el => {
            cy.wrap($el).should("have.attr", "type", "checkbox");
        });
        cy.get("[name=dropdown]").should("be.visible");
    });

    it("Fills the form  and submits it", () => {
        cy.get("[name=single]").type("example text");
        cy.get("[name=multiline]").type("this is multiline text");
        cy.get("[name=email]").type("abc@xyz.com");
        cy.get("[name=url]").type("http://localhost:8000");
        cy.get("[name=date]").type("2021-09-09");
        cy.get("[name=number]").type("1234556");
        cy.get("[name=positive_number]").type("2020909");
        cy.get("[name=checkbox]").check();
        cy.get("[id=id_checkboxes_0]").check();
        cy.get("[name=dropdown]").select("c1");

        cy.submit(".survey-page__btn>span", "Submit");
        cy.url().should("include", `/?back_url=${url}&form_length=12`);

        cy.submit(".survey-page__btn>span", "Back");
        cy.wait(500);
        cy.get(".survey-page__already-completed").contains('You have already completed this survey.').should("be.visible")
        cy.url().should("include", url);
    });
});
