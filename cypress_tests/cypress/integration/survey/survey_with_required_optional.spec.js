describe("Survey with required and optional", () => {
    const url = "/en/sections/questionnaire-testing/survey-with-requiredoptional/";

    it("Visits the survey page", () => {
        cy.visitUrl(url);
    });

    it("Checks for the title text", () => {
        cy.testTitle("Survey with required/optional", ".survey-page__title");
    });

    it("It checks for the description text", () => {
        cy.testDescription(
            "intro text",
            ".survey-page__description>.block-paragraph>p"
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
    });

    it("Fills out the required fields", () => {
        cy.get("[name=text_required]").type("test");
        cy.get("[id=id_radio_required_0]").click();
        cy.get("[id=id_checkboxes_reqired_0]").check();
        cy.get("[name=dropdown_required]").select("d1");
    });

    it("Submits the form", () => {
        cy.submit(".survey-page__btn>span","Submit");
    });

    it("Checks for successful redirection", () => {
        cy.url().should(
            "include",
            `/?back_url=${url}&form_length=8`
        );

        cy.thanksText(".block-paragraph", "thanks");
        cy.submit(".survey-page__btn>span", "Back");
    });

});