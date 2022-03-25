describe("Direct components tests", () => {
    const url = "/en/"

    it("Test footer page with icon", () => {
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

    it("Test footer page without icon - indirect icon", () => {
        cy.visitUrl(url)
        cy.get("[href=\"/en/footer/about-internet-of-good-thins/\"]")
            .contains("About Internet of Good Things")
        cy.get("[href=\"/en/footer/about-internet-of-good-thins/\"] img[src=\"/media/svg-to-png-maps/svg-to-png_gxn0V4r.png\"").should("be.visible")
            .and(($img) => {
            expect($img[0].naturalWidth).to.be.greaterThan(0)
        });
        cy.get(".section-container .bottom-level a[href=\"/en/footer/about-internet-of-good-thins/\"]")
            .contains("About Internet of Good Things").click()
        cy.url().should("include","/en/footer/about-internet-of-good-thins/")
    })

    it("Test footer page without icon - indirect image", () => {
        cy.visitUrl(url)
        cy.get("[href=\"/en/footer/use-iogt-free-of-data-charges/\"]")
            .contains("Use IOGT free of data charges")
        cy.get("[href=\"/en/footer/use-iogt-free-of-data-charges/\"] img[src=\"/en/images/xBjkR17JRLpnRJcQBtw41_KgRnU=/18/fill-32x32/solid-dark-green.png\"").should("be.visible")
            .and(($img) => {
            expect($img[0].naturalWidth).to.be.greaterThan(0)
        });
        cy.get(".section-container .bottom-level a[href=\"/en/footer/use-iogt-free-of-data-charges/\"]")
            .contains("Use IOGT free of data charges").click()
        cy.url().should("include","/en/footer/use-iogt-free-of-data-charges/")
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

describe("Page link page components tests", () => {
    const url = "/en/"

    it("Test PageLink section with icon", () => {
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
    
    it("Test PageLink section without icon - indirect icon", () => {
        cy.visitUrl(url)
        cy.get("[href=\"/en/sections/covid-19/\"]")
            .contains("Covid 19 Section page link")
        cy.get("[href=\"/en/sections/covid-19/\"] img[src=\"/media/svg-to-png-maps/svg-to-png_gxn0V4r.png\"").should("be.visible")
            .and(($img) => {
            expect($img[0].naturalWidth).to.be.greaterThan(0)
        });
        cy.get(".section-container .bottom-level a[href=\"/en/sections/covid-19/\"]")
            .contains("Covid 19 Section page link").click()
        cy.url().should("include","/en/sections/covid-19/")
    })
    
    it("Test PageLink section without icon - indirect image", () => {
        cy.visitUrl(url)
        cy.get("[href=\"/en/sections/parents-caregivers/\"]")
            .contains("Parents & Caregivers page link")
        cy.get("[href=\"/en/sections/parents-caregivers/\"] img[src=\"/en/images/xBjkR17JRLpnRJcQBtw41_KgRnU=/18/fill-32x32/solid-dark-green.png\"").should("be.visible")
            .and(($img) => {
            expect($img[0].naturalWidth).to.be.greaterThan(0)
        });
        cy.get(".section-container .bottom-level a[href=\"/en/sections/parents-caregivers/\"]")
            .contains("Parents & Caregivers page link").click()
        cy.url().should("include","/en/sections/parents-caregivers/")
    })  

    it("Test PageLink Article", () => {
        cy.visitUrl(url)
        cy.get(".section-container .bottom-level a[href=\"/en/sections/covid-19/odd-story/\"]")
            .contains("Odd story PLP").click()
        cy.url().should("include","/en/sections/covid-19/odd-story/")
    })
    
    it("Test PageLink Poll", () => {
        cy.visitUrl(url)
        cy.get(".section-container .bottom-level a[href=\"/en/sections/questionnaire-testing/basic-test-poll/\"]")
            .contains("Basic Test Poll PLP").click()
        cy.url().should("include","/en/sections/questionnaire-testing/basic-test-poll/")
    })

    it("Test PageLink Quiz", () => {
        cy.visitUrl(url)
        cy.get(".section-container .bottom-level a[href=\"/en/sections/questionnaire-testing/basic-test-quiz/\"]")
            .contains("Basic Test Quiz PLP").click()
        cy.url().should("include","/en/sections/questionnaire-testing/basic-test-quiz/")
    })

    it("Test PageLink Survey", () => {
        cy.visitUrl(url)
        cy.get(".section-container .bottom-level a[href=\"/en/sections/questionnaire-testing/basic-test-survey/\"]")
            .contains("Basic Test Survey PLP").click()
        cy.url().should("include","/en/sections/questionnaire-testing/basic-test-survey/")
    })

})



