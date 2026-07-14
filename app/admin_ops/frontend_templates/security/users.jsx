"use client";

import { useEffect, useMemo, useState } from "react";
import ErpLayout from "@/components/erp/ErpLayout";
import LoadingState from "@/components/erp/LoadingState";

const API_BASE = process.env.NEXT_PUBLIC_AGENTE_API_URL || "https://agente.divinahomepy.com";
const API_TOKEN = process.env.NEXT_PUBLIC_AGENTE_ADMIN_TOKEN || "";

async function apiPost(path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      ...(API_TOKEN ? { Authorization: `Bearer ${API_TOKEN}` } : {}),
    },
    body: JSON.stringify(body),
  });
  const json = await response.json();
  if (!response.ok) throw new Error(json?.detail || json?.error || "Erro ao carregar usuários");
  return json;
}

export default function UsuariosSegurancaPage() {
  const [users, setUsers] = useState([]);
  const [query, setQuery] = useState("");
  const [activeOnly, setActiveOnly] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const json = await apiPost("/erp/security/users/list", { ativo: activeOnly, search: query || null, limit: 300 });
      setUsers(json.users || []);
    } catch (e) {
      setError(e.message);
    }
    setLoading(false);
  }

  useEffect(() => { load(); }, []);
  const filtered = useMemo(() => users, [users]);

  return (
    <ErpLayout title="Usuários" subtitle="Administração de usuários operacionais do ERP">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, marginBottom: 16 }}>
        <a href="/erp/seguranca" style={{ color: "#334155" }}>← Segurança</a>
        <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Buscar por nome ou email" style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #cbd5e1", minWidth: 260 }} />
          <label style={{ fontSize: 13, color: "#475569" }}><input type="checkbox" checked={activeOnly} onChange={(e) => setActiveOnly(e.target.checked)} /> Apenas ativos</label>
          <button onClick={load} style={buttonStyle}>Pesquisar</button>
          <button disabled title="Próxima entrega" style={{ ...buttonStyle, opacity: .55 }}>Novo usuário</button>
        </div>
      </div>
      <LoadingState loading={loading} error={error} empty={!loading && !error && !filtered.length} />
      {!loading && !error && !!filtered.length && (
        <div style={{ overflowX: "auto", background: "white", border: "1px solid #e5e7eb", borderRadius: 14 }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead><tr>{["Nome", "Email", "Tipo", "Departamento", "Status", "Empresas", "Auth"].map((h) => <th key={h} style={thStyle}>{h}</th>)}</tr></thead>
            <tbody>{filtered.map((u) => <tr key={u.id}><td style={tdStyle}>{u.nome}</td><td style={tdStyle}>{u.email}</td><td style={tdStyle}>{u.tipo_usuario || "-"}</td><td style={tdStyle}>{u.departamento || "-"}</td><td style={tdStyle}><span style={u.ativo ? okBadge : offBadge}>{u.ativo ? "Ativo" : "Inativo"}</span></td><td style={tdStyle}>{u.acessos_empresas || 0}</td><td style={tdStyle}>{u.auth_user_id ? "Vinculado" : "Pendente"}</td></tr>)}</tbody>
          </table>
        </div>
      )}
    </ErpLayout>
  );
}

const buttonStyle = { padding: "10px 14px", borderRadius: 10, border: "1px solid #cbd5e1", background: "white", cursor: "pointer" };
const thStyle = { padding: 10, textAlign: "left", background: "#f1f5f9", borderBottom: "1px solid #e5e7eb", whiteSpace: "nowrap" };
const tdStyle = { padding: 10, borderBottom: "1px solid #f1f5f9", whiteSpace: "nowrap" };
const okBadge = { display: "inline-block", padding: "3px 8px", borderRadius: 999, background: "#dcfce7", color: "#166534", fontWeight: 700 };
const offBadge = { display: "inline-block", padding: "3px 8px", borderRadius: 999, background: "#fee2e2", color: "#991b1b", fontWeight: 700 };
