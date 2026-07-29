import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
import os

# ==========================================
# CONFIGURAÇÃO DE PÁGINA E CSS TEMA CLARO
# ==========================================
st.set_page_config(page_title="Caixa de Esportes Bet77", layout="wide", page_icon="⚽")

st.markdown("""
    <style>
    .stApp {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }
    h1, h2, h3 {
        color: #1E3A8A !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700 !important;
    }
    .card-resumo {
        background-color: #FFFFFF;
        padding: 16px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
    }
    .card-resumo span {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
    }
    .card-resumo h3 {
        margin-top: 5px;
        margin-bottom: 0;
        font-size: 1.5rem;
    }
    .valor-negativo {
        color: #DC2626 !important;
        font-weight: 700;
    }
    .valor-zero {
        color: #16A34A !important;
        font-weight: 700;
    }
    div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        border-radius: 6px !important;
    }
    div.stButton > button {
        border-radius: 6px !important;
        font-weight: bold !important;
        width: 100% !important;
    }
    button[data-baseweb="tab"] {
        font-weight: 600 !important;
        color: #475569 !important;
    }
    button[aria-selected="true"] {
        color: #2563EB !important;
        border-bottom-color: #2563EB !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# AUTENTICAÇÃO
# ==========================================
CODIGO_ACESSO_CORRETO = "E2605"

def verificar_autenticacao():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: center;'>⚽ Caixa Bet77</h2>", unsafe_allow_html=True)
            with st.form("form_login"):
                codigo = st.text_input("Código de Acesso:", type="password")
                if st.form_submit_button("🔑 Entrar no Sistema", use_container_width=True):
                    if codigo == CODIGO_ACESSO_CORRETO:
                        st.session_state["autenticado"] = True
                        st.rerun()
                    else:
                        st.error("❌ Código de acesso incorreto!")
        return False
    return True

if not verificar_autenticacao():
    st.stop()

# ==========================================
# BASE DE DADOS AUTOMÁTICA
# ==========================================
DB_FILE = 'caixa_bet77_database.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS supervisores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS agentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            utilizador TEXT UNIQUE NOT NULL,
            supervisor_id INTEGER,
            estado TEXT DEFAULT 'Activo',
            FOREIGN KEY (supervisor_id) REFERENCES supervisores (id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS fecho_caixa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            utilizador TEXT NOT NULL,
            valor_feito REAL DEFAULT 0.0,
            valor_entregue REAL DEFAULT 0.0,
            saldo REAL DEFAULT 0.0,
            data_registo TEXT NOT NULL,
            UNIQUE(data, utilizador)
        )
    ''')
    conn.commit()

    # Inserção de dados de exemplo caso esteja vazio
    c.execute("SELECT COUNT(*) FROM supervisores")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO supervisores (nome) VALUES ('Sup Albertina')")
        c.execute("INSERT INTO supervisores (nome) VALUES ('Sup Carlos')")
        
        agentes_teste = [
            ("Rabeca", "bet77 18", 1),
            ("Silva", "bet77 40", 1),
            ("Rosa", "bet77 53", 1),
            ("Felismina", "bet77 50", 1)
        ]
        c.executemany("INSERT INTO agentes (nome, utilizador, supervisor_id) VALUES (?, ?, ?)", agentes_teste)
        conn.commit()

    conn.close()

init_db()

# ==========================================
# FUNÇÕES DE BANCO DE DADOS
# ==========================================
def carregar_supervisores():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM supervisores ORDER BY nome", conn)
    conn.close()
    return df

def carregar_agentes_por_supervisor(supervisor_id=None):
    conn = sqlite3.connect(DB_FILE)
    if supervisor_id and supervisor_id != "TODOS":
        query = """
            SELECT a.id, a.nome, a.utilizador, a.supervisor_id, a.estado, s.nome as supervisor_nome 
            FROM agentes a 
            LEFT JOIN supervisores s ON a.supervisor_id = s.id 
            WHERE a.supervisor_id = ? AND a.estado = 'Activo' ORDER BY s.nome, a.utilizador
        """
        df = pd.read_sql_query(query, conn, params=(supervisor_id,))
    else:
        query = """
            SELECT a.id, a.nome, a.utilizador, a.supervisor_id, a.estado, COALESCE(s.nome, 'Sem Supervisor') as supervisor_nome 
            FROM agentes a 
            LEFT JOIN supervisores s ON a.supervisor_id = s.id 
            WHERE a.estado = 'Activo'
            ORDER BY s.nome, a.utilizador
        """
        df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def obter_fecho_existente(data_str, utilizador):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT valor_feito, valor_entregue, saldo FROM fecho_caixa WHERE data = ? AND utilizador = ?", (data_str, utilizador))
    res = c.fetchone()
    conn.close()
    return res

def salvar_fecho_caixa(data_str, utilizador, feito, entregue):
    saldo = entregue - feito
    data_registo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO fecho_caixa (data, utilizador, valor_feito, valor_entregue, saldo, data_registo)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(data, utilizador) DO UPDATE SET
            valor_feito = excluded.valor_feito,
            valor_entregue = excluded.valor_entregue,
            saldo = excluded.saldo,
            data_registo = excluded.data_registo
    ''', (data_str, utilizador, feito, entregue, saldo, data_registo))
    conn.commit()
    conn.close()

# OPERAÇÕES CRUD (SUPERVISORES E AGENTES)
def cadastrar_supervisor(nome):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO supervisores (nome) VALUES (?)", (nome,))
        conn.commit()
        res = True
    except sqlite3.IntegrityError:
        res = False
    conn.close()
    return res

def editar_supervisor(sup_id, novo_nome):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("UPDATE supervisores SET nome = ? WHERE id = ?", (novo_nome, sup_id))
        conn.commit()
        res = True
    except sqlite3.IntegrityError:
        res = False
    conn.close()
    return res

def apagar_supervisor(sup_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE agentes SET supervisor_id = NULL WHERE supervisor_id = ?", (sup_id,))
    c.execute("DELETE FROM supervisores WHERE id = ?", (sup_id,))
    conn.commit()
    conn.close()

def cadastrar_agente(nome, utilizador, supervisor_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO agentes (nome, utilizador, supervisor_id) VALUES (?, ?, ?)", (nome, utilizador, supervisor_id))
        conn.commit()
        res = True
    except sqlite3.IntegrityError:
        res = False
    conn.close()
    return res

def editar_agente(agente_id, novo_nome, novo_utilizador, novo_sup_id, novo_estado):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("UPDATE agentes SET nome = ?, utilizador = ?, supervisor_id = ?, estado = ? WHERE id = ?", 
                  (novo_nome, novo_utilizador, novo_sup_id, novo_estado, agente_id))
        conn.commit()
        res = True
    except sqlite3.IntegrityError:
        res = False
    conn.close()
    return res

def apagar_agente(agente_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM agentes WHERE id = ?", (agente_id,))
    conn.commit()
    conn.close()

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
col_top1, col_top2 = st.columns([5, 1])
with col_top1:
    st.title("⚽ Operação de Caixa Bet77")
with col_top2:
    if st.button("🚪 Sair"):
        st.session_state["autenticado"] = False
        st.rerun()

st.divider()

# NAVEGAÇÃO POR ABAS
tab_operacao, tab_gestao = st.tabs(["📥 Lançamento & Fecho de Caixa", "⚙️ Gestão de Supervisores e Agentes"])

# ------------------------------------------
# ABA 1: OPERAÇÃO E FECHO DE CAIXA
# ------------------------------------------
with tab_operacao:
    col_data, col_sup = st.columns([1, 2])

    with col_data:
        data_operacao = st.date_input("1. Data da Operação", datetime.now())
        data_str = data_operacao.strftime("%Y-%m-%d")

    df_sups = carregar_supervisores()

    with col_sup:
        # Monta as opções do Selectbox incluindo a opção "TODOS"
        sup_map = {"🌐 Todos os Supervisores": "TODOS"}
        for _, r in df_sups.iterrows():
            sup_map[r['nome']] = r['id']

        sup_selecionado_nome = st.selectbox("2. Selecione o Supervisor / Rota", list(sup_map.keys()))
        sup_id_selecionado = sup_map[sup_selecionado_nome]

    st.divider()

    # Carrega os agentes com base na escolha
    df_agentes = carregar_agentes_por_supervisor(sup_id_selecionado)

    if df_agentes.empty:
        st.info("Nenhum agente ativo encontrado para esta seleção.")
    else:
        st.subheader(f"📋 Painel de Fecho de Caixa — {sup_selecionado_nome}")
        
        # Cabeçalho da Tabela (Inclui a coluna 'Supervisor' se "Todos" for selecionado)
        if sup_id_selecionado == "TODOS":
            c_sup, c_ag, c_feito, c_ent, c_saldo, c_acao = st.columns([1.2, 1.8, 1.5, 1.5, 1.5, 1.5])
            with c_sup: st.markdown("**SUPERVISOR**")
        else:
            c_ag, c_feito, c_ent, c_saldo, c_acao = st.columns([2, 1.5, 1.5, 1.5, 1.5])

        with c_ag: st.markdown("**AGENTE**")
        with c_feito: st.markdown("**VALOR DIÁRIO FEITO (MT)**")
        with c_ent: st.markdown("**VALOR ENTREGUE (MT)**")
        with c_saldo: st.markdown("**SALDO / PENDÊNCIA**")
        with c_acao: st.markdown("**AÇÃO**")

        tot_feito = 0.0
        tot_entregue = 0.0

        # Exibição de cada Agente
        for _, ag in df_agentes.iterrows():
            fecho = obter_fecho_existente(data_str, ag['utilizador'])
            val_feito_ini = fecho[0] if fecho else 0.0
            val_ent_ini = fecho[1] if fecho else 0.0
            ja_fechado = fecho is not None

            if sup_id_selecionado == "TODOS":
                c_sup, c_ag, c_feito, c_ent, c_saldo, c_acao = st.columns([1.2, 1.8, 1.5, 1.5, 1.5, 1.5])
                with c_sup:
                    st.markdown(f"<span style='color:#475569; font-weight:600;'>{ag['supervisor_nome']}</span>", unsafe_allow_html=True)
            else:
                c_ag, c_feito, c_ent, c_saldo, c_acao = st.columns([2, 1.5, 1.5, 1.5, 1.5])

            with c_ag:
                st.markdown(f"<strong style='color:#0F172A; font-size: 1.05rem;'>{ag['nome']}</strong><br><small style='color:#64748B;'>{ag['utilizador']}</small>", unsafe_allow_html=True)

            with c_feito:
                v_feito = st.number_input(
                    "Feito", min_value=0.0, step=50.0, value=float(val_feito_ini),
                    key=f"feito_{ag['id']}_{data_str}", label_visibility="collapsed"
                )

            with c_ent:
                v_entregue = st.number_input(
                    "Entregue", min_value=0.0, step=50.0, value=float(val_ent_ini),
                    key=f"ent_{ag['id']}_{data_str}", label_visibility="collapsed"
                )

            saldo_linha = v_entregue - v_feito
            tot_feito += v_feito
            tot_entregue += v_entregue

            with c_saldo:
                if saldo_linha < 0:
                    st.markdown(f"<h4 class='valor-negativo' style='margin:0;'>{saldo_linha:,.2f} MT</h4>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<h4 class='valor-zero' style='margin:0;'>{saldo_linha:,.2f} MT</h4>", unsafe_allow_html=True)

            with c_acao:
                label_btn = "✅ Caixa Fechado" if ja_fechado else "🔒 Fechar Caixa"
                tipo_btn = "secondary" if ja_fechado else "primary"
                
                if st.button(label_btn, key=f"btn_{ag['id']}_{data_str}", type=tipo_btn):
                    salvar_fecho_caixa(data_str, ag['utilizador'], v_feito, v_entregue)
                    st.toast(f"Caixa de {ag['utilizador']} salvo com sucesso!", icon="🔒")
                    st.rerun()

        st.divider()

        # Resumo Geral
        st.subheader(f"📊 Resumo Geral do Diário ({sup_selecionado_nome})")
        tot_saldo = tot_entregue - tot_feito
        
        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown(f"<div class='card-resumo'><span>TOTAL FEITO</span><h3 style='color:#1E3A8A;'>{tot_feito:,.2f} MT</h3></div>", unsafe_allow_html=True)
        with r2:
            st.markdown(f"<div class='card-resumo'><span>TOTAL ENTREGUE</span><h3 style='color:#059669;'>{tot_entregue:,.2f} MT</h3></div>", unsafe_allow_html=True)
        with r3:
            cor_txt = "#DC2626" if tot_saldo < 0 else "#16A34A"
            st.markdown(f"<div class='card-resumo'><span>SALDO PENDENTE</span><h3 style='color:{cor_txt};'>{tot_saldo:,.2f} MT</h3></div>", unsafe_allow_html=True)

# ------------------------------------------
# ABA 2: GESTÃO DE SUPERVISORES E AGENTES
# ------------------------------------------
with tab_gestao:
    st.subheader("⚙️ Gestão de Rede")
    
    subtab_sup, subtab_ag = st.tabs(["📌 Supervisores", "👤 Agentes"])
    
    # 1. GESTÃO DE SUPERVISORES
    with subtab_sup:
        c_sup1, c_sup2 = st.columns(2)
        
        with c_sup1:
            st.write("➕ **Cadastrar Novo Supervisor**")
            with st.form("form_novo_sup", clear_on_submit=True):
                novo_sup_nome = st.text_input("Nome do Supervisor:")
                if st.form_submit_button("💾 Salvar Supervisor", use_container_width=True):
                    if novo_sup_nome.strip():
                        if cadastrar_supervisor(novo_sup_nome.strip()):
                            st.success("Supervisor adicionado!")
                            st.rerun()
                        else:
                            st.error("Nome de supervisor já existe.")
                    else:
                        st.error("Digite o nome.")

        with c_sup2:
            st.write("✏️ **Editar ou Apagar Supervisor**")
            df_sups_geral = carregar_supervisores()
            if not df_sups_geral.empty:
                sup_sel_map = {r['nome']: r for _, r in df_sups_geral.iterrows()}
                sup_escolhido = st.selectbox("Selecione para alterar:", list(sup_sel_map.keys()))
                sup_d = sup_sel_map[sup_escolhido]
                
                edit_sup_nome = st.text_input("Editar Nome:", value=sup_d['nome'])
                
                col_btn_sup1, col_btn_sup2 = st.columns(2)
                with col_btn_sup1:
                    if st.button("💾 Guardar Alteração", key="btn_edit_sup"):
                        if editar_supervisor(sup_d['id'], edit_sup_nome.strip()):
                            st.success("Atualizado com sucesso!")
                            st.rerun()
                with col_btn_sup2:
                    if st.button("🚨 Apagar Supervisor", type="primary", key="btn_del_sup"):
                        apagar_supervisor(sup_d['id'])
                        st.success("Supervisor removido!")
                        st.rerun()
            else:
                st.info("Nenhum supervisor cadastrado.")
                
        st.divider()
        st.write("📋 **Lista de Supervisores**")
        st.dataframe(carregar_supervisores(), use_container_width=True)

    # 2. GESTÃO DE AGENTES
    with subtab_ag:
        df_sups_para_ag = carregar_supervisores()
        
        st.write("➕ **Cadastrar Novo Agente**")
        if df_sups_para_ag.empty:
            st.warning("Cadastre um supervisor primeiro.")
        else:
            with st.form("form_novo_ag", clear_on_submit=True):
                c_ag1, c_ag2 = st.columns(2)
                with c_ag1:
                    ag_nome = st.text_input("Nome do Agente (ex: Rabeca):")
                    ag_code = st.text_input("Código Utilizador (ex: bet77 18):")
                with c_ag2:
                    s_map_ag = {r['nome']: r['id'] for _, r in df_sups_para_ag.iterrows()}
                    ag_sup = st.selectbox("Associar ao Supervisor:", list(s_map_ag.keys()))
                
                if st.form_submit_button("💾 Salvar Agente", use_container_width=True):
                    if ag_nome.strip() and ag_code.strip():
                        if cadastrar_agente(ag_nome.strip(), ag_code.strip(), s_map_ag[ag_sup]):
                            st.success("Agente adicionado!")
                            st.rerun()
                        else:
                            st.error("Este código de utilizador já existe.")
                    else:
                        st.error("Preencha todos os campos.")

        st.divider()
        
        st.write("✏️ **Editar ou Apagar Agente**")
        df_ag_todos = carregar_agentes_por_supervisor("TODOS")
        if not df_ag_todos.empty:
            ag_map_sel = {f"{r['utilizador']} - {r['nome']} ({r['supervisor_nome']})": r for _, r in df_ag_todos.iterrows()}
            ag_escolhido = st.selectbox("Selecione o Agente:", list(ag_map_sel.keys()))
            ag_d = ag_map_sel[ag_escolhido]
            
            c_e1, c_e2, c_e3 = st.columns(3)
            with c_e1:
                e_ag_nome = st.text_input("Nome:", value=ag_d['nome'], key="e_ag_nome")
                e_ag_code = st.text_input("Código Utilizador:", value=ag_d['utilizador'], key="e_ag_code")
            with c_e2:
                sup_opts = {r['nome']: r['id'] for _, r in df_sups_para_ag.iterrows()}
                idx_sup_atual = list(sup_opts.values()).index(ag_d['supervisor_id']) if ag_d['supervisor_id'] in sup_opts.values() else 0
                e_ag_sup = st.selectbox("Supervisor / Rota:", list(sup_opts.keys()), index=idx_sup_atual, key="e_ag_sup")
            with c_e3:
                idx_est = 0 if ag_d['estado'] == 'Activo' else 1
                e_ag_estado = st.selectbox("Status:", ["Activo", "Bloqueado"], index=idx_est, key="e_ag_est")

            col_bag1, col_bag2 = st.columns(2)
            with col_bag1:
                if st.button("💾 Atualizar Dados do Agente", use_container_width=True):
                    if editar_agente(ag_d['id'], e_ag_nome.strip(), e_ag_code.strip(), sup_opts[e_ag_sup], e_ag_estado):
                        st.success("Agente atualizado!")
                        st.rerun()
                    else:
                        st.error("Código de utilizador já pertence a outro agente.")
            with col_bag2:
                if st.button("🚨 Apagar Agente", type="primary", use_container_width=True):
                    apagar_agente(ag_d['id'])
                    st.success("Agente removido!")
                    st.rerun()
        else:
            st.info("Nenhum agente cadastrado.")

        st.divider()
        st.write("📋 **Lista Geral de Agentes**")
        st.dataframe(df_ag_todos[['id', 'nome', 'utilizador', 'supervisor_nome', 'estado']], use_container_width=True)