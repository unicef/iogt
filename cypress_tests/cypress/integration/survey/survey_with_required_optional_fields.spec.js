describe("Survey with required and optional fields", () => {
    const url = "/en/sections/questionnaire-testing/survey-with-requiredoptional/";

    it("Visits the survey page", () => {
        cy.visitUrl(url);
        cy.testTitle("Survey with required/optional", ".survey-page__title");
        cy.testDescription(
            "intro text", ".survey-page__description>.block-paragraph>p"
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
    });

    it("submits empty form", () => {
        cy.submit(".survey-page__btn>span", "Submit");
        cy.url().should("include", url);
    });

    it("Checks for the input types and fills them", () => {
        cy.get("[name=text_required]").should("have.attr", "required");
        cy.get("[name=text_optional]").should("not.have.attr", "required");
        cy.get("[name=radio_required]").each($el => {
            cy.wrap($el).should("have.attr", "required")
        });
        cy.get("[name=radio_optional]").each($el => {
            cy.wrap($el).should("not.have.attr", "required")
        });
        cy.get("[name=checkboxes_optional]").each($el => {
            cy.wrap($el).should("not.have.attr", "required")
        });
        cy.get("[name=dropdown_required]").each($el => {
            cy.wrap($el).should("not.have.attr", "required")
        });
        cy.get("[name=dropdown_optional]").each($el => {
            cy.wrap($el).should("not.have.attr", "required")
        });
        cy.get("[name=date]").should("have.attr", "type", "date");
        cy.get("[name=date_time]").should("have.attr", "type", "datetime-local");
    });

    it("Fills out the required fields", () => {
        cy.get("[name=text_required]").type("test");
        cy.get("[id=id_radio_required_0]").click();
        cy.get("[id=id_checkboxes_reqired_0]").check();
        cy.get("[name=dropdown_required]").select("d1");
    });

    it("Submits the form", () => {
        cy.submit(".survey-page__btn>span", "Submit");
        cy.url().should(
            "include",
            `/?back_url=${url}&form_length=10`
        );
        cy.thanksText(".block-paragraph", "thanks");
        cy.submit(".survey-page__btn>span", "Back");
    });

});
