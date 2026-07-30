import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
import os

# ==========================================
# CONFIGURAÇÃO DE PÁGINA E CSS PROFISSIONAL
# ==========================================
st.set_page_config(page_title="Caixa de Esportes Bet77", layout="wide", page_icon="⚽")

st.markdown("""
    <style>
    /* Estilo Geral da Aplicação */
    .stApp {
        background-color: #F8FAFC !important;
        color: #1E293B !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Títulos compactos e modernos */
    h1 {
        font-size: 1.6rem !important;
        color: #0F172A !important;
        font-weight: 700 !important;
    }
    h2, h3 {
        font-size: 1.2rem !important;
        color: #1E3A8A !important;
        font-weight: 600 !important;
    }
    
    /* Linha de Agente com divisor e efeito Hover */
    .linha-agente {
        padding: 8px 12px;
        border-bottom: 1px solid #E2E8F0;
        border-radius: 6px;
        transition: background-color 0.15s ease-in-out;
    }
    .linha-agente:hover {
        background-color: #F1F5F9;
    }

    /* Rótulos e Texto dos Agentes */
    .nome-agente {
        font-size: 0.92rem !important;
        font-weight: 600;
        color: #0F172A;
    }
    .codigo-agente {
        font-size: 0.78rem !important;
        color: #64748B;
    }
    .header-tabela {
        font-size: 0.8rem !important;
        font-weight: 700;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-bottom: 2px solid #CBD5E1;
        padding-bottom: 6px;
        margin-bottom: 6px;
    }

    /* Cards de Resumo */
    .card-resumo {
        background-color: #FFFFFF;
        padding: 12px 16px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        text-align: center;
    }
    .card-resumo span {
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
    }
    .card-resumo h3 {
        margin-top: 4px;
        margin-bottom: 0;
        font-size: 1.25rem !important;
    }

    /* Destaques de Valores */
    .valor-negativo {
        color: #DC2626 !important;
        font-weight: 700;
        font-size: 0.95rem !important;
    }
    .valor-zero {
        color: #16A34A !important;
        font-weight: 700;
        font-size: 0.95rem !important;
    }

    /* Campos de Entrada Compactos */
    div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        border-radius: 5px !important;
        min-height: 38px !important;
    }
    input {
        font-size: 0.9rem !important;
    }

    /* Botões */
    div.stButton > button {
        border-radius: 5px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        height: 38px !important;
        width: 100% !important;
    }
    
    /* Abas Superioras */
    button[data-baseweb="tab"] {
        font-size: 0.9rem !important;
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

    c.execute("SELECT COUNT(*) FROM supervisores")
    if c.fetchone()[0] == 0:
        estrutura_rede = {
            "Telma": [
                ("Assane", "bet77 79"), ("Oscar", "bet77 51"), ("Teresa", "bet77 76"),
                ("Alvaro", "bet77 75"), ("Samuel", "bet77 60"), ("Germanio", "bet77 74"),
                ("Amancio", "bet77 69"), ("Elton", "bet77 82"), ("Minesio", "bet77 49")
            ],
            "Pedro": [
                ("Marcos", "bet77 55"), ("Osvaldo", "bet77 12"), ("Argentina Emílio", "bet77 44"),
                ("Meque", "bet77 78"), ("Rabeca", "bet77 11"), ("Delfina Nhanombe", "bet77 01"),
                ("Antonio Issa", "bet77 19"), ("Aurelio", "bet77 80"), ("Cristovao", "bet77 14"),
                ("Dinarcia", "bet77 88"), ("Lino", "bet77 58"), ("Ordito", "bet77 15"),
                ("Mariana", "bet77 31")
            ],
            "Paulo": [
                ("Amisse", "bet77 06"), ("Aron", "bet77 34"), ("Cristina", "bet77 56"),
                ("Elton Muhosse", "bet77 17"), ("Ernesto", "bet77 86"), ("Joaquim Macucule", "bet77 68"),
                ("Marquezinho", "bet77 45"), ("Meque", "bet77 83"), ("Nilza", "bet77 36"),
                ("Silvia", "bet77 13"), ("Silvio", "bet77 09")
            ],
            "Eduardo": [
                ("Joao", "bet77 42"), ("Artur", "bet77 41"), ("Horacio", "bet77 61"),
                ("Fina", "bet77 54"), ("Everton", "bet77 81"), ("Jeremias", "bet77 59"),
                ("Helio", "bet77 43")
            ],
            "Diolinda": [
                ("Bercia", "bet77 30"), ("Victor", "bet77 07"), ("Admira", "bet77 71"),
                ("Admiro", "bet77 65"), ("Alberto", "bet77 47"), ("Angela", "bet77 20"),
                ("Joaquim Juliao", "bet77 08"), ("Lucia", "bet77 72"), ("Martins", "bet77 10"),
                ("Niyurica", "bet77 92"), ("Messias", "bet77 21")
            ],
            "Custodio": [
                ("Castelo", "bet77 93"), ("Aires Mucavel", "bet77 05"), ("Helio Gove", "bet77 62"),
                ("Cardina", "bet77 91"), ("Maria", "bet77 02"), ("Rui", "bet77 37"),
                ("Arnaldo", "bet77 77"), ("Celio", "bet77 03"), ("Gito", "bet77 73"),
                ("Nelson", "bet77 46")
            ],
            "Adelia": [
                ("Airina", "bet77 23"), ("Albino", "bet77 67"), ("Manuel", "bet77 26"),
                ("Abel", "bet77 63"), ("Wilson", "bet77 90"), ("Julio", "bet77 85"),
                ("Sofia", "bet77 24"), ("Antonio Macamo", "bet77 48"), ("Crimilda", "bet77 22"),
                ("Doliz", "bet77 16"), ("Nelia", "bet77 66"), ("Teresa", "bet77 35")
            ],
            "Albertina": [
                ("Antonio", "bet77 52"), ("Batista Ruco", "bet77 27"), ("Elaercia", "bet77 84"),
                ("Felismina", "bet77 50"), ("Francelino", "bet77 28"), ("Isabel", "bet77 33"),
                ("Jeremias", "bet77 29"), ("Rabeca", "bet77 18"), ("Rosa", "bet77 53"),
                ("Sergio", "bet77 32"), ("Silva", "bet77 40")
            ]
        }

        for sup_nome, lista_agentes in estrutura_rede.items():
            c.execute("INSERT INTO supervisores (nome) VALUES (?)", (sup_nome,))
            sup_id = c.lastrowid
            for ag_nome, ag_code in lista_agentes:
                c.execute("INSERT OR IGNORE INTO agentes (nome, utilizador, supervisor_id) VALUES (?, ?, ?)", 
                          (ag_nome, ag_code, sup_id))
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

def obter_dividas_acumuladas(data_str=None, supervisor_id=None):
    conn = sqlite3.connect(DB_FILE)
    params = []
    where_clauses = ["f.saldo < 0"]
    
    if data_str:
        where_clauses.append("f.data = ?")
        params.append(data_str)
        
    if supervisor_id and supervisor_id != "TODOS":
        where_clauses.append("a.supervisor_id = ?")
        params.append(supervisor_id)
        
    where_str = " WHERE " + " AND ".join(where_clauses)
    
    query = f"""
        SELECT 
            COALESCE(s.nome, 'Sem Supervisor') as supervisor,
            a.nome as agente_nome,
            f.utilizador as codigo,
            f.valor_feito as feito,
            f.valor_entregue as entregue,
            f.saldo as divida,
            f.data as data_operacao
        FROM fecho_caixa f
        JOIN agentes a ON f.utilizador = a.utilizador
        LEFT JOIN supervisores s ON a.supervisor_id = s.id
        {where_str}
        ORDER BY s.nome, a.nome
    """
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

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

# OPERAÇÕES CRUD
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
tab_dividas, tab_operacao, tab_gestao = st.tabs([
    "📌 Visão Geral de Dívidas", 
    "📥 Lançamento & Fecho de Caixa", 
    "⚙️ Gestão de Network"
])

# ------------------------------------------
# ABA 1: VISÃO GERAL DE DÍVIDAS (LAYOUT LIMPO)
# ------------------------------------------
with tab_dividas:
    st.subheader("🔴 Painel Geral de Agentes com Dívidas")
    
    col_d_data, col_d_sup = st.columns([1, 2])
    
    with col_d_data:
        data_divida = st.date_input("Data da Operação:", datetime.now(), key="dt_divida")
        dt_div_str = data_divida.strftime("%Y-%m-%d")

    df_sups_d = carregar_supervisores()
    with col_d_sup:
        sup_map_d = {"🌐 Todos os Supervisores": "TODOS"}
        for _, r in df_sups_d.iterrows():
            sup_map_d[r['nome']] = r['id']
            
        sup_div_nome = st.selectbox("Filtrar por Supervisor:", list(sup_map_d.keys()), key="sup_div")
        sup_div_id = sup_map_d[sup_div_nome]

    df_dividas = obter_dividas_acumuladas(data_str=dt_div_str, supervisor_id=sup_div_id)

    if df_dividas.empty:
        st.info(f"Nenhuma pendência registada para {data_divida.strftime('%d/%m/%Y')}.")
    else:
        tot_divida = df_dividas["divida"].sum()
        qtd_devedores = len(df_dividas)

        card1, card2 = st.columns(2)
        with card1:
            st.markdown(f"<div class='card-resumo'><span>QUANTIDADE DE DEVEDORES</span><h3 style='color:#DC2626;'>{qtd_devedores} Agentes</h3></div>", unsafe_allow_html=True)
        with card2:
            st.markdown(f"<div class='card-resumo'><span>TOTAL DE DÍVIDAS PENDENTES</span><h3 style='color:#DC2626;'>{tot_divida:,.2f} MT</h3></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Cabeçalho compacto
        c_h1, c_h2, c_h3, c_h4, c_h5, c_h6 = st.columns([1.5, 2, 1.2, 1.2, 1.2, 1.5])
        with c_h1: st.markdown("<div class='header-tabela'>Supervisor</div>", unsafe_allow_html=True)
        with c_h2: st.markdown("<div class='header-tabela'>Agente</div>", unsafe_allow_html=True)
        with c_h3: st.markdown("<div class='header-tabela'>Código</div>", unsafe_allow_html=True)
        with c_h4: st.markdown("<div class='header-tabela'>Feito (MT)</div>", unsafe_allow_html=True)
        with c_h5: st.markdown("<div class='header-tabela'>Entregue (MT)</div>", unsafe_allow_html=True)
        with c_h6: st.markdown("<div class='header-tabela'>Dívida</div>", unsafe_allow_html=True)

        # Tabela com linhas divisórias
        for _, row in df_dividas.iterrows():
            c1, c2, c3, c4, c5, c6 = st.columns([1.5, 2, 1.2, 1.2, 1.2, 1.5])
            with c1: st.markdown(f"<span style='color:#475569; font-size:0.88rem;'>{row['supervisor']}</span>", unsafe_allow_html=True)
            with c2: st.markdown(f"<span class='nome-agente'>{row['agente_nome']}</span>", unsafe_allow_html=True)
            with c3: st.markdown(f"<span class='codigo-agente'>{row['codigo']}</span>", unsafe_allow_html=True)
            with c4: st.markdown(f"<span style='font-size:0.88rem;'>{row['feito']:,.2f}</span>", unsafe_allow_html=True)
            with c5: st.markdown(f"<span style='font-size:0.88rem;'>{row['entregue']:,.2f}</span>", unsafe_allow_html=True)
            with c6: st.markdown(f"<span class='valor-negativo'>{row['divida']:,.2f} MT</span>", unsafe_allow_html=True)
            st.markdown("<div style='border-bottom: 1px solid #E2E8F0; margin: 4px 0;'></div>", unsafe_allow_html=True)

# ------------------------------------------
# ABA 2: OPERAÇÃO DE CAIXA (COM SEPARADORES)
# ------------------------------------------
with tab_operacao:
    col_data, col_sup = st.columns([1, 2])

    with col_data:
        data_operacao = st.date_input("1. Data da Operação", datetime.now(), key="dt_operacao")
        data_str = data_operacao.strftime("%Y-%m-%d")

    df_sups = carregar_supervisores()

    with col_sup:
        sup_map = {"🌐 Todos os Supervisores": "TODOS"}
        for _, r in df_sups.iterrows():
            sup_map[r['nome']] = r['id']

        sup_selecionado_nome = st.selectbox("2. Selecione o Supervisor / Rota", list(sup_map.keys()), key="sup_op")
        sup_id_selecionado = sup_map[sup_selecionado_nome]

    st.divider()

    df_agentes = carregar_agentes_por_supervisor(sup_id_selecionado)

    if df_agentes.empty:
        st.info("Nenhum agente ativo encontrado.")
    else:
        st.subheader(f"📋 Painel de Fecho de Caixa — {sup_selecionado_nome}")
        
        # Cabeçalhos compactos
        if sup_id_selecionado == "TODOS":
            c_sup, c_ag, c_feito, c_ent, c_saldo, c_acao = st.columns([1.2, 1.8, 1.5, 1.5, 1.5, 1.5])
            with c_sup: st.markdown("<div class='header-tabela'>Supervisor</div>", unsafe_allow_html=True)
        else:
            c_ag, c_feito, c_ent, c_saldo, c_acao = st.columns([2, 1.5, 1.5, 1.5, 1.5])

        with c_ag: st.markdown("<div class='header-tabela'>Agente</div>", unsafe_allow_html=True)
        with c_feito: st.markdown("<div class='header-tabela'>Feito (MT)</div>", unsafe_allow_html=True)
        with c_ent: st.markdown("<div class='header-tabela'>Entregue (MT)</div>", unsafe_allow_html=True)
        with c_saldo: st.markdown("<div class='header-tabela'>Saldo / Pendência</div>", unsafe_allow_html=True)
        with c_acao: st.markdown("<div class='header-tabela'>Ação</div>", unsafe_allow_html=True)

        tot_feito = 0.0
        tot_entregue = 0.0

        for _, ag in df_agentes.iterrows():
            fecho = obter_fecho_existente(data_str, ag['utilizador'])
            val_feito_ini = fecho[0] if fecho else 0.0
            val_ent_ini = fecho[1] if fecho else 0.0
            ja_fechado = fecho is not None

            if sup_id_selecionado == "TODOS":
                c_sup, c_ag, c_feito, c_ent, c_saldo, c_acao = st.columns([1.2, 1.8, 1.5, 1.5, 1.5, 1.5])
                with c_sup:
                    st.markdown(f"<span style='color:#475569; font-size:0.85rem; font-weight:600;'>{ag['supervisor_nome']}</span>", unsafe_allow_html=True)
            else:
                c_ag, c_feito, c_ent, c_saldo, c_acao = st.columns([2, 1.5, 1.5, 1.5, 1.5])

            with c_ag:
                st.markdown(f"<span class='nome-agente'>{ag['nome']}</span><br><span class='codigo-agente'>{ag['utilizador']}</span>", unsafe_allow_html=True)

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
                    st.markdown(f"<span class='valor-negativo'>{saldo_linha:,.2f} MT</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span class='valor-zero'>{saldo_linha:,.2f} MT</span>", unsafe_allow_html=True)

            with c_acao:
                label_btn = "✅ Fechado" if ja_fechado else "🔒 Fechar"
                tipo_btn = "secondary" if ja_fechado else "primary"
                
                if st.button(label_btn, key=f"btn_{ag['id']}_{data_str}", type=tipo_btn):
                    salvar_fecho_caixa(data_str, ag['utilizador'], v_feito, v_entregue)
                    st.toast(f"Caixa de {ag['utilizador']} salvo!", icon="🔒")
                    st.rerun()

            # Linha divisória fina para cada agente
            st.markdown("<div style='border-bottom: 1px solid #E2E8F0; margin: 4px 0 8px 0;'></div>", unsafe_allow_html=True)

        st.divider()

        # Resumos em cartões compactos
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
# ABA 3: GESTÃO DE SUPERVISORES E AGENTES
# ------------------------------------------
with tab_gestao:
    st.subheader("⚙️ Gestão de Rede")
    
    subtab_sup, subtab_ag = st.tabs(["📌 Supervisores", "👤 Agentes"])
    
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