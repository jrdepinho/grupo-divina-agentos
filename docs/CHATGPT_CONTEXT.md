# ChatGPT Context

Regra operacional:
- Sempre utilizar as Actions administrativas antes de solicitar comandos Linux ao usuário.
- Somente solicitar SSH/comandos manuais quando não existir Action equivalente ou quando a Action falhar.
- Antes de concluir que uma Action não existe, verificar as Actions disponíveis.
- Para problemas de OpenAPI do GPT, validar /openapi-gpt.json e confirmar que contém apenas os endpoints compactos autorizados.
- Após qualquer alteração, validar compilação, reiniciar o serviço quando necessário e conferir logs.
