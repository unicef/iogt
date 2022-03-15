describe("Tests for embedded completed questionaires", () => {
    const url = "/en/sections/questionnaire-testing/testing-functionality-of-embedded-components/";

    it("Complete questionaires and check for display", () => {
        cy.visitUrl("/en/accounts/login/");
        cy.login("mbilal", "mbilal");
        cy.visitUrl(url);
        cy.get(".questionnaire-container>p").contains("You have already completed this poll.")
        cy.get(".questionnaire-container>p").contains("You have already completed this survey.")
        cy.get(".questionnaire-container>p").contains("You have already completed this quiz.")        
        
    });    
})
