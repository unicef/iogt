describe.skip('Survey submission tests', () => {

    const url = "/en/surveys/survey-title/";

    it('Submit a survey and get back', () => {
        cy.visitUrl(url);
        cy.get('input[name=textfield]')
            .type('A1')
            .should('have.value', 'A1');
        cy.get('button[type=submit]').click();
        cy.get('.icon-btn.icon-btn--md.icon-btn--dark.icon-btn--rounded').click();
        cy.url().should('include', url);
    });

});
