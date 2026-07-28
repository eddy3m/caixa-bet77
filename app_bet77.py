import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
from PIL import Image
import numpy as np
import os
import re

# Importação segura do EasyOCR
ocr_disponivel = False
easyocr = None

try:
    import easyocr
    ocr_disponivel = True
except Exception:
    ocr_disponivel = False

# ==========================================
# CONFIGURAÇÃO DE SEGURANÇA E CÓDIGO DE ACESSO
# ==========================================
# Podes alterar a tua palavra-passe na linha abaixo:
CODIGO_ACESSO_CORRETO = "E2605"

def verificar_autenticacao():
    """Gere a verificação da palavra-passe antes de dar acesso à app."""
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if os.path.exists("logo.png"):
                st.image("logo.png", use_container_width=True)
            else:
                st.markdown("<h2 style='text-align: center;'>⚽ Caixa de Esportes Bet77</h2>", unsafe_allow_html=True)
            
            st.subheader("🔒 Acesso Restrito ao Sistema")
            
            with st.form("form_login"):
                codigo_inserido = st.text_input("Introduza o Código de Acesso / Palavra-passe:", type="password")
                btn_entrar = st.form_submit_button("🔑 Entrar no Sistema", use_container_width=True)
                
                if btn_entrar:
                    if codigo_inserido == CODIGO_ACESSO_CORRETO:
                        st.session_state["autenticado"] = True
                        st.success("Acesso concedido!")
                        st.rerun()
                    else:
                        st.error("❌ Código de acesso incorreto! Tente novamente.")
        return False
    return True

# Configuração da Página Web
st.set_page_config(page_title="Caixa de Esportes Bet77 - Gestão Financeira", layout="wide", page_icon="⚽")

# Se não estiver autenticado, interrompe o carregamento do resto do aplicativo
if not verificar_autenticacao():
    st.stop()

# ==========================================
# ESTILIZAÇÃO CSS (TEMA CLARO DE ALTO CONTRASTE)
# ==========================================
st.markdown("""
    <style>
    .stApp {
        background-color: #F1F5F9;
        color: #0F172A;
    }
    h1 {
        color: #1E3A8A !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700 !important;
    }
    h2, h3 {
        color: #0F172A !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 600 !important;
    }
    p, label, span {
        color: #1E293B !important;
    }
    div.stButton > button:first-child {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #1D4ED8 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    div.stButton > button[kind="primary"] {
        background-color: #DC2626 !important;
        color: #FFFFFF !important;
    }
    .stForm, div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        padding: 20px !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
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
# BASE DE DADOS AUTOMÁTICA
# ==========================================
def init_db():
    conn = sqlite3.connect('caixa_bet77_database.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS supervisores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            estado TEXT DEFAULT 'Activo'
        )
    ''')
    try:
        c.execute("ALTER TABLE supervisores ADD COLUMN estado TEXT DEFAULT 'Activo'")
    except sqlite3.OperationalError:
        pass
    
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
    try:
        c.execute("ALTER TABLE agentes ADD COLUMN estado TEXT DEFAULT 'Activo'")
    except sqlite3.OperationalError:
        pass
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            utilizador TEXT NOT NULL,
            valor_recebido REAL DEFAULT 0.0,
            valor_por_pagar REAL DEFAULT 0.0,
            data_registo TEXT NOT NULL,
            FOREIGN KEY (utilizador) REFERENCES agentes (utilizador)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# ==========================================
# FUNÇÕES OCR
# ==========================================
@st.cache_resource
def carregar_leitor_ocr():
    if ocr_disponivel and easyocr is not None:
        return easyocr.Reader(['pt', 'en'], gpu=False)
    return None

def extrair_dados_imagem(imagem_pil):
    reader = carregar_leitor_ocr()
    if not reader:
        return "", None, []
        
    img_array = np.array(imagem_pil)
    resultados = reader.readtext(img_array, detail=0)
    texto_completo = " ".join(resultados)
    
    match_utilizador = re.search(r'(bet77[\s_-]?\d+)', texto_completo, re.IGNORECASE)
    utilizador_detetado = match_utilizador.group(1).replace("_", " ").lower() if match_utilizador else None
    
    numeros = re.findall(r'\b\d+(?:[\.,]\d+)?\b', texto_completo)
    valores_encontrados = []
    for num in numeros:
        try:
            val = float(num.replace(',', '.'))
            if val > 0:
                valores_encontrados.append(val)
        except ValueError:
            pass
            
    return texto_completo, utilizador_detetado, valores_encontrados

# ==========================================
# FUNÇÕES BD
# ==========================================
def carregar_supervisores(apenas_activos=False):
    conn = sqlite3.connect('caixa_bet77_database.db')
    where = "WHERE estado IS NULL OR estado = 'Activo'" if apenas_activos else ""
    query = f"SELECT id, nome, COALESCE(estado, 'Activo') as estado FROM supervisores {where} ORDER BY nome"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def carregar_agentes(supervisor_id=None, apenas_activos=False):
    conn = sqlite3.connect('caixa_bet77_database.db')
    conditions = []
    params = []
    
    if supervisor_id is not None:
        conditions.append("a.supervisor_id = ?")
        params.append(int(supervisor_id))
    if apenas_activos:
        conditions.append("(a.estado IS NULL OR a.estado = 'Activo')")
        
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    
    query = f'''
        SELECT a.id, a.nome, a.utilizador, a.supervisor_id, 
               COALESCE(a.estado, 'Activo') as estado, 
               s.nome as supervisor 
        FROM agentes a
        LEFT JOIN supervisores s ON a.supervisor_id = s.id
        {where_clause}
        ORDER BY a.utilizador
    '''
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def registar_venda(data_venda, utilizador, valor_rec, valor_pag):
    conn = sqlite3.connect('caixa_bet77_database.db')
    c = conn.cursor()
    data_registo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO vendas (data, utilizador, valor_recebido, valor_por_pagar, data_registo)
        VALUES (?, ?, ?, ?, ?)
    ''', (data_venda, utilizador, valor_rec, valor_pag, data_registo))
    conn.commit()
    conn.close()

def atualizar_venda(venda_id, nova_data, novo_utilizador, novo_val_rec, novo_val_pag):
    conn = sqlite3.connect('caixa_bet77_database.db')
    c = conn.cursor()
    c.execute('''
        UPDATE vendas 
        SET data = ?, utilizador = ?, valor_recebido = ?, valor_por_pagar = ? 
        WHERE id = ?
    ''', (nova_data, novo_utilizador, novo_val_rec, novo_val_pag, venda_id))
    conn.commit()
    conn.close()

def apagar_venda(venda_id):
    conn = sqlite3.connect('caixa_bet77_database.db')
    c = conn.cursor()
    c.execute('DELETE FROM vendas WHERE id = ?', (venda_id,))
    conn.commit()
    conn.close()

def cadastrar_supervisor(nome, estado="Activo"):
    conn = sqlite3.connect('caixa_bet77_database.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO supervisores (nome, estado) VALUES (?, ?)', (nome, estado))
        conn.commit()
        sucesso = True
    except sqlite3.IntegrityError:
        sucesso = False
    conn.close()
    return sucesso

def cadastrar_agente(nome, utilizador, supervisor_id, estado="Activo"):
    conn = sqlite3.connect('caixa_bet77_database.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO agentes (nome, utilizador, supervisor_id, estado) VALUES (?, ?, ?, ?)', 
                  (nome, utilizador, supervisor_id, estado))
        conn.commit()
        sucesso = True
    except sqlite3.IntegrityError:
        sucesso = False
    conn.close()
    return sucesso

def atualizar_supervisor(supervisor_id, novo_nome, novo_estado):
    conn = sqlite3.connect('caixa_bet77_database.db')
    c = conn.cursor()
    try:
        c.execute('UPDATE supervisores SET nome = ?, estado = ? WHERE id = ?', (novo_nome, novo_estado, supervisor_id))
        conn.commit()
        sucesso = True
    except sqlite3.IntegrityError:
        sucesso = False
    conn.close()
    return sucesso

def atualizar_agente(agente_id, novo_nome, novo_utilizador, novo_supervisor_id, novo_estado):
    conn = sqlite3.connect('caixa_bet77_database.db')
    c = conn.cursor()
    try:
        c.execute('''
            UPDATE agentes 
            SET nome = ?, utilizador = ?, supervisor_id = ?, estado = ? 
            WHERE id = ?
        ''', (novo_nome, novo_utilizador, novo_supervisor_id, novo_estado, agente_id))
        conn.commit()
        sucesso = True
    except sqlite3.IntegrityError:
        sucesso = False
    conn.close()
    return sucesso

def atualizar_estado_por_utilizador(utilizador, novo_estado):
    conn = sqlite3.connect('caixa_bet77_database.db')
    c = conn.cursor()
    c.execute('UPDATE agentes SET estado = ? WHERE utilizador = ?', (novo_estado, utilizador))
    conn.commit()
    conn.close()

def apagar_agente(agente_id):
    conn = sqlite3.connect('caixa_bet77_database.db')
    c = conn.cursor()
    c.execute('DELETE FROM agentes WHERE id = ?', (agente_id,))
    conn.commit()
    conn.close()

def apagar_supervisor(supervisor_id):
    conn = sqlite3.connect('caixa_bet77_database.db')
    c = conn.cursor()
    c.execute('UPDATE agentes SET supervisor_id = NULL WHERE supervisor_id = ?', (supervisor_id,))
    c.execute('DELETE FROM supervisores WHERE id = ?', (supervisor_id,))
    conn.commit()
    conn.close()

def carregar_vendas(data_filtro=None):
    conn = sqlite3.connect('caixa_bet77_database.db')
    where = "WHERE v.data = ?" if data_filtro else ""
    params = (data_filtro,) if data_filtro else ()
    
    query = f'''
        SELECT 
            v.id as "ID",
            v.data as "Data Operação",
            COALESCE(s.nome, 'Sem Supervisor') as "Supervisor",
            COALESCE(a.nome, 'Agente Desconhecido') as "Nome Agente",
            v.utilizador as "Utilizador",
            COALESCE(a.estado, 'Activo') as "Estado",
            v.valor_recebido as "Valor Recebido (MT)",
            v.valor_por_pagar as "Valor Por Pagar (MT)",
            (v.valor_recebido - v.valor_por_pagar) as "Saldo Líquido (MT)",
            v.data_registo as "Data e Hora do Registo"
        FROM vendas v
        LEFT JOIN agentes a ON v.utilizador = a.utilizador
        LEFT JOIN supervisores s ON a.supervisor_id = s.id
        {where}
        ORDER BY s.nome, a.utilizador, v.id DESC
    '''
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# ==========================================
# CABEÇALHO DO APLICATIVO COM BOTÃO DE SAIR
# ==========================================
col_top1, col_top2 = st.columns([4, 1])
with col_top2:
    if st.button("🚪 Sair / Terminar Sessão"):
        st.session_state["autenticado"] = False
        st.rerun()

col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
with col_logo2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center;'>⚽ Caixa de Esportes Bet77</h1>", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #475569; font-weight: 600;'>Painel Central de Gestão Financeira e Controlo de Caixa</p>", unsafe_allow_html=True)
st.divider()

tab1, tab2, tab3 = st.tabs(["📊 Balanço & Relatórios Financeiros", "📝 Lançamento de Caixa", "⚙️ Configuração de Agentes e Supervisores"])

# ------------------------------------------
# TAB 1: RELATÓRIOS E VISÃO GERAL
# ------------------------------------------
with tab1:
    st.subheader("📊 Visão Geral e Relatório Financeiro")
    
    col_filtro1, col_filtro2, _ = st.columns([1, 1, 2])
    with col_filtro1:
        data_pesquisa = st.date_input("1. Filtrar por Data", datetime.now(), key="pesquisa_data")
        
    df_vendas_geral = carregar_vendas(data_pesquisa.strftime("%Y-%m-%d"))
    
    with col_filtro2:
        lista_sups = ["Todos"] + list(df_vendas_geral["Supervisor"].unique()) if not df_vendas_geral.empty else ["Todos"]
        sup_filtro = st.selectbox("2. Filtrar por Supervisor", lista_sups)
    
    if sup_filtro != "Todos":
        df_vendas = df_vendas_geral[df_vendas_geral["Supervisor"] == sup_filtro]
    else:
        df_vendas = df_vendas_geral
    
    if not df_vendas.empty:
        tot_recebido = df_vendas["Valor Recebido (MT)"].sum()
        tot_pagar = df_vendas["Valor Por Pagar (MT)"].sum()
        saldo_final = tot_recebido - tot_pagar
        
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 TOTAL RECEBIDO", f"{tot_recebido:,.2f} MT")
        c2.metric("🔻 TOTAL POR PAGAR", f"{tot_pagar:,.2f} MT", delta_color="inverse")
        c3.metric("📊 SALDO LÍQUIDO DO DIA", f"{saldo_final:,.2f} MT")
        
        st.divider()
        
        st.write(f"📌 **Visão Geral: Valor em Dívida e Estado dos Agentes ({sup_filtro})**")
        st.caption("💡 Pode alterar o estado (**Activo** / **Bloqueado**) diretamente na coluna 'Estado' da tabela abaixo:")
        
        df_divida_agentes = df_vendas.groupby(["Nome Agente", "Utilizador", "Estado", "Supervisor"]).agg({
            "Saldo Líquido (MT)": "sum"
        }).reset_index()
        
        df_divida_agentes.rename(columns={"Saldo Líquido (MT)": "Valor em Dívida (MT)"}, inplace=True)
        
        edited_df = st.data_editor(
            df_divida_agentes,
            use_container_width=True,
            disabled=["Nome Agente", "Utilizador", "Supervisor", "Valor em Dívida (MT)"],
            column_config={
                "Estado": st.column_config.SelectboxColumn(
                    "Estado (Clique p/ Alternar)",
                    options=["Activo", "Bloqueado"],
                    required=True,
                    help="Selecione para alternar entre Activo e Bloqueado"
                ),
                "Valor em Dívida (MT)": st.column_config.NumberColumn(format="%.2f MT")
            },
            key="editor_divida_agentes"
        )
        
        for idx, row in edited_df.iterrows():
            if row["Estado"] != df_divida_agentes.loc[idx, "Estado"]:
                atualizar_estado_por_utilizador(row["Utilizador"], row["Estado"])
                st.success(f"✅ Estado do agente **{row['Utilizador']}** alterado para **{row['Estado']}**!")
                st.rerun()

        st.divider()
        
        st.write("🔍 **Detalhamento de Lançamentos**")
        
        supervisores_unicos = df_vendas["Supervisor"].unique()
        
        for sup in supervisores_unicos:
            df_sup_agentes = df_vendas[df_vendas["Supervisor"] == sup]
            sub_saldo = df_sup_agentes["Saldo Líquido (MT)"].sum()
            
            with st.expander(f"📁 **{sup}** — Saldo Total Líquido: **{sub_saldo:,.2f} MT**"):
                df_exibicao = df_sup_agentes.drop(columns=["Supervisor"])
                
                st.dataframe(
                    df_exibicao, 
                    use_container_width=True,
                    column_config={
                        "ID": st.column_config.NumberColumn(format="%d"),
                        "Valor Recebido (MT)": st.column_config.NumberColumn(format="%.2f MT"),
                        "Valor Por Pagar (MT)": st.column_config.NumberColumn(format="%.2f MT"),
                        "Saldo Líquido (MT)": st.column_config.NumberColumn(format="%.2f MT")
                    }
                )
    else:
        st.info(f"Sem registos efetuados para a data {data_pesquisa.strftime('%d/%m/%Y')} e/ou Supervisor selecionado.")

# ------------------------------------------
# TAB 2: LANÇAMENTO DE CAIXA
# ------------------------------------------
with tab2:
    st.subheader("📥 Lançar Operação de Caixa")
    
    modo_lancamento = st.radio("Método de entrada:", ["✍️ Manual", "📸 Leitura por Captura de Ecrã (OCR)"], horizontal=True)
    st.divider()
    
    df_agentes_activos = carregar_agentes(apenas_activos=True)
    
    if df_agentes_activos.empty:
        st.warning("⚠️ Nenhum agente activo cadastrado na base de dados.")
    else:
        if modo_lancamento == "📸 Leitura por Captura de Ecrã (OCR)":
            if not ocr_disponivel:
                st.error("⚠️ O leitor de imagens está temporariamente indisponível.")
            else:
                imagem_uploaded = st.file_uploader("Carregar Captura de Ecrã (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
                
                if imagem_uploaded:
                    img = Image.open(imagem_uploaded)
                    col_img, col_dados = st.columns([1, 1])
                    
                    with col_img:
                        st.image(img, caption="Captura de Ecrã Carregada", use_container_width=True)
                    
                    with col_dados:
                        with st.spinner("A analisar imagem..."):
                            texto_detectado, util_detectado, valores_detectados = extrair_dados_imagem(img)
                        
                        st.success("Análise concluída!")
                        st.caption(f"Texto detetado:_{texto_detectado[:150]}..._")
                        
                        idx_agente = 0
                        if util_detectado:
                            for idx, row in df_agentes_activos.iterrows():
                                if util_detectado.lower() in row['utilizador'].lower():
                                    idx_agente = list(df_agentes_activos['utilizador']).index(row['utilizador'])
                                    st.info(f"💡 Agente **{row['utilizador']}** identificado!")
                                    break
                        
                        val_rec_sugerido = valores_detectados[0] if valores_detectados else 0.0
                        val_pag_sugerido = valores_detectados[1] if len(valores_detectados) > 1 else 0.0
                        
                        with st.form("form_ocr"):
                            dt_ocr = st.date_input("1. Data da Operação", datetime.now())
                            opcoes_ag = [f"{row['utilizador']} — {row['nome']}" for _, row in df_agentes_activos.iterrows()]
                            ag_ocr = st.selectbox("2. Confirmar Agente", opcoes_ag, index=idx_agente)
                            
                            val_rec_ocr = st.number_input("3. Valor Recebido (MT)", value=float(val_rec_sugerido), step=50.0)
                            val_pag_ocr = st.number_input("4. Valor por Pagar (MT)", value=float(val_pag_sugerido), step=50.0)
                            
                            if st.form_submit_button("💾 Confirmar e Salvar no Caixa"):
                                code = ag_ocr.split(" — ")[0]
                                registar_venda(dt_ocr.strftime("%Y-%m-%d"), code, val_rec_ocr, val_pag_ocr)
                                st.success(f"✅ Registo guardado para {code}!")

        else:
            df_supervisores = carregar_supervisores(apenas_activos=True)
            col_sup, _ = st.columns([1, 2])
            with col_sup:
                sup_opcoes = {"Todos os Supervisores": None}
                for _, r in df_supervisores.iterrows():
                    sup_opcoes[r['nome']] = r['id']
                sup_selecionado_nome = st.selectbox("🔍 Filtrar por Supervisor", list(sup_opcoes.keys()))
                sup_selecionado_id = sup_opcoes[sup_selecionado_nome]

            df_agentes_filtrados = carregar_agentes(sup_selecionado_id, apenas_activos=True)

            with st.form("form_vendas_manual", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    data_venda = st.date_input("1. Data da Operação", datetime.now())
                    opcoes_agentes = [f"{row['utilizador']} — {row['nome']}" for _, row in df_agentes_filtrados.iterrows()]
                    agente_selecionado = st.selectbox("2. Selecione o Agente (Activos)", opcoes_agentes)
                
                with col2:
                    valor_recebido = st.number_input("3. Valor Recebido (MT)", min_value=0.0, step=100.0, format="%.2f")
                    valor_por_pagar = st.number_input("4. Valor por Pagar / Prémios (MT)", min_value=0.0, step=100.0, format="%.2f")
                
                btn_submeter = st.form_submit_button("💾 Guardar Lançamento", use_container_width=True)
                
                if btn_submeter:
                    if valor_recebido <= 0 and valor_por_pagar <= 0:
                        st.error("⚠️ Insira pelo menos um valor maior que 0,00 MT.")
                    else:
                        utilizador_code = agente_selecionado.split(" — ")[0]
                        registar_venda(data_venda.strftime("%Y-%m-%d"), utilizador_code, valor_recebido, valor_por_pagar)
                        st.success(f"✅ Registado com sucesso para **{utilizador_code}**!")

# ------------------------------------------
# TAB 3: CONFIGURAÇÃO DE REDE
# ------------------------------------------
with tab3:
    st.subheader("⚙️ Configuração de Agentes e Supervisores")
    
    subtab_sup, subtab_ag, subtab_edit_venda, subtab_del = st.tabs([
        "📌 Gestão de Supervisores", 
        "👤 Gestão de Agentes", 
        "📝 Editar Lançamentos do Caixa", 
        "🗑️ Apagar Registos"
    ])
    
    # 1. SUPERVISORES
    with subtab_sup:
        col_s1, col_s2 = st.columns(2)
        
        with col_s1:
            st.write("➕ **Cadastrar Novo Supervisor**")
            with st.form("form_sup_unificado", clear_on_submit=True):
                nome_sup_novo = st.text_input("1. Nome do Supervisor")
                estado_sup_novo = st.selectbox("2. Estado Inicial", ["Activo", "Bloqueado"])
                
                if st.form_submit_button("➕ Salvar Supervisor", use_container_width=True):
                    if nome_sup_novo.strip():
                        if cadastrar_supervisor(nome_sup_novo.strip(), estado_sup_novo):
                            st.success(f"Supervisor '{nome_sup_novo}' registado com sucesso!")
                            st.rerun()
                        else:
                            st.error("Já existe um supervisor com este nome.")
                    else:
                        st.error("Insira o nome do supervisor.")

        with col_s2:
            st.write("✏️ **Editar / Alterar Supervisor**")
            df_sups_all = carregar_supervisores()
            if not df_sups_all.empty:
                s_map = {f"{r['nome']} ({r['estado']})": r for _, r in df_sups_all.iterrows()}
                s_sel = st.selectbox("1. Selecione o Supervisor para Alterar", list(s_map.keys()))
                s_dados = s_map[s_sel]
                
                s_novo_nome = st.text_input("2. Novo Nome do Supervisor", value=s_dados['nome'])
                idx_est_sup = 0 if s_dados['estado'] == 'Activo' else 1
                s_novo_estado = st.selectbox("3. Estado do Supervisor", ["Activo", "Bloqueado"], index=idx_est_sup, key="est_sup_edit")
                
                if st.button("💾 Atualizar Supervisor", use_container_width=True):
                    if s_novo_nome.strip():
                        if atualizar_supervisor(s_dados['id'], s_novo_nome.strip(), s_novo_estado):
                            st.success("Supervisor atualizado!")
                            st.rerun()
                        else:
                            st.error("Nome indisponível.")
            else:
                st.info("Nenhum supervisor registado.")
                
        st.divider()
        st.write("📋 **Lista Geral de Supervisores**")
        st.dataframe(df_sups_all, use_container_width=True)

    # 2. AGENTES
    with subtab_ag:
        df_sups_disponiveis = carregar_supervisores()
        
        st.write("➕ **Cadastrar Novo Agente**")
        if df_sups_disponiveis.empty:
            st.warning("Crie primeiro um supervisor antes de cadastrar agentes.")
        else:
            with st.form("form_ag_unificado", clear_on_submit=True):
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    nome_ag_novo = st.text_input("1. Nome do Agente")
                    code_ag_novo = st.text_input("2. Código Utilizador (ex: bet77 99)")
                with col_c2:
                    sup_map_cad = {r['nome']: r['id'] for _, r in df_sups_disponiveis.iterrows()}
                    sup_esc_cad = st.selectbox("3. Associar a Supervisor", list(sup_map_cad.keys()))
                    estado_ag_novo = st.selectbox("4. Estado Inicial", ["Activo", "Bloqueado"])
                
                if st.form_submit_button("➕ Salvar Agente", use_container_width=True):
                    if nome_ag_novo.strip() and code_ag_novo.strip():
                        if cadastrar_agente(nome_ag_novo.strip(), code_ag_novo.strip(), sup_map_cad[sup_esc_cad], estado_ag_novo):
                            st.success(f"Agente '{nome_ag_novo}' registado com sucesso!")
                            st.rerun()
                        else:
                            st.error("O código de utilizador já existe.")
                    else:
                        st.error("Preencha todos os campos.")

        st.divider()
        
        col_alt_rota, col_edit_dados = st.columns(2)
        
        # ALTERAR ROTA / SUPERVISOR
        with col_alt_rota:
            st.write("🔄 **Alterar Rota / Supervisor do Agente**")
            if not df_sups_disponiveis.empty:
                sup_map_rota = {"Todos os Supervisores": None}
                for _, r in df_sups_disponiveis.iterrows():
                    sup_map_rota[r['nome']] = r['id']
                
                sup_filtro_rota = st.selectbox("1. Filtrar Supervisor Atual", list(sup_map_rota.keys()), key="sup_filtro_rota")
                df_ag_rota = carregar_agentes(supervisor_id=sup_map_rota[sup_filtro_rota])
                
                if not df_ag_rota.empty:
                    ag_map_rota = {f"{r['utilizador']} - {r['nome']}": r for _, r in df_ag_rota.iterrows()}
                    ag_sel_rota = st.selectbox("2. Selecione o Agente para Transferir", list(ag_map_rota.keys()), key="ag_sel_rota")
                    ag_dados_rota = ag_map_rota[ag_sel_rota]
                    
                    sup_map_novos = {r['nome']: r['id'] for _, r in df_sups_disponiveis.iterrows()}
                    sup_atual_nome = ag_dados_rota['supervisor'] if ag_dados_rota['supervisor'] in sup_map_novos else list(sup_map_novos.keys())[0]
                    idx_sup_atual = list(sup_map_novos.keys()).index(sup_atual_nome)
                    
                    novo_sup_destino = st.selectbox("3. Mudar para Novo Supervisor", list(sup_map_novos.keys()), index=idx_sup_atual, key="novo_sup_destino")
                    
                    if st.button("🔄 Confirmar Mudança de Rota", use_container_width=True):
                        if atualizar_agente(ag_dados_rota['id'], ag_dados_rota['nome'], ag_dados_rota['utilizador'], sup_map_novos[novo_sup_destino], ag_dados_rota['estado']):
                            st.success(f"Agente {ag_dados_rota['utilizador']} transferido para {novo_sup_destino}!")
                            st.rerun()
                else:
                    st.info("Nenhum agente sob este supervisor.")

        # EDITAR DADOS DO AGENTE (NOME / CÓDIGO)
        with col_edit_dados:
            st.write("✏️ **Editar Dados do Agente (Nome / Código Utilizador)**")
            if not df_sups_disponiveis.empty:
                sup_map_edit = {"Todos os Supervisores": None}
                for _, r in df_sups_disponiveis.iterrows():
                    sup_map_edit[r['nome']] = r['id']
                
                sup_filtro_edit = st.selectbox("1. Filtrar por Supervisor", list(sup_map_edit.keys()), key="sup_filtro_edit")
                df_ag_edit_dados = carregar_agentes(supervisor_id=sup_map_edit[sup_filtro_edit])
                
                if not df_ag_edit_dados.empty:
                    ag_map_dados = {f"{r['utilizador']} - {r['nome']}": r for _, r in df_ag_edit_dados.iterrows()}
                    ag_sel_dados = st.selectbox("2. Selecione o Agente", list(ag_map_dados.keys()), key="ag_sel_dados")
                    ag_dados = ag_map_dados[ag_sel_dados]
                    
                    novo_nome_ag = st.text_input("Novo Nome do Agente", value=ag_dados['nome'], key="novo_nome_ag")
                    novo_code_ag = st.text_input("Novo Código Utilizador", value=ag_dados['utilizador'], key="novo_code_ag")
                    
                    if st.button("💾 Guardar Alterações dos Dados", use_container_width=True):
                        if novo_nome_ag.strip() and novo_code_ag.strip():
                            if atualizar_agente(ag_dados['id'], novo_nome_ag.strip(), novo_code_ag.strip(), ag_dados['supervisor_id'], ag_dados['estado']):
                                st.success("Dados do agente atualizados!")
                                st.rerun()
                            else:
                                st.error("Este código de utilizador já pertence a outro agente.")
                        else:
                            st.error("Preencha todos os campos.")
                else:
                    st.info("Nenhum agente para editar neste supervisor.")

        st.divider()
        st.write("📋 **Lista Geral de Agentes**")
        df_ag_all_display = carregar_agentes()
        st.dataframe(df_ag_all_display, use_container_width=True)

    # 3. EDITAR LANÇAMENTOS DO CAIXA
    with subtab_edit_venda:
        st.write("📝 **Alterar Lançamentos de Caixa Efetuados**")
        df_todas_vendas = carregar_vendas()
        df_todos_agentes = carregar_agentes()
        
        if not df_todas_vendas.empty and not df_todos_agentes.empty:
            venda_map = {
                f"ID: {r['ID']} | Data: {r['Data Operação']} | Agente: {r['Utilizador']} | Rec: {r['Valor Recebido (MT)']} MT": r 
                for _, r in df_todas_vendas.iterrows()
            }
            venda_sel = st.selectbox("1. Escolha o Registo para Alterar", list(venda_map.keys()))
            v_data = venda_map[venda_sel]
            
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                data_dt = datetime.strptime(v_data['Data Operação'], "%Y-%m-%d")
                edit_data = st.date_input("2. Alterar Data", data_dt)
                
                ag_codes = list(df_todos_agentes['utilizador'])
                idx_ag = ag_codes.index(v_data['Utilizador']) if v_data['Utilizador'] in ag_codes else 0
                edit_utilizador = st.selectbox("3. Alterar Agente", ag_codes, index=idx_ag)
                
            with col_v2:
                edit_rec = st.number_input("4. Valor Recebido (MT)", value=float(v_data['Valor Recebido (MT)']), step=50.0)
                edit_pag = st.number_input("5. Valor por Pagar (MT)", value=float(v_data['Valor Por Pagar (MT)']), step=50.0)
                
            if st.button("💾 Atualizar Registo de Caixa", use_container_width=True):
                atualizar_venda(v_data['ID'], edit_data.strftime("%Y-%m-%d"), edit_utilizador, edit_rec, edit_pag)
                st.success("Lançamento alterado com sucesso!")
                st.rerun()

    # 4. APAGAR REGISTOS
    with subtab_del:
        c_d1, c_d2, c_d3 = st.columns(3)
        
        with c_d1:
            st.write("❌ **Apagar Agente**")
            df_ag_del = carregar_agentes()
            if not df_ag_del.empty:
                ag_d = {f"{r['utilizador']} - {r['nome']}": r['id'] for _, r in df_ag_del.iterrows()}
                ag_del = st.selectbox("Selecione Agente", list(ag_d.keys()))
                if st.button("🚨 Apagar Agente", type="primary"):
                    apagar_agente(ag_d[ag_del])
                    st.success("Agente removido!")
                    st.rerun()

        with c_d2:
            st.write("❌ **Apagar Supervisor**")
            df_sup_del = carregar_supervisores()
            if not df_sup_del.empty:
                sup_d = {r['nome']: r['id'] for _, r in df_sup_del.iterrows()}
                sup_del = st.selectbox("Selecione Supervisor", list(sup_d.keys()))
                if st.button("🚨 Apagar Supervisor", type="primary"):
                    apagar_supervisor(sup_d[sup_del])
                    st.success("Supervisor removido!")
                    st.rerun()
                    
        with c_d3:
            st.write("❌ **Apagar Registo de Caixa**")
            df_v_del = carregar_vendas()
            if not df_v_del.empty:
                v_d = {f"ID: {r['ID']} | Data: {r['Data Operação']} | {r['Utilizador']}": r['ID'] for _, r in df_v_del.iterrows()}
                v_del = st.selectbox("Selecione Lançamento", list(v_d.keys()))
                if st.button("🚨 Apagar Lançamento", type="primary"):
                    apagar_venda(v_d[v_del])
                    st.success("Lançamento apagado!")
                    st.rerun()
