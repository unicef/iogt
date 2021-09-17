describe("Survey skip logic tests", () => {
    const url = "/en/sections/questionnaire-testing/multi-page-survey-with-skip-logic/";

    it("Visits the survey and check for 'survey end' logic", () => {
        cy.visitUrl(url);
        cy.get(".quest-item__number").contains("1 of 5 questions");
        cy.get(".quest-item__desc").contains("radio_1");
        cy.get("[id=id_radio_0]").check();
        cy.submit(".survey-page__btn>span", "Next");
        cy.url().should("include", `/?p=2&back_url=${url}&form_length=1`);

        it.skip("Bug in question numbering", () => {
            cy.get(".quest-item__number").contains("4 of 5 questions");
        });

        cy.get(".quest-item__desc").contains("single_line_4");
        cy.get("[name=single_line]").type("hello");
        cy.submit(".survey-page__btn>span", "Next");
        cy.submit(".survey-page__btn>span", "Back");
    });

    it("It checks for the survey 'next default question' ", () => {
        cy.get("[id=id_radio_1]").check();
        cy.submit(".survey-page__btn>span", "Next");
        cy.url().should("include", `/?p=2&back_url=${url}&form_length=1`);
        cy.get(".quest-item__number").contains("2 of 5 questions");
        cy.get("[name=checkbox]").check();
        cy.submit(".survey-page__btn>span", "Next");
        cy.get("[id=id_checkboxes_0]").check();

        it.skip("Skips bug question numbering bug",() => {
            cy.get(".quest-item__number").contains("3 of 5 questions");
        });

        cy.get(".quest-item__desc").contains("checkboxes_3");
        cy.submit(".survey-page__btn>span", "Next");
        cy.get("[name=single_line]").type("test");
        cy.submit(".survey-page__btn>span", "Next");
        cy.get("[name=multiline]").type("test");

        it.skip("Skips question numbering but",() => {
            cy.get(".quest-item__number").contains("5 of 5 questions");
        });

        cy.get(".quest-item__desc").contains("multiline_5");
        cy.submit(".survey-page__btn>span", "Submit");
        cy.submit(".survey-page__btn>span", "Back");
    });

    it("It checks for the 'another question logic'", () => {
        cy.get("[id=id_radio_2]").check();
        cy.submit(".survey-page__btn>span", "Next");
        cy.url().should("include", `/?p=2&back_url=${url}&form_length=1`);

        it.skip("Skips the question numbering bug", () => {
              cy.get(".quest-item__number").contains("3 of 5 questions");
        });

        cy.get(".quest-item__desc").contains("checkboxes_3");
        cy.get("[id=id_checkboxes_2]").check();
        cy.submit(".survey-page__btn>span", "Next");
        cy.get("[name=single_line]").type("hello");
        cy.submit(".survey-page__btn>span", "Next");
    });
});
