describe("2 pages survey tests", () => {

    it("Visits the survey page", () => {
        cy.visit("/en/sections/questionnaire-testing/2-page-survey/");
        cy.url().should(
            "include",
            "/en/sections/questionnaire-testing/2-page-survey/"
        );
    });

    it("Checks for the title text", () => {
        cy.get(".survey-page__title")
            .contains("Survey (2-pages)")
            .should("be.visible");
    });

    it("It checks for the description text", () => {
        cy.get(".survey-page__description>.block-paragraph>p")
            .contains("intro txt")
            .should("be.visible");
    });

    it("Checks for the question numbers", () => {
        cy.get(".quest-item__number").contains("1 of 2 questions");
        cy.get(".quest-item__step-desc>span").contains("Optional");
    })

    it("Checks for first page input types fill the form", () => {
        cy.get("[name=checkbxoes]").each($el => {
            cy.wrap($el).should("have.attr", "type", "checkbox");
        });
        cy.get("[id=id_checkbxoes_0]").check();
    });

    it("Goes to next page", () => {
        cy.get("button")
            .should("have.attr", "type", "submit")
            .contains("Next")
            .click();
    });

    it("Checks for successful redirection", () => {
        cy.url().should(
            "include",
            "/?p=2&back_url=/en/sections/questionnaire-testing/2-page-survey/&form_length=1"
        );
    });

    it("Checks for question no on page 2", () => {
        cy.get(".quest-item__number")
            .contains("2 of 2 questions");
    });

    it("Checks for input field type and fills it", () => {
        cy.get("[name=text_field]")
            .should("have.attr", "type", "text")
            .should("have.attr", "required", "required")
            .type("test");
    });

    it("Submits the form and checks for successful redirection", () => {
        cy.get(".survey-page__btn>span")
            .contains("Submit")
            .should("be.visible")
            .click();

        cy.url().should(
            "include",
            "/?p=3&back_url=/en/sections/questionnaire-testing/2-page-survey/&form_length=1"
        );

        cy.get(".block-paragraph")
            .contains("end txt")
            .should("be.visible");

        cy.get(".survey-page__btn>span")
            .contains("Back")
            .should("be.visible");

    });
});