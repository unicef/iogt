describe("Articles components tests", () => {
    const url = "/en/sections/covid-19/"

    it("Test for questionnaire poll in section", () => {
        cy.visitUrl(url);
        cy.get(".questionnaire-components > :nth-child(1)").should("have.css", "color", "rgb(238, 56, 81)")
        cy.get(".questionnaire-components > :nth-child(1)").should("have.css", "background-color", "rgb(253, 235, 238)")
        cy.get(":nth-child(1) > a > .quiz__details > :nth-child(2)")
            .contains("How concerned are you about Coronavirus?")
    })

    it("Test for questionnaire survey in section", () => {
        cy.get(".questionnaire-components > :nth-child(2)").should("have.css", "color", "rgb(238, 56, 81)")
        cy.get(".questionnaire-components > :nth-child(2)").should("have.css", "background-color", "rgb(253, 235, 238)")
        cy.get(":nth-child(2) > a > .quiz__details > :nth-child(2)")
            .contains("Early Life Tips quick survey")
    })

    it("Test for questionnaire quiz in section", () => {
        cy.get(".questionnaire-components > :nth-child(3)").should("have.css", "color", "rgb(238, 56, 81)")
        cy.get(".questionnaire-components > :nth-child(3)").should("have.css", "background-color", "rgb(253, 235, 238)")
        cy.get(":nth-child(3) > a > .quiz__details > :nth-child(2)")
            .contains("Take the Corona-Quiz")
    })
})
