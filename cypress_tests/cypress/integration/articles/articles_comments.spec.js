describe("Tests for comment section in articles", () => {
    const url = "/en/sections/covid-19/odd-story/"
    const adminLoginUrl = "/admin/login/"

    it("Test article comments when user is logged out and comments are open", () => {
        cy.visitUrl(adminLoginUrl)
        cy.adminLogin("mbilal", "mbilal");
        cy.visitUrl("/admin/pages/22/edit/#tab-comments")
        cy.get("select#id_commenting_status").select('Open').should('have.value', 'open');
        cy.get(".dropdown-toggle").click()
        cy.get("[name=action-publish]").scrollIntoView().should("have.value", "action-publish").click()
        cy.visitUrl("/en/accounts/logout/")
        cy.get(".cust-btn>span").contains("Log out").click()
        cy.visitUrl(url)
        cy.get("[class=comments__submit] a").contains("Log in / Create account");
    })

    it("Test article comments when user is logged in and commenting is open", () => {
        cy.visitUrl("/en/accounts/login/");
        cy.login("mbilal", "mbilal");
        cy.visitUrl(url)
        cy.get("textarea[id=id_comment]")
    })

    it("Test report button when clicked by another user", () => {
        cy.visitUrl("/en/accounts/login/")
        cy.login("7777", "7412")
        cy.visitUrl(url)
        cy.get(".individual-comment:nth-child(1) > :nth-child(2) > :nth-child(6)").click()
        cy.url().should("include", "/en/comments/flag/14/")
    })

    it("Test remove button when user is logged in as admin/moderator", () => {
        cy.visitUrl(adminLoginUrl)
        cy.adminLogin("mbilal", "mbilal");
        cy.visitUrl(url)
        cy.get(".reply-link.text-danger")
    })

    it("Test list of comments when comments are not disabled", () => {
        cy.visitUrl(url)
        cy.get("div.individual-comment:nth-child(1) > div:nth-child(2) > div:nth-child(1) > span:nth-child(1) > p:nth-child(2)")
        cy.get("div.individual-comment:nth-child(1) > div:nth-child(2) > span:nth-child(2)")
        cy.get(".comments-holder > :nth-child(1) > :nth-child(2) > :nth-child(4)")
    })

    it("Test article comments when user is logged in and comments are closed", () => {
        cy.visitUrl(adminLoginUrl)
        cy.adminLogin("mbilal", "mbilal");
        cy.visitUrl("/admin/pages/22/edit/#tab-comments")
        cy.get("select#id_commenting_status").select('Closed').should('have.value', 'closed')
        cy.get(".dropdown-toggle").click()
        cy.get("[name=action-publish]").scrollIntoView().should("have.value", "action-publish").click()
        cy.visitUrl(url)
        cy.get("section[class=comments] > p:nth-child(2)").contains("New comments have been disabled for this page.")
    })

    it("Test article comments when comments are disabled", () => {
        cy.visitUrl(adminLoginUrl)
        cy.adminLogin("mbilal", "mbilal");
        cy.visitUrl("/admin/pages/22/edit/#tab-comments")
        cy.get("select#id_commenting_status").select('Disabled').should('have.value', 'disabled')
        cy.get(".dropdown-toggle").click()
        cy.get("[name=action-publish]").scrollIntoView().should("have.value", "action-publish").click()
        cy.visitUrl(url)
        cy.get("section[class=comments").should("not.exist");
    })
})
