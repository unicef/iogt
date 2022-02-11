describe.skip("Articles components tests", () => {
    const url = "/en/sections/covid-19/"

    it("Test for myths subsections in section", () => {
        cy.visitUrl(url);
        cy.get(".sub-section").contains("Myths");
        cy.get("[href=\"/en/sections/covid-19/myths/\"] .img-holder img").should("be.visible")
            .and(($img) => {
            expect($img[0].naturalWidth).to.be.greaterThan(0)
        });
    })

    it("Test for vaccination centers subsections in section", () => {
        cy.get(".sub-section").contains("Vaccination centres");
        cy.get("[href=\"/en/sections/covid-19/vaccination-centres/\"] .img-holder img").should("be.visible")
            .and(($img) => {
            expect($img[0].naturalWidth).to.be.greaterThan(0)
        });
    })
})
