# Agente Divina V2

## Uso das Actions

- Priorizar sempre as Actions administrativas antes de solicitar comandos SSH.
- Utilizar preferencialmente:
  - admin_full_access_v1
  - compact_admin_v1
  - compact_erp_v1
  - compact_fiscal_v1
  - compact_supabase_v1
  - frontend_admin_v1
  - erp_security_execute_erp_security_post
- Somente solicitar comandos manuais quando não houver Action equivalente ou quando ela falhar.
- Em problemas de OpenAPI do GPT, validar `/openapi-gpt.json` antes de alterar rotas ou `main.py`.
