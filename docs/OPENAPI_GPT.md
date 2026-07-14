# OpenAPI do Agente Divina

**Atualizado em:** 12/07/2026

## Objetivo
O projeto mantém dois schemas OpenAPI distintos.

### OpenAPI completo
- URL: https://agente.divinahomepy.com/openapi.json
- Uso: documentação interna, Swagger e desenvolvimento.
- Expõe todas as rotas (aprox. 72 operações).

### OpenAPI GPT
- URL: https://agente.divinahomepy.com/openapi-gpt.json
- Uso: GPT Builder / Actions.
- Expõe apenas 8 operações autorizadas.

Rotas:
- GET /health
- POST /admin
- POST /admin/full-access
- POST /erp
- POST /erp/security
- POST /fiscal
- POST /supabase
- POST /frontend

## Observação
Sempre utilizar https://agente.divinahomepy.com/openapi-gpt.json no GPT Builder. Não utilizar o OpenAPI completo, pois excede o limite de operações.
