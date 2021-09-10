describe("Survey with multiple options tests", () => {

    it("Visits the survey page", () => {
        cy.visit("/en/sections/questionnaire-testing/sample-survey/");
        cy.url().should("include", "/en/sections/questionnaire-testing/sample-survey/");
    });

    it("Checks for the title text", () => {
        cy.get(".survey-page__title")
            .contains("Survey with multiple choice options")
            .should("be.visible");
    });

    it("It checks for the description test", () => {
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
                .contains(`${index + 1} of ${questionNumbers.length} questions`)
        });
    });

    it("Checks for the input types", () => {
        cy.get("[name=number_field_required]").each($el => {
            cy.wrap($el)
                .should("have.attr", "type", "checkbox")
                .should("be.visible");
        });

        cy.get("[type=radio]").each($el => {
            cy.wrap($el).should("be.visible");
        });
    });

    it("Selects the answers", () => {
        cy.get("[id=id_number_field_required_0]").click();
        cy.get("[id=id_dropdown_field_0]").check();
    });

    it("Submits the answers", () => {
        cy.get(".survey-page__btn>span")
            .contains("Submit")
            .should("be.visible")
            .click();
    });

    it("Checks for successful redirection", () => {
        cy.url()
            .should("include", "/?back_url=/en/sections/questionnaire-testing/sample-survey/&form_length=3");

        cy.get(".block-paragraph")
            .contains("thanks text")
            .should("be.visible");

        cy.get(".survey-page__btn>span")
            .contains("Back")
            .should("be.visible");
    });
});