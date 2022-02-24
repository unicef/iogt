describe("Page link page article tests", () => {
    const url = "/en/sections/page-in-page-testing/"

    it("Test images and titles", () => {

        cy.visitUrl(url);
        cy.get(".article-card>[href=\"/en/sections/covid-19/where-to-get-vaccinated-in/\"]>div.article-header>p").contains("Where to get vaccinated in?")
        cy.get(".article-card>[href=\"/en/sections/covid-19/where-to-get-vaccinated-in/\"]>div.img-holder>[alt='solid-dark-green.png']")
        cy.get(".article-card>[href=\"/en/sections/covid-19/where-to-get-vaccination/\"]>div.article-header>p").contains("Where to get vaccination?")
        cy.get(".article-card>[href=\"/en/sections/covid-19/where-to-get-vaccination/\"]>div.img-holder>[alt='solid-dark-green.png']")
                
    })

})
