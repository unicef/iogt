describe("Survey with optional checkbox tests", () => {
    const url = "/en/sections/questionnaire-testing/survey-with-checkbox/";

    before("Login", () => {
        cy.login("saqlain", "saqlain");
    })

    it("Visits the survey page", () => {
        cy.visitUrl(url)
        cy.testTitle(
            "Survey with optional checkbox", ".survey-page__title"
        );
        cy.testDescription(
            "intro", ".survey-page__description>.block-paragraph>p"
        );

        let questionNumbers = []
        cy.get(".quest-item__number").each(($el, index) => {
            questionNumbers.push($el)
        });
        cy.get(".quest-item__number").each(($el, index) => {
            cy.wrap($el)
                .should("be.visible")
                .contains(`${index + 1} of ${questionNumbers.length} question`);
        });

        cy.get(".quest-item__step-desc span")
            .contains("Optional")
            .should("be.visible");
    });

    it("Submits the form", () => {
        cy.get("[name=checkbox]").check();
        cy.submit(".survey-page__btn>span", "Submit");
        cy.url().should(
            "include",
            `/?back_url=${url}&form_length=1`
        );
    });
});
