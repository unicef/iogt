describe("Related articles tests in section", () => {
    const url = "/en/sections/covid-19/"

    it("Test for related article 'Where to get vaccinated in?'", () => {
        cy.visitUrl(url);
        cy.get("[href=\"/en/sections/covid-19/where-to-get-vaccinated-in/\"] p").contains("Where to get vaccinated in?")
        cy.get("[href=\"/en/sections/covid-19/where-to-get-vaccinated-in/\"] .img-holder img").should("be.visible")
            .and(($img) => {
            expect($img[0].naturalWidth).to.be.greaterThan(0)
        });
    })

    it("Test for related article 'How to encourage friends for vaccination?'", () => {
        cy.get("[href=\"/en/sections/covid-19/encourage-vaccination/\"] p").contains("How to encourage friends for vaccination?")
        cy.get("[href=\"/en/sections/covid-19/encourage-vaccination/\"] .img-holder img").should("be.visible")
            .and(($img) => {
            expect($img[0].naturalWidth).to.be.greaterThan(0)
        });
    })

    it("Test for related article 'Where to get vaccination?'", () => {
        cy.get("[href=\"/en/sections/covid-19/where-to-get-vaccination/\"] p").contains("Where to get vaccination?")
        cy.get("[href=\"/en/sections/covid-19/where-to-get-vaccination/\"] .img-holder img").should("be.visible")
            .and(($img) => {
            expect($img[0].naturalWidth).to.be.greaterThan(0)
        });
    })

    it("Test for related article 'Odd story'", () => {
        cy.get("[href=\"/en/sections/covid-19/odd-story/\"] p").contains("Odd story")
        cy.get("[href=\"/en/sections/covid-19/odd-story/\"] .img-holder img").should("be.visible")
            .and(($img) => {
            expect($img[0].naturalWidth).to.be.greaterThan(0)
        });
    })
})
