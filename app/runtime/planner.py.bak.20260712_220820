def build_plan(goal: str):
    g = goal.lower().strip()

    plan = []

    # Restart
    if any(x in g for x in [
        "restart",
        "reinicie",
        "reiniciar",
        "reinicia",
    ]):
        plan.append({
            "action": "service.restart",
            "args": {
                "service": "agente-divina-api.service"
            }
        })

    # Status
    elif any(x in g for x in [
        "status",
        "situação",
        "situacao",
        "estado",
    ]):
        plan.append({
            "action": "service.status",
            "args": {
                "service": "agente-divina-api.service"
            }
        })

    # Deploy
    elif any(x in g for x in [
        "deploy",
        "publicar",
        "atualizar",
        "implantar",
    ]):
        plan.extend([
            {
                "action":"deploy.validate",
                "args":{}
            },
            {
                "action":"deploy.apply",
                "args":{}
            }
        ])

    # Health
    elif any(x in g for x in [
        "health",
        "saúde",
        "saude",
        "diagnóstico",
        "diagnostico",
    ]):
        plan.append({
            "action":"service.status",
            "args":{
                "service":"agente-divina-api.service"
            }
        })

    # Fallback
    if not plan:
        plan.append({
            "action":"goal.echo",
            "args":{
                "goal":goal
            }
        })

    return plan
