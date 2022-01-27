describe("Section tests", () => {
    const url = "/en/sections/covid-19/"

    it("Tests for lead image and title in section", () => {
        cy.visitUrl(url);

        cy.get(".lead-img").should("be.visible")
            .and(($img) => {
            expect($img[0].naturalWidth).to.be.greaterThan(0)
        });

        cy.get(".image-overlay__text").contains("Covid-19");
    })

    it("Tests for featured content in section", () => {
        cy.get(".section-featured-content-title").should("have.css", "color", "rgb(238, 56, 81)");
        cy.get(".section-featured-content-title").should("have.css", "background-color", "rgb(253, 235, 238)");
        cy.get(".section-featured-content-title").contains("How to encourage friends for vaccination?")
    })
})
