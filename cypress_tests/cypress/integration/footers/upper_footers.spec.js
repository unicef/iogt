describe("Upper footer tests", () => {
    const url = "/en/"

    it("Test youth page", () => {
        cy.visitUrl(url)
        cy.submit(".top-level>nav>[href=\"/en/sections/youth/\"]", "Youth")
        cy.url().should("include", "/sections/youth/");
    })    

    it("Test Covid-19 page", () => {
        cy.visitUrl(url)
        cy.submit(".top-level>nav>[href=\"/en/sections/covid-19/\"]", "Covid-19")
        cy.url().should("include", "/sections/covid-19/");
    })

    it("Test Parents & Caregivers page", () => {
        cy.visitUrl(url)
        cy.submit(".top-level>nav>[href=\"/en/sections/parents-caregivers/\"]", "Parents & Caregivers")
        cy.url().should("include", "/sections/parents-caregivers/");
    })

    it("Test Front line page", () => {
        cy.visitUrl(url)
        cy.submit(".top-level>nav>[href=\"/en/sections/front-line-workers-educators/\"]", "Front line workers & educators")
        cy.url().should("include", "/sections/front-line-workers-educators/");
    })

    it("Test Questionnaire testing page", () => {
        cy.visitUrl(url)
        cy.submit(".top-level>nav>[href=\"/en/sections/questionnaire-testing/\"]", "Questionnaire testing")
        cy.url().should("include", "/sections/questionnaire-testing/");
    })
})
