describe("Quiz with text fields tests", () => {
    const url = "/en/sections/questionnaire-testing/quiz-with-text-fields/";

    it("Visits the quiz page", () => {
        cy.visitUrl(url);
        cy.testTitle("Quiz with text fields", ".quiz-page__title");
        cy.testDescription(
            "intro text",
            ".quiz-page__description>.block-paragraph>p"
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
        cy.get("[name=pick_a_date]").should("have.attr", "type", "radio");
        cy.get("[name=positive_numbers]").should("have.attr", "type", "number");
        cy.get("[name=date]").should("have.attr", "type", "date");
        cy.get("[name=date_time]").should("have.attr", "type", "datetime-local");
        cy.get("[name=radio]").should("have.attr", "type", "radio");
    });

    it("Fills the forum with correct answers", () => {
        cy.get("[name=single_line_text_ans_is_hte_correct_answer]").type("ans");
        cy.get("[name=multi_line_text_ans]").type("ans");
        cy.get("[name=email_field_abcom]").type("a@b.com");
        cy.get("[name=number_0]").type("0");
        cy.get("[name=url_field_wwwidemsinternational]").type("https://www.idems.international.com");
        cy.get("[id=id_pick_a_date_0]").click();
        cy.get("[name=positive_numbers]").type('12');
        cy.get("[id=id_radio_0]").click();
    });

    it("Submits the forum", () => {
        cy.submit(".survey-page__btn>span", "Submit");
        cy.url().should("include", `/?back_url=${url}&form_length=10`);
        cy.thanksText(".block-paragraph", "thank you text");

        cy.get(".quiz-answer-banner__counter").contains("7 / 10");
        cy.get(".quest-item__status").each($el => {
            cy.wrap($el).contains(/Correct|Incorrect/).should("be.visible");
        });
    });
});
