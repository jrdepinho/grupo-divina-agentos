from __future__ import annotations

from fastapi import APIRouter

from app.utils import supabase_rpc


router = APIRouter()


@router.get("/auditoria_dashboard")
def auditoria_dashboard():
    return {
        "notas": supabase_rpc("select count(*) as total from notas_fiscais"),
        "itens": supabase_rpc("select count(*) as total from itens_nota_fiscal"),
        "parcelas": supabase_rpc("select count(*) as total from contas_pagar"),
    }


@router.get("/auditoria_importacao/{chave_nfe}")
def auditoria_importacao(chave_nfe: str):
    return {
        "nota": supabase_rpc("select * from notas_fiscais where chave_nfe = '" + chave_nfe + "'"),
        "itens": supabase_rpc("select count(*) as total from itens_nota_fiscal where chave_nfe = '" + chave_nfe + "'"),
        "parcelas": supabase_rpc("select count(*) as total from contas_pagar where chave_nfe = '" + chave_nfe + "'"),
    }

