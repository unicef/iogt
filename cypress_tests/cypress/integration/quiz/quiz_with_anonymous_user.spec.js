describe("Quiz with text fields tests", () => {
    const url = "/en/sections/questionnaire-testing/quiz-with-text-fields/";

    it("Visits the quiz page and checks for the input type", () => {
        cy.visitUrl(url);

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
        cy.get("[name=checkbox]").should("have.attr", "type", "checkbox");
        cy.get("[name=checkboxes]").each($el => {
            cy.wrap($el).should("have.attr", "type", "checkbox");
        });

        cy.submit(".survey-page__btn>span", "Submit");
    });

    it("Fills the form with correct answers", () => {
        cy.get("[name=single_line_text_ans_is_hte_correct_answer]").type("ans");
        cy.get("[name=multi_line_text_ans]").type("ans");
        cy.get("[name=email_field_abcom]").type("a@b.com");
        cy.get("[name=number_0]").type("0");
        cy.get("[name=url_field_wwwidemsinternational]").type("https://www.idems.international.com");
        cy.get("[id=id_pick_a_date_0]").click();
        cy.get("[name=positive_numbers]").type('12');
        cy.get("[id=id_radio_0]").click();
        cy.get("[name=checkbox]").check();
        cy.get("[id=id_checkboxes_0]").check();
    });

    it("Submits the form and check for not allowed multiple submission", () => {
        cy.submit(".survey-page__btn>span", "Submit");
        cy.url().should("include", `/?back_url=${url}&form_length=12`);
        cy.thanksText(".block-paragraph", "thank you text");

        cy.get(".quiz-answer-banner__counter").contains("7 / 12");
        cy.get(".quest-item__status").each($el => {
            cy.wrap($el).contains(/Correct|Incorrect/).should("be.visible");
        });
        cy.submit(".icon-btn__title", "Replay Quiz");
        cy.submit(".survey-page__btn>span", "Submit");
        cy.url().should("include", `/?back_url=${url}&form_length=0`)

    });

});