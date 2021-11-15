describe("2 pages quizes tests", () => {
    const url = "/en/sections/questionnaire-testing/quiz-2-pages/";

    it("Visits the quiz page", () => {
        cy.visitUrl(url);
        cy.testTitle("Quiz (2 pages)", ".quiz-page__title");
        cy.get(".quest-item__step-desc>span").contains("Select one");
    });

    it("Submits empty field which is required", () => {
        cy.get("button[type=submit]>span").contains("Next").click();
        cy.url().should("include", url);
    });

    it("Select the wrong answer and go to next page", () => {
        cy.get(".quest-item__content #id_q1_c1_ends_the_quiz_c2_is_correct_0").click();
        cy.get("button[type=submit]>span").contains("Next").click();
        cy.url().should("include", `/?p=2&back_url=${url}&form_length=1`);
        cy.get(".quest-item__step-desc>span").contains("Select one");

        cy.get("[name=q2_c2_is_correct]").select("c2");

        cy.submit("button[type=submit]>span", "Submit");
        cy.url().should(
            "include",
            `/?p=3&back_url=${url}&form_length=1`
        );

        cy.get(".quiz-answer-banner__counter").contains("1 / 2");
    });
});
