describe("Tests for navigation buttons in articles", () => {
    const url = "/en/sections/covid-19/odd-story/";

    it.skip("Test previous buttons", () => {
        cy.visit(url);
        cy.get(".article__navigation > .article__navigation--previous").click();
        cy.url().should("include", "/en/sections/covid-19/where-to-get-vaccination/");
    });

    it("Test next button", () => {
        cy.visit(url);
        cy.get("a[class=article__navigation--next]").click();
        cy.url().should("include", "/en/sections/covid-19/early-life-tips-quick-survey/");
    });
});
