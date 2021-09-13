describe("Survey with text field tests", () => {
    const url = "/en/sections/questionnaire-testing/survey-with-text-fields/";

    it("Visits the survey page", () => {
        cy.visitUrl(url);
        cy.testTitle("Survey with text fields", ".survey-page__title");
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
        cy.submit(".survey-page__btn>span", "Submit");
        cy.url().should(
            "include",
            `/?back_url=${url}&form_length=9`
        );
        cy.thanksText(".block-paragraph", "thank you");
        cy.submit(".survey-page__btn>span", "Back");
    });
});
