describe("Quiz with text fields tests", () => {

    it("Visits the quiz page", () => {
        cy.visit("/en/sections/questionnaire-testing/quiz-with-text-fields/");
        cy.url().should(
            "include",
            "/en/sections/questionnaire-testing/quiz-with-text-fields/"
        );
    });

    it("Checks for the title text", () => {
        cy.get(".quiz-page__title")
            .contains("Quiz with text fields")
            .should("be.visible");
    });

    it("It checks for the description text", () => {
        cy.get(".quiz-page__description>.block-paragraph>p")
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

    it("Checks for all the help text", () => {
        cy.get(".quest-item__step-desc").each($el => {
            cy.wrap($el).contains("Optional");
        });
    });

    it("Checks for the different input types", () => {
        cy.get("[name=single_line_text_ans_is_hte_correct_answer]")
            .should("have.attr", "type", "text");
        cy.get("[name=multi_line_text_ans]").should("be.visible");
        cy.get("[name=email_field_abcom]").should("have.attr", "type", "email");
        cy.get("[name=number_0]").should("have.attr", "type", "number");
        cy.get("[name=url_field_wwwidemsinternational]").should("have.attr", "type", "url");
    });

    it("Fills the forum with correct answers", () => {
        cy.get("[name=single_line_text_ans_is_hte_correct_answer]").type("ans");
        cy.get("[name=multi_line_text_ans]").type("ans");
        cy.get("[name=email_field_abcom]").type("a@b.com");
        cy.get("[name=number_0]").type("0");
        cy.get("[name=url_field_wwwidemsinternational]").type("https://www.idems.international.com");
    });

    it("Submits the forum", () => {
        cy.get(".survey-page__btn>span")
            .contains("Submit")
            .should("be.visible")
            .click();
    });

    it("Checks for successful redirection", () => {
        cy.url().should(
                "include",
                "/?back_url=/en/sections/questionnaire-testing/quiz-with-text-fields/&form_length=5"
            );

        cy.get(".block-paragraph")
            .contains("thank you text")
            .should("be.visible");
    });

    it("Checks for the correct answers", () => {
        cy.get(".quiz-answer-banner__counter").contains("5 / 5");
        cy.get(".quest-item__status").each($el => {
            cy.wrap($el).contains("Correct").should("be.visible");
        })
    });

});