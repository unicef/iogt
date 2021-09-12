describe("2 pages quizes tests", () => {

    it("Visits the quiz page", () => {
        cy.visit("/en/sections/questionnaire-testing/quiz-2-pages/");
        cy.url().should(
            "include",
            "/en/sections/questionnaire-testing/quiz-2-pages/"
        );
    });

    it("Checks for title, and description", () => {
        cy.get(".quiz-page__title")
            .contains("Quiz (2 pages)")
            .should("be.visible");

        cy.get(".quiz-page__description>.block-paragraph>p")
            .contains("intro")
            .should("be.visible");
    })

    it("Checks for first page question number and help text", () => {
        cy.get(".quest-item__number").contains("1 of 2 questions");
        cy.get(".quest-item__step-desc>span").contains("Select one");
    });

    it("Submits empty field which is required", () => {
        cy.get("button[type=submit]>span").contains("Next").click();
        cy.url().should("include", "/en/sections/questionnaire-testing/quiz-2-pages/");
    });

    it("Select the wrong answer and go to next page", () => {
        cy.pause();
        cy.get("#id_q1_c1_ends_the_quiz_c2_is_correct_0").click();
        cy.get("button[type=submit]>span").contains("Next").click();
        cy.url().should(
            "include",
            "/?p=2&back_url=/en/sections/questionnaire-testing/quiz-2-pages/&form_length=1"
        );
    });

    it("Checks for 2nd page question no and help text", () => {
        cy.get(".quest-item__number").contains("2 of 2 questions");
        cy.get(".quest-item__step-desc>span").contains("Select one");
    });

    it("Selects correct option and submits", () => {
        cy.get("[name=q2_c2_is_correct]").select("c2");
        cy.get("button[type=submit]>span").contains("Submit").click();
        cy.url().should(
            "include",
            "/?p=3&back_url=/en/sections/questionnaire-testing/quiz-2-pages/&form_length=1"
        )
    });

    it("Checks for the expected result", () => {
        cy.get(".quiz-answer-banner__counter").contains("1 / 2");
    });
});