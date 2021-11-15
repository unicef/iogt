describe("Articles components tests", () => {
    const url = "/en/"

    it("Test footer pages in footer index page", () => {
        cy.visitUrl(url)
        cy.get("[href=\"/en/footer/are-you-a-fan-of-iogt/\"]")
            .contains("Are you a fan of IOGT?")
        cy.get("[href=\"/en/footer/are-you-a-fan-of-iogt/\"] img").should("be.visible")
            .and(($img) => {
            expect($img[0].naturalWidth).to.be.greaterThan(0)
        });
        cy.get(".section-container .bottom-level a[href=\"/en/footer/are-you-a-fan-of-iogt/\"]")
            .contains("Are you a fan of IOGT?").click()
        cy.url().should("include","/en/footer/are-you-a-fan-of-iogt/")
    })

    it("Test PageLink page with icon", () => {
        cy.visitUrl(url)
        cy.get("[href=\"/en/sections/covid-19/\"]")
            .contains("covid 19 page link")
        cy.get("[href=\"/en/sections/covid-19/\"] img").should("be.visible")
            .and(($img) => {
            expect($img[0].naturalWidth).to.be.greaterThan(0)
        });
        cy.get(".section-container .bottom-level a[href=\"/en/sections/covid-19/\"]")
            .contains("covid 19 page link").click()
        cy.url().should("include","/en/sections/covid-19/")
    })

    it("Test PageLink page without icon", () => {
        cy.visitUrl(url)
        cy.get("[href=\"/en/sections/youth/\"]")
            .contains("Youth section page link")
        cy.get("[href=\"/en/sections/youth/\"] img").should("be.visible")
            .and(($img) => {
            expect($img[0].naturalWidth).to.be.greaterThan(0)
        });
        cy.get(".section-container .bottom-level a[href=\"/en/sections/youth/\"]")
            .contains("Youth section page link").click()
        cy.url().should("include","/en/sections/youth/")
    })

    it("Test article in footer index page", () => {
        cy.visitUrl(url)
        cy.get("[href=\"/en/footer/footer-article/\"]")
            .contains("footer article")
        cy.get("[href=\"/en/footer/footer-article/\"] img").should("be.visible")
            .and(($img) => {
            expect($img[0].naturalWidth).to.be.greaterThan(0)
        });
        cy.get(".section-container .bottom-level a[href=\"/en/footer/footer-article/\"]")
            .contains("footer article").click()
        cy.url().should("include","/en/footer/footer-article/")
    })

    it("Test poll in footer index page", () => {
        cy.visitUrl(url)
        cy.get("[href=\"/en/footer/covid-19-poll/\"]")
            .contains("covid 19 poll")
        cy.get("[href=\"/en/footer/covid-19-poll/\"] img").should("be.visible")
            .and(($img) => {
            expect($img[0].naturalWidth).to.be.greaterThan(0)
        });
        cy.get(".section-container .bottom-level a[href=\"/en/footer/covid-19-poll/\"]")
            .contains("covid 19 poll").click()
        cy.url().should("include","/en/footer/covid-19-poll/")
    })

    it("Test quiz in footer index page", () => {
        cy.visitUrl(url)
        cy.get("[href=\"/en/footer/covid-quiz/\"]")
            .contains("covid quiz")
        cy.get("[href=\"/en/footer/covid-quiz/\"] img").should("be.visible")
            .and(($img) => {
            expect($img[0].naturalWidth).to.be.greaterThan(0)
        });
        cy.get(".section-container .bottom-level a[href=\"/en/footer/covid-quiz/\"]")
            .contains("covid quiz").click()
        cy.url().should("include","/en/footer/covid-quiz/")
    })

    it("Test section in footer index page", () => {
        cy.visitUrl(url)
        cy.get("[href=\"/en/footer/covid-section/\"]")
            .contains("covid section")
        cy.get("[href=\"/en/footer/covid-section/\"] img").should("be.visible")
            .and(($img) => {
            expect($img[0].naturalWidth).to.be.greaterThan(0)
        });
        cy.get(".section-container .bottom-level a[href=\"/en/footer/covid-section/\"]")
            .contains("covid section").click()
        cy.url().should("include","/en/footer/covid-section/")
    })

    it("Test survey in footer index page", () => {
        cy.visitUrl(url)
        cy.get("[href=\"/en/footer/covid-survey/\"]")
            .contains("covid survey")
        cy.get("[href=\"/en/footer/covid-survey/\"] img").should("be.visible")
            .and(($img) => {
            expect($img[0].naturalWidth).to.be.greaterThan(0)
        });
        cy.get(".section-container .bottom-level a[href=\"/en/footer/covid-survey/\"]")
            .contains("covid survey").click()
        cy.url().should("include","/en/footer/covid-survey/")
    })
})
