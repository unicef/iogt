describe('Direct components tests', () => {
    const home = '/en/';

    it('Test footer page with icon', () => {
        cy.visit(home);
        const link = '.footer .bottom-level [href$="are-you-a-fan-of-iogt/"]';
        cy.get(link)
            .contains('Are you a fan of IOGT?')
            .find('img')
            .should('be.visible')
            .and(($img) => {
                expect($img[0].naturalWidth).to.be.greaterThan(0);
            });
        cy.get(link).click();
        cy.url().should('include', '/en/footer/are-you-a-fan-of-iogt/');
    });

    it('Test footer page with image icon', () => {
        cy.visit(home);
        const link = '.footer .bottom-level [href$="about-internet-of-good-thins/"]';
        cy.get(link)
            .contains('About Internet of Good Things')
            .find('img')
            .should('be.visible')
            .and(($img) => {
                expect($img[0].naturalWidth).to.be.greaterThan(0);
            });
        cy.get(link).click();
        cy.url().should('include', '/en/footer/about-internet-of-good-thins/');
    });

    it('Test footer page without icon', () => {
        cy.visit(home);
        const link = '.footer .bottom-level [href$="use-iogt-free-of-data-charges/"]';
        cy.get(link)
            .contains('Use IOGT free of data charges')
            .find('img[src=""]');
        cy.get(link).click();
        cy.url().should('include', '/en/footer/use-iogt-free-of-data-charges/');
    });

    it('Test article in footer index page', () => {
        cy.visit(home);
        const link = '.footer .bottom-level [href$="footer-article/"]';
        cy.get(link)
            .contains('footer article')
            .find('img')
            .should('be.visible')
            .and(($img) => {
                expect($img[0].naturalWidth).to.be.greaterThan(0);
            });
        cy.get(link).click();
        cy.url().should('include', '/en/footer/footer-article/');
    });

    it('Test poll in footer index page', () => {
        cy.visit(home);
        const link = '.footer .bottom-level [href$="covid-19-poll/"]';
        cy.get(link).contains('covid 19 poll')
            .find('img')
            .should('be.visible')
            .and(($img) => {
                expect($img[0].naturalWidth).to.be.greaterThan(0);
            });
        cy.get(link).click();
        cy.url().should('include', '/en/footer/covid-19-poll/');
    });

    it('Test quiz in footer index page', () => {
        cy.visit(home);
        const link = '.footer .bottom-level [href$="covid-quiz/"]';
        cy.get(link).contains('covid quiz')
            .find('img')
            .should('be.visible')
            .and(($img) => {
                expect($img[0].naturalWidth).to.be.greaterThan(0);
            });
        cy.get(link).click();
        cy.url().should('include', '/en/footer/covid-quiz/');
    });

    it('Test section in footer index page', () => {
        cy.visit(home);
        const link = '.footer .bottom-level [href$="covid-section/"]';
        cy.get(link).contains('covid section')
            .find('img')
            .should('be.visible')
            .and(($img) => {
                expect($img[0].naturalWidth).to.be.greaterThan(0);
            });
        cy.get(link).click();
        cy.url().should('include', '/en/footer/covid-section/');
    });

    it('Test survey in footer index page', () => {
        cy.visit(home);
        const link = '.footer .bottom-level [href$="covid-survey/"]';
        cy.get(link).contains('covid survey')
            .find('img')
            .should('be.visible')
            .and(($img) => {
                expect($img[0].naturalWidth).to.be.greaterThan(0);
            });
        cy.get(link).click();
        cy.url().should('include', '/en/footer/covid-survey/');
    });

});

describe('Page link page components tests', () => {
    const home = '/en/';

    it('Test PageLink section with icon', () => {
        cy.visit(home);
        const link = '.footer .bottom-level [href="/en/sections/youth/"]';
        cy.get(link).contains('Youth section page link')
            .find('img')
            .should('be.visible')
            .and(($img) => {
                expect($img[0].naturalWidth).to.be.greaterThan(0);
            });
        cy.get(link).click();
        cy.url().should('include', '/en/sections/youth/');
    });
    
    it('Test PageLink section without icon - indirect icon', () => {
        cy.visit(home);
        const link = '.footer .bottom-level [href="/en/sections/covid-19/"]';
        cy.get(link).contains('covid 19 page link')
            .find('img')
            .should('be.visible')
            .and(($img) => {
                expect($img[0].naturalWidth).to.be.greaterThan(0);
            });
        cy.get(link).click();
        cy.url().should("include","/en/sections/covid-19/");
    });
    
    it.skip('Test PageLink section without icon - indirect image', () => {
        cy.visit(home);
        const link = '.footer .bottom-level [href="/en/sections/parents-caregivers/"]';
        cy.get(link).contains('Parents & Caregivers page link')
            .find('img[src="/en/images/xBjkR17JRLpnRJcQBtw41_KgRnU=/18/fill-32x32/solid-dark-green.png"]')
            .should('be.visible')
            .and(($img) => {
                expect($img[0].naturalWidth).to.be.greaterThan(0);
        });
        cy.get(link).click();
        cy.url().should('include', '/en/sections/parents-caregivers/');
    });

    it.skip('Test PageLink Article', () => {
        cy.visit(home);
        cy.get('.footer .bottom-level a[href="/en/sections/covid-19/odd-story/"]')
            .contains('Odd story PLP')
            .click();
        cy.url().should('include','/en/sections/covid-19/odd-story/');
    });
    
    it.skip('Test PageLink Poll', () => {
        cy.visit(home);
        cy.get('.section-container .bottom-level a[href="/en/sections/questionnaire-testing/basic-test-poll/"]')
            .contains('Basic Test Poll PLP')
            .click();
        cy.url().should('include','/en/sections/questionnaire-testing/basic-test-poll/');
    });

    it.skip('Test PageLink Quiz', () => {
        cy.visit(home);
        cy.get('.section-container .bottom-level a[href="/en/sections/questionnaire-testing/basic-test-quiz/"]')
            .contains('Basic Test Quiz PLP')
            .click();
        cy.url().should('include', '/en/sections/questionnaire-testing/basic-test-quiz/');
    });

    it.skip('Test PageLink Survey', () => {
        cy.visit(home);
        cy.get('.section-container .bottom-level a[href="/en/sections/questionnaire-testing/basic-test-survey/"]')
            .contains('Basic Test Survey PLP')
            .click();
        cy.url().should('include', '/en/sections/questionnaire-testing/basic-test-survey/');
    });

});
