describe("Section questionnaires tests", () => {
    const url = "/en/sections/covid-19/"

    it("Test for questionnaire survey in section", () => {
        cy.visitUrl(url);
        cy.get(".child-pages>:nth-child(5) a div :nth-child(1)")
            .contains("SURVEY")
        cy.get(".child-pages>:nth-child(5) a div :nth-child(2)")
            .contains("Early Life Tips quick survey")
    })

    it("Test for questionnaire quiz in section", () => {
        cy.get(".child-pages>:nth-child(6) a div :nth-child(1)")
            .contains("QUIZ")
        cy.get(".child-pages>:nth-child(6) a div :nth-child(2)")
            .contains("Take the Corona-Quiz")
    })

    it("Test for questionnaire poll in section", () => {
        cy.get(".child-pages>:nth-child(7) a div :nth-child(1)")
            .contains("POLL")
        cy.get(".child-pages>:nth-child(7) a div :nth-child(2)")
            .contains("How concerned are you about Coronavirus?")
    })
})
