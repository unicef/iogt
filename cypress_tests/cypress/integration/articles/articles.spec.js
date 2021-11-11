describe("Articles components tests", () => {
    const url = "/en/sections/covid-19/odd-story/"

    it("Test lead image and title", () => {

        cy.visitUrl(url);

        cy.get("img.article__lead-img-featured").should("be.visible")
            .and(($img) => {
            expect($img[0].naturalWidth).to.be.greaterThan(0)
        });

        cy.get("section.article__content > h1").contains("Odd story");
    })

    it("Test Content Blocks elements", () => {
        cy.get("[class=block-heading]").contains("content block heading");

        cy.get("div.block-paragraph:nth-child(3) > p:nth-child(1)")
            .contains("content block paragraph");

        cy.get("div.block-markdown > p:nth-child(1) strong").contains("markdown");

        cy.get("[class=block-image] img").should("be.visible")
            .and(($img) => {
            expect($img[0].naturalWidth).to.be.greaterThan(0)
        });

        // //todo content block List (should have bullet points)
        // cy.get("[class=block-list]").contains("::marker")
        // //todo content block Numbered list (should have 1., 2., 3. etc)
        // cy.get("[class=block-numbered_list]").contains("::marker")

        cy.get("[class=article__content__link-btn]").contains("Youth");

        cy.get('video').its('0.paused').should('equal', true);

    })

    it("Test chat bot with logged in user", () => {
        cy.visitUrl("/en/accounts/login/");
        cy.login("saqlain", "saqlain");
        cy.visitUrl(url);
        cy.get("#content-wrap > div.main-wrapper > div > div.content > article > section > div.block-chat_bot > div > form > button").click({force: true})
        cy.url().should("include", "/en/messaging/message/");
    });

    it("Test chat bot with anonymous user", () => {
        cy.visitUrl(url);
        cy.get("#content-wrap > div.main-wrapper > div > div.content > article > section > div.block-chat_bot > div > form > button").click({force: true});
        cy.login("saqlain", "saqlain");
        cy.url().should("include", "/en/messaging/message/create");
    })

    it("Test previous buttons", () => {
        cy.visit(url);
        cy.get("a[class=article__navigation--previous]").click();
        cy.url().should("include", "/en/sections/covid-19/where-to-get-vaccination/")

    })

    it("Test next button", () => {
        cy.visit(url);
        cy.get("a[class=article__navigation--next]").click();
        cy.url().should("include", "/en/sections/covid-19/early-life-tips-quick-survey/")
    })

    it("Test article comments when user is logged out", () => {
        cy.visitUrl(url)
        cy.get("[class=comments__submit] a").contains("Log in / Create account");
    })

    it("Test article comments when user is logged in and commenting is open", () => {
        cy.visitUrl("/en/accounts/login/");
        cy.login("saqlain", "saqlain");
        cy.visitUrl(url)
        cy.get("textarea[id=id_comment]")
    })

    it("Test article comments when user is logged in and comments are closed", () => {
        cy.visitUrl("/en/accounts/login/");
        cy.login("saqlain", "saqlain");
        cy.visitUrl(url)
        cy.get("section[class=comments] > p:nth-child(2)").contains("New comments have been disabled for this page.")
    })

})