def hello(nome="Mundo"):

    return {
        "success": True,
        "message": f"Olá {nome}",
        "data": {
            "nome": nome
        }
    }
