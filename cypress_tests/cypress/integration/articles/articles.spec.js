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

    it("Test related article section", () => {

        cy.get(".related-articles > ul:nth-child(2) > li:nth-child(1) > a:nth-child(1) > p:nth-child(1)")
            .contains("Where to get vaccinated in?")
    })
})
