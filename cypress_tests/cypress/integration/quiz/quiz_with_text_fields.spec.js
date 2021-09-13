describe("Quiz with text fields tests", () => {
    const url = "/en/sections/questionnaire-testing/quiz-with-text-fields/";

    it("Visits the quiz page", () => {
        cy.visitUrl(url);
    });

    it("Checks for the title text", () => {
        cy.testTitle(
            "Quiz with text fields",
            ".quiz-page__title"
        );
    });

    it("It checks for the description text", () => {
        cy.testDescription(
            "intro text",
            ".quiz-page__description>.block-paragraph>p"
        );
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
        cy.submit(".survey-page__btn>span", "Submit");
    });

    it("Checks for successful redirection", () => {
        cy.url().should(
            "include",
            `/?back_url=${url}&form_length=5`
        );

        cy.thanksText(".block-paragraph", "thank you text");
    });

    it("Checks for the correct answers", () => {
        cy.get(".quiz-answer-banner__counter").contains("5 / 5");
        cy.get(".quest-item__status").each($el => {
            cy.wrap($el).contains("Correct").should("be.visible");
        })
    });

});