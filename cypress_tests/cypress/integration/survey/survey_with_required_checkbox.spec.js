describe("Survey with required checkbox tests", () => {

    it("Visits the survey page", () => {
        cy.visit("/en/sections/questionnaire-testing/survey-with-checkbox-req/");
        cy.url().should(
            "include",
            "/en/sections/questionnaire-testing/survey-with-checkbox-req/"
        );
    });

    it("Checks for the title text", () => {
        cy.get(".survey-page__title")
            .contains("Survey with required checkbox")
            .should("be.visible");
    });

    it("It checks for the description text", () => {
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
                .contains(`${index + 1} of ${questionNumbers.length} question`);
        });
    });

    it("Checks for help text", () => {
        cy.get(".quest-item__step-desc span")
            .contains("Check if apply")
            .should("be.visible");
    });

    it("submits unchecked form", () => {
        cy.get(".survey-page__btn>span")
            .contains("Submit")
            .should("be.visible")
            .click();

        cy.url().should(
            "include",
            "/en/sections/questionnaire-testing/survey-with-checkbox-req/"
        );
    });


    it("Checks the checkbox", () => {
        cy.get("[name=checkbox]").check();
    })

    it("Submits the form", () => {
        cy.get(".survey-page__btn>span")
            .contains("Submit")
            .should("be.visible")
            .click();
    });

    it("Checks for successful redirection", () => {
        cy.url().should(
            "include",
            "/?back_url=/en/sections/questionnaire-testing/survey-with-checkbox-req/&form_length=1"
        );

        cy.get(".block-paragraph")
            .contains("thanks")
            .should("be.visible");

        cy.get(".survey-page__btn>span")
            .contains("Back")
            .should("be.visible");
    });

});