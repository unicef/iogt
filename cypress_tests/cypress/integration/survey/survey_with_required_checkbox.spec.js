describe("Survey with required checkbox tests", () => {
    const url = "/en/sections/questionnaire-testing/survey-with-checkbox-req/";

    it("Visits the survey page", () => {
        cy.visitUrl(url);
        cy.testTitle(
            "Survey with required checkbox", ".survey-page__title"
        );
        cy.testDescription(
            "intro", ".survey-page__description>.block-paragraph>p"
        );

        let questionNumbers = []
        cy.get(".quest-item__number").each(($el) => {
            questionNumbers.push($el)
        });
        cy.get(".quest-item__number").each(($el, index) => {
            cy.wrap($el)
                .should("be.visible")
                .contains(`${index + 1} of ${questionNumbers.length} question`);
        });

        cy.get(".quest-item__step-desc span")
            .contains("Check if apply")
            .should("be.visible");
    });

    it("submits unchecked form", () => {
        cy.get(".survey-page__btn>span")
            .contains("Submit")
            .should("be.visible")
            .click();
        cy.url().should("include", url);
    });


    it("Fills the form and submits it", () => {
        cy.get("[name=checkbox]").check();
        cy.submit(".survey-page__btn>span", "Submit");
        cy.url().should(
            "include",
            `/?back_url=${url}&form_length=1`
        );

        cy.thanksText(".block-paragraph", "thanks");
        cy.submit(".survey-page__btn>span", "Back");
    });
});
