describe('Survey submission tests', () => {
  it('Submit a survey and get back', () => {
    cy.visit('/en/surveys/survey/')
    cy.url().should('include', '/en/surveys/survey/')
    cy.get('input[name=q1]')
        .type('A1')
        .should('have.value', 'A1')
    cy.get('button[type=submit]').click()
    cy.get('.cust-btn.cust-btn--dark.survey-page__btn').click()
    cy.url().should('include', '/en/surveys/survey/')
  })
})
