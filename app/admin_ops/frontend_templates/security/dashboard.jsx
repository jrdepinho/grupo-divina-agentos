"use client";

import { useEffect, useState } from "react";
import ErpLayout from "@/components/erp/ErpLayout";
import StatCard from "@/components/erp/StatCard";
import LoadingState from "@/components/erp/LoadingState";

const API_BASE = process.env.NEXT_PUBLIC_AGENTE_API_URL || "https://agente.divinahomepy.com";
const API_TOKEN = process.env.NEXT_PUBLIC_AGENTE_ADMIN_TOKEN || "";

async function apiGet(path) {
  const response = await fetch(`${API_BASE}${path}`, {
    cache: "no-store",
    headers: API_TOKEN ? { Authorization: `Bearer ${API_TOKEN}` } : {},
  });
  const json = await response.json();
  if (!response.ok) throw new Error(json?.detail || json?.error || "Erro ao carregar segurança");
  return json;
}

export default function SegurancaPage() {
  const [summary, setSummary] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const json = await apiGet("/erp/security/summary");
      setSummary(json.summary || {});
    } catch (e) {
      setError(e.message);
    }
    setLoading(false);
  }

  useEffect(() => { load(); }, []);

  const cards = [
    ["Usuários", summary.usuarios, `${summary.usuarios_ativos || 0} ativos`],
    ["Perfis", summary.perfis, "Perfis operacionais"],
    ["Permissões", summary.permissoes, `${summary.perfil_permissoes || 0} vínculos`],
    ["Acessos", summary.usuario_empresa_vinculos, "Usuário × empresa"],
    ["Empresas", summary.empresas_ativas, "Empresas ativas"],
    ["Unidades", summary.unidades_ativas, "Unidades ativas"],
    ["Auditoria", summary.auditorias, "Eventos registrados"],
  ];

  return (
    <ErpLayout title="Segurança" subtitle="Administração de usuários, acessos, perfis e permissões">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <a href="/erp" style={{ color: "#334155" }}>← ERP</a>
        <button onClick={load} style={buttonStyle}>Atualizar</button>
      </div>
      <LoadingState loading={loading} error={error} empty={false} />
      {!loading && !error && (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 14, marginBottom: 20 }}>
            {cards.map(([title, value, subtitle]) => <StatCard key={title} title={title} value={value ?? 0} subtitle={subtitle} />)}
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 14 }}>
            <a href="/erp/seguranca/usuarios" style={tileStyle}>Usuários<span>Gerenciar usuários operacionais</span></a>
            <a href="/erp/seguranca/perfis" style={tileStyle}>Perfis<span>Perfis e papéis de acesso</span></a>
            <a href="/erp/seguranca/permissoes" style={tileStyle}>Permissões<span>Matriz de permissões por módulo</span></a>
            <a href="/erp/seguranca/empresas" style={tileStyle}>Empresas<span>Acessos por empresa e unidade</span></a>
            <a href="/erp/seguranca/auditoria" style={tileStyle}>Auditoria<span>Histórico de alterações</span></a>
          </div>
        </>
      )}
    </ErpLayout>
  );
}

const buttonStyle = { padding: "10px 14px", borderRadius: 10, border: "1px solid #cbd5e1", background: "white", cursor: "pointer" };
const tileStyle = { display: "flex", flexDirection: "column", gap: 6, padding: 18, borderRadius: 14, border: "1px solid #e5e7eb", background: "white", color: "#0f172a", textDecoration: "none", fontWeight: 800 };
