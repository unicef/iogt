describe("Survey with text field tests", () => {

    it("Visits the survey page", () => {
        cy.visit("/en/sections/questionnaire-testing/survey-with-text-fields/");
        cy.url().should(
            "include",
            "/en/sections/questionnaire-testing/survey-with-text-fields/"
        );
    });

    it("Checks for the title text", () => {
        cy.get(".survey-page__title")
            .contains("Survey with text fields")
            .should("be.visible");
    });

    it("It checks for the description test", () => {
        cy.get(".survey-page__description>.block-paragraph>p")
            .contains("intro")
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

    it("Checks for input tag visibility", () => {
        cy.get("[name=single]").should("be.visible");
        cy.get("[name=multiline]").should("be.visible");
        cy.get("[name=email]").should("be.visible");
        cy.get("[name=url]").should("be.visible");
        cy.get("[name=date]").should("be.visible");
        cy.get("[name=datetime]").should("be.visible");
        cy.get("[name=hidden]").should("not.be.visible");
        cy.get("[name=nume]").should("be.visible");
        cy.get("[name=positive_num]").should("be.visible");
    });

    it("Fills the forum", () => {
        cy.get("[name=single]").type("saqlain");
        cy.get("[name=multiline]").type("this is multiline text");
        cy.get("[name=email]").type("abc@xyz.com");
        cy.get("[name=url]").type("http://localhost:8000");
        cy.get("[name=date]").type("2021-09-09")
        cy.get("[name=hidden]");
        cy.get("[name=nume]").type("1234556");
        cy.get("[name=positive_num]").type("2020909");
    });

    it("Submits the form", () => {
        cy.get(".survey-page__btn>span")
            .contains("Submit")
            .should("be.visible")
            .click();
    });

    it("Checks for successful redirection", () => {
        cy.url().should(
            "include",
            "/?back_url=/en/sections/questionnaire-testing/survey-with-text-fields/&form_length=9"
        );

        cy.get(".block-paragraph")
            .contains("thank you")
            .should("be.visible");

        cy.get(".survey-page__btn>span")
            .contains("Back")
            .should("be.visible");
    });

});