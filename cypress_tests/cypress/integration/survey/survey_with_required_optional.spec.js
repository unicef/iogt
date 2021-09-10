describe("Survey with required and optional", () => {

    it("Visits the survey page", () => {
        cy.visit("/en/sections/questionnaire-testing/survey-with-requiredoptional/");
        cy.url().should("include", "/en/sections/questionnaire-testing/survey-with-requiredoptional/")
    });

    it("Checks for the title text", () => {
        cy.get(".survey-page__title")
            .contains("Survey with required/optional")
            .should("be.visible");
    });

    it("It checks for the description text", () => {
        cy.get(".survey-page__description>.block-paragraph>p")
            .contains("intro text")
            .should("be.visible");
    });

    it("Checks for the question number text", () => {
        let questionNumbers = []
        cy.get(".quest-item__number").each(($el, index) => {
            questionNumbers.push($el)
        });
        cy.get(".quest-item__number").each(($el, index) => {
            cy.wrap($el)
                .should("be.visible")
                .contains(`${index + 1} of ${questionNumbers.length} question`);
        });
    });

    it("submits empty form", () => {
        cy.get(".survey-page__btn>span")
            .contains("Submit")
            .should("be.visible")
            .click();

        cy.url().should("include", "/en/sections/questionnaire-testing/survey-with-requiredoptional/")
    });

    it("Checks for the input types and fills them", () => {
        cy.get("[name=text_required]").should("have.attr", "required");

        cy.get("[name=text_optional]").should("not.have.attr", "required");

        cy.get("[name=radio_required]").each($el => {
            cy.wrap($el).should("have.attr", "required")
        });

        cy.get("[name=radio_optional]").each($el => {
            cy.wrap($el).should("not.have.attr", "required")
        });

        cy.get("[name=checkboxes_optional]").each($el => {
            cy.wrap($el).should("not.have.attr", "required")
        });

        cy.get("[name=dropdown_required]").each($el => {
            cy.wrap($el).should("not.have.attr", "required")
        });

        cy.get("[name=dropdown_optional]").each($el => {
            cy.wrap($el).should("not.have.attr", "required")
        });
    });

    it("Fills out the required fields", () => {
        cy.get("[name=text_required]").type("test");
        cy.get("[id=id_radio_required_0]").click();
        cy.get("[id=id_checkboxes_reqired_0]").check();
        cy.get("[name=dropdown_required]").select("d1");
    });

    it("Submits the form", () => {
        cy.get(".survey-page__btn>span")
            .contains("Submit")
            .should("be.visible")
            .click();
    });

    it("Checks for successful redirection", () => {
        cy.url()
            .should("include", "/?back_url=/en/sections/questionnaire-testing/survey-with-requiredoptional/&form_length=8");

        cy.get(".block-paragraph")
            .contains("thanks")
            .should("be.visible");

        cy.get(".survey-page__btn>span")
            .contains("Back")
            .should("be.visible");
    });

});