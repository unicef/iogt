describe("Navbar", () => {
    const url = "/en/"

    it("Test items exist in Navbar ", () => {
        cy.visitUrl(url)
        cy.get(".nav-bar__wrap>.btn-primary")
          .contains("Home")
          .should('have.css', 'color')
          .and('equal', 'rgb(255, 255, 255)')
        cy.get(".nav-bar__wrap>.btn-primary")
          .contains("Categories")
          .should('have.css', 'color')
          .and('equal', 'rgb(255, 255, 255)')
        cy.get(".nav-bar__wrap>.btn-primary")
          .contains("Profile")
          .should('have.css', 'color')
          .and('equal', 'rgb(255, 255, 255)')
        cy.get(".nav-bar__wrap>.btn-primary")
          .contains("Chat")
          .should('have.css', 'color')
          .and('equal', 'rgb(255, 255, 255)')
    })
    
    it("Test youth page", () => {
        cy.visitUrl(url)
        cy.get(".top-level>nav>[href=\"/en/sections/youth/\"]")
          .contains("Youth")
          .should('have.css', 'color')
          .and('equal', 'rgb(29, 174, 236)')
        cy.submit(".top-level>nav>[href=\"/en/sections/youth/\"]", "Youth")
        cy.url().should("include", "/sections/youth/");
    })    

    it("Test Covid-19 page", () => {
        cy.visitUrl(url)
        cy.get(".top-level>nav>[href=\"/en/sections/covid-19/\"]")
          .contains("Covid-19")
          .should('have.css', 'color')
          .and('equal', 'rgb(238, 56, 81)')
        cy.submit(".top-level>nav>[href=\"/en/sections/covid-19/\"]", "Covid-19")
        cy.url().should("include", "/sections/covid-19/");
    })

    it("Test Parents & Caregivers page", () => {
        cy.visitUrl(url)
        cy.get(".top-level>nav>[href=\"/en/sections/parents-caregivers/\"]")
          .contains("Parents & Caregivers")
          .should('have.css', 'color')
          .and('equal', 'rgb(139, 92, 214)')
        cy.submit(".top-level>nav>[href=\"/en/sections/parents-caregivers/\"]", "Parents & Caregivers")
        cy.url().should("include", "/sections/parents-caregivers/");
    })

    it("Test Front line page", () => {
        cy.visitUrl(url)
        cy.get(".top-level>nav>[href=\"/en/sections/front-line-workers-educators/\"]")
          .contains("Front line workers & educators")
          .should('have.css', 'color')
          .and('equal', 'rgb(26, 144, 144)')
        cy.submit(".top-level>nav>[href=\"/en/sections/front-line-workers-educators/\"]", "Front line workers & educators")
        cy.url().should("include", "/sections/front-line-workers-educators/");
    })

    it("Test Questionnaire testing page", () => {
        cy.visitUrl(url)
        cy.get(".top-level>nav>[href=\"/en/sections/questionnaire-testing/\"]")
          .contains("Questionnaire testing")
          .should('have.css', 'color')
          .and('equal', 'rgb(120, 96, 112)')
        cy.submit(".top-level>nav>[href=\"/en/sections/questionnaire-testing/\"]", "Questionnaire testing")
        cy.url().should("include", "/sections/questionnaire-testing/");
    })

    it("Test page link page testing", () => {
        cy.visitUrl(url)
        cy.get(".top-level>nav>[href=\"/en/sections/page-in-page-testing/\"]")
          .contains("Page link page testing")
          .should('have.css', 'color')
          .and('equal', 'rgb(68, 68, 68)')
        cy.submit(".top-level>nav>[href=\"/en/sections/page-in-page-testing/\"]", "Page link page testing")
        cy.url().should("include", "/sections/page-in-page-testing/");
    })
})
