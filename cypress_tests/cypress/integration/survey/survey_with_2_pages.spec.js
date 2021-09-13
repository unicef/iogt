describe("2 pages survey tests", () => {
    const url = "/en/sections/questionnaire-testing/2-page-survey/";

    it("Visits the survey page", () => {
        cy.visitUrl(url)
        cy.testTitle("Survey (2-pages)", ".survey-page__title");
        cy.testDescription(
            "intro txt",
            ".survey-page__description>.block-paragraph>p"
        );
        cy.get(".quest-item__number").contains("1 of 2 questions");
        cy.get(".quest-item__step-desc>span").contains("Optional");

        cy.get("[name=checkbxoes]").each($el => {
            cy.wrap($el).should("have.attr", "type", "checkbox");
        });
        cy.get("[id=id_checkbxoes_0]").check();
    });

    it("Goes to next page", () => {
        cy.get("button")
            .should("have.attr", "type", "submit")
            .contains("Next").click();

        cy.url().should(
            "include",
            `/?p=2&back_url=${url}&form_length=1`
        );
        cy.get(".quest-item__number")
            .contains("2 of 2 questions");

        cy.get("[name=text_field]")
            .should("have.attr", "type", "text")
            .should("have.attr", "required", "required")
            .type("test");

        cy.submit(".survey-page__btn>span", "Submit");
        cy.url().should(
            "include",
            `/?p=3&back_url=${url}&form_length=1`
        );

        cy.thanksText(".block-paragraph", "end txt");
        cy.submit(".survey-page__btn>span", "Back")
    });
});
