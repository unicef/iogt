describe("Tests for chat bots in articles", () => {
    const url = "/en/sections/covid-19/odd-story/";

    it("Test chat bot with logged in user", () => {
        cy.visitUrl("/en/accounts/login/");
        cy.login("mbilal", "mbilal");
        cy.visitUrl(url);
        cy.get("#content-wrap > div.main-wrapper > div > div.content > article > section > div.block-chat_bot > div > form > button").click({force: true})
        cy.url().should("include", "/en/messaging/message/");
    });


    it("Test chat bot with anonymous user", () => {
        cy.visitUrl(url);
        cy.get("div.block-chat_bot > div > form > button").click({force: true});
        cy.login("mbilal", "mbilal");
        cy.url().should("include", "/en/messaging/message/create");
    })
})
