describe("Navbar", () => {
    const url = "/en/"

    it("Test items exist in Navbar ", () => {
        cy.visitUrl(url)
        cy.get(".nav-bar").contains("Home")
        cy.get(".nav-bar").contains("Categories")
        cy.get(".nav-bar").contains("Profile")
        cy.get(".nav-bar").contains("Chat")
    })    

})
