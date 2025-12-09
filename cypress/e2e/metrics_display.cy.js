// Cypress тест для проверки отображения LLM-метрик на UI
// Этот тест использует cy.intercept для мокирования ответа API, который содержит метрики

describe('Metrics display', () => {
  const apiUrl = 'https://api.mentorpiece.org/v1/process-ai-request';

  it('shows BLEU and BERTScore and green indicator when metrics pass thresholds', () => {
    cy.intercept('POST', apiUrl, (req) => {
      req.reply({
        statusCode: 200,
        body: {
          translation: 'Bonjour le monde',
          metrics: {
            BLEU: 0.32,
            BERTScore: 0.82,
            LengthRatio: 1.02
          },
          verdict: 'Translation acceptable'
        }
      });
    }).as('apiRequest');

    cy.visit('/');
    cy.get('#original_text').clear().type('Hello world');
    cy.get('#target_language').select('French');
    cy.contains('button', 'Перевести').click();
    cy.wait('@apiRequest');

    // Проверяем, что на странице появилась секция с метриками
    cy.contains('BLEU').should('exist');
    cy.contains('BERTScore').should('exist');
    cy.contains('0.32').should('exist');
    cy.contains('0.82').should('exist');

    // Проверяем, что индикатор успеха (например, зеленый) присутствует
    // Предполагается, что успешные метрики помечаются классом .metric-success
    cy.get('.metric-success').should('exist');
  });

  it('shows warning when metrics are below threshold', () => {
    cy.intercept('POST', apiUrl, (req) => {
      req.reply({
        statusCode: 200,
        body: {
          translation: 'Mauvaise traduction',
          metrics: {
            BLEU: 0.10,
            BERTScore: 0.30,
            LengthRatio: 0.5
          },
          verdict: 'Poor quality'
        }
      });
    }).as('apiRequestLow');

    cy.visit('/');
    cy.get('#original_text').clear().type('This is a test of translation quality');
    cy.get('#target_language').select('French');
    cy.contains('button', 'Перевести').click();
    cy.wait('@apiRequestLow');

    cy.contains('BLEU').should('exist');
    cy.contains('0.10').should('exist');
    // Предполагается, что предупреждение помечается классом .metric-warning
    cy.get('.metric-warning').should('exist');
  });
});
