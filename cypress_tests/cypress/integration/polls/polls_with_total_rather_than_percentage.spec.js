describe("Polls with total rather than percentage tests", () => {
    it("Visits the polls page", () => {
        cy.visit("/en/sections/questionnaire-testing/poll-with-results-as-totals-rather-than-percentage/");
        cy.url().should(
            "include",
            "/en/sections/questionnaire-testing/poll-with-results-as-totals-rather-than-percentage/"
        );
    });

    it("Checks for title text", () => {
        cy.get("h1.polls-widget__title")
            .contains("Poll with results as totals rather than percentage")
            .should("be.visible");
    });

    it("Checks for description text", () => {
        cy.get(".polls-widget__description>div>p")
            .contains("Make your choice.")
            .should("be.visible");
    });

    it("Checks for the questions number", () => {
        cy.get(".quest-item__header .quest-item__number")
            .contains("1 of 1 question")
            .should("be.visible");
    });

    it("Submits the poll", () => {
        cy.get(".survey-page__btn")
            .contains("Submit")
            .should("be.visible")
            .click();

        cy.url().should(
            "include",
            "/?back_url=/en/sections/questionnaire-testing/poll-with-results-as-totals-rather-than-percentage/"
        );
    });

    it("Checks for thank you text", () => {
        cy.get(".block-paragraph > p")
            .contains("thanks")
            .should("be.visible");
    });

    it("Checks the result text", () => {
        cy.get(".cust-check__percent")
            .each(($el) => {
                cy.wrap($el)
                    .should("be.visible")
                    .contains(/^[0-9]*$/)
            });
    });


});