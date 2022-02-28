describe("Page link page article tests", () => {
    const url = "/en/sections/page-in-page-testing/"

    it("Test PLP articles", () => {

        cy.visitUrl(url);
        cy.get(".article-card>[href=\"/en/sections/covid-19/where-to-get-vaccinated-in/\"]>div.article-header>p").contains("Where to get vaccinated in?")
        cy.get(".article-card>[href=\"/en/sections/covid-19/where-to-get-vaccinated-in/\"]>div.img-holder>[alt='solid-dark-green.png']")
        cy.get(".article-card>[href=\"/en/sections/covid-19/where-to-get-vaccination/\"]>div.article-header>p").contains("Where to get vaccination?")
        cy.get(".article-card>[href=\"/en/sections/covid-19/where-to-get-vaccination/\"]>div.img-holder>[alt='solid-dark-green.png']")
        
    })

    it("Test PLP questionnaires", () => {

        cy.visitUrl(url);
        
        cy.get(".questionnaire-components__component>[href=\"/en/sections/questionnaire-testing/basic-test-poll/\"]>div>p").contains("Basic Test Poll")
        cy.get(".questionnaire-components__component>[href=\"/en/sections/questionnaire-testing/basic-test-quiz/\"]>div>p").contains("Basic Test Quiz")
        cy.get(".questionnaire-components__component>[href=\"/en/sections/questionnaire-testing/basic-test-survey/\"]>div>p").contains("Basic Test Survey")
                   
    })

    it("Test PLP sections", () => {

        cy.visitUrl(url);
        cy.get(".section-card>[href=\"/en/sections/covid-19/\"]>p").contains("Covid-19")
        cy.get(".section-card>[href=\"/en/sections/covid-19/\"]>div.img-holder>[alt='solid-dark-green.png']")
                
    })

})
