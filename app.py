import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from datetime import datetime, timedelta

# Configuração da página para celular (Samsung A15 e iPhone)
st.set_page_config(
    page_title="Finanças Didáticas",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CONFIGURAÇÃO DE ESTILO: MODO ESCURO PREMIUM ---
st.markdown("""
<style>
    /* Estilo geral da página */
    .stApp {
        background-color: #121214;
        color: #E1E1E6;
    }
    
    /* Cabeçalho */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Cards Customizados */
    .card-principal {
        background-color: #202024;
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 15px;
        border-left: 5px solid #8257E5;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .card-didatico {
        background-color: #1A1A1E;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 5px solid #3867D6;
        font-size: 0.9em;
        line-height: 1.5;
        color: #C4C4CC;
    }
    .card-receita {
        background-color: #1A2E26;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #26DE81;
    }
    .card-gasto {
        background-color: #2D1A1E;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF4757;
    }
    .titulo-secao {
        color: #FFFFFF;
        font-weight: bold;
        margin-top: 20px;
        border-bottom: 1px solid #29292E;
        padding-bottom: 8px;
    }
    
    /* Botões */
    .stButton>button {
        background-color: #8257E5 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 20px !important;
        font-weight: bold !important;
        width: 100%;
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #9466FF !important;
    }
    
    /* Inputs */
    div[data-baseweb="input"] {
        background-color: #202024 !important;
        border-color: #29292E !important;
    }
    input {
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE AUXÍLIO PARA DATAS ---
def get_proximos_meses(data_inicial, parcelas):
    """Retorna uma lista de strings 'AAAA-MM' para as parcelas futuras."""
    datas = []
    ano = data_inicial.year
    mes = data_inicial.month
    
    for i in range(parcelas):
        datas.append(f"{ano}-{mes:02d}")
        mes += 1
        if mes > 12:
            mes = 1
            ano += 1
    return datas

# --- CONTROLE DE MULTIPERFIS E SEGURANÇA ---
def obter_caminho_dados(usuario):
    # Formata o nome do arquivo com base no usuário
    nome_limpo = usuario.lower().strip().replace(" ", "_")
    return f"dados_financeiros_{nome_limpo}.json"

def carregar_dados_usuario(usuario):
    caminho = obter_caminho_dados(usuario)
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
            
    # Estrutura inicial padrão para novos usuários
    pin_padrao = "123456" if usuario.lower() == "yago" else "654321" if usuario.lower() == "binete" else "123456"
    return {
        "pin": pin_padrao,
        "receitas": [],
        "gastos_fixos": [],
        "gastos_avulsos": [],
        "gastos_terceiros_cartao": [],
        "gastos_terceiros_emprestimo": [],
        "conta_isolada": {
            "saldo_principal": 0.0,
            "caixinha_nu": 0.0,
            "historico_depositos": []
        }
    }

def salvar_dados_usuario(usuario, dados):
    caminho = obter_caminho_dados(usuario)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if "usuario_ativo" not in st.session_state:
    # Capturar usuário pela URL (?user=nome) se houver
    params = st.query_params
    usuario_url = params.get("user", "Yago").title()
    st.session_state.usuario_ativo = usuario_url

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# Carregar dados do perfil ativo
usuario_atual = st.session_state.usuario_ativo
dados = carregar_dados_usuario(usuario_atual)

# --- CABEÇALHO DO APP ---
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    # Tenta carregar o logotipo gerado
    if os.path.exists("app_logo_financeiro.png"):
        st.image("app_logo_financeiro.png", width=70)
    else:
        st.markdown("<h1 style='font-size: 50px; margin: 0;'>💰</h1>", unsafe_allow_html=True)

with col_titulo:
    st.title("Finanças Didáticas")
    st.caption("Controle financeiro premium e descomplicado")

# --- TELA DE LOGIN / SEGURANÇA ---
if not st.session_state.autenticado:
    st.markdown(f"### 🔒 Acesso Restrito - Perfil: **{usuario_atual}**")
    st.markdown("Por segurança, digite sua senha de 6 dígitos para acessar seus dados.")
    
    pin_digitado = st.text_input("Digite o PIN de 6 dígitos:", type="password", max_chars=6)
    
    col_btn_login, col_btn_perfil = st.columns(2)
    with col_btn_login:
        if st.button("Entrar 🔓"):
            if pin_digitado == dados.get("pin", "123456"):
                st.session_state.autenticado = True
                st.success("Acesso liberado!")
                st.rerun()
            else:
                st.error("PIN incorreto! Tente novamente.")
                
    with col_btn_perfil:
        # Opção para mudar de usuário diretamente na tela de bloqueio
        novo_usuario = st.selectbox("Trocar de Perfil:", ["Yago", "Binete", "Criar Novo Perfil"])
        if novo_usuario == "Criar Novo Perfil":
            st.markdown("---")
            st.markdown("**Criar Novo Perfil Independente**")
            novo_nome = st.text_input("Nome do Novo Usuário:")
            novo_pin = st.text_input("Escolha um PIN de 6 dígitos (somente números):", type="password", max_chars=6)
            if st.button("Criar Perfil e Acessar 🚀"):
                if novo_nome and len(novo_pin) == 6 and novo_pin.isdigit():
                    # Inicializa e salva novo usuário
                    dados_novos = carregar_dados_usuario(novo_nome)
                    dados_novos["pin"] = novo_pin
                    salvar_dados_usuario(novo_nome, dados_novos)
                    st.session_state.usuario_ativo = novo_nome.title()
                    st.session_state.autenticado = True
                    st.query_params["user"] = novo_nome.lower()
                    st.success(f"Perfil de {novo_nome} criado e logado!")
                    st.rerun()
                else:
                    st.error("Por favor, digite um nome válido e um PIN numérico de exatamente 6 dígitos.")
        elif novo_usuario != usuario_atual:
            st.session_state.usuario_ativo = novo_usuario
            st.query_params["user"] = novo_usuario.lower()
            st.rerun()
            
    st.stop() # Interrompe a execução aqui para quem não está logado

# --- SELETOR DE MÊS E ANO (PLANEJAMENTO SEM LIMITES) ---
st.markdown("---")
col_perf, col_m, col_a = st.columns([2, 2, 2])

with col_perf:
    st.markdown(f"👤 **{usuario_atual}**")
    if st.button("Sair / Bloquear 🔒"):
        st.session_state.autenticado = False
        st.rerun()

with col_m:
    meses_lista = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    mes_atual_nome = meses_lista[datetime.now().month - 1]
    mes_selecionado = st.selectbox("Selecione o Mês:", meses_lista, index=datetime.now().month - 1)
    mes_num = meses_lista.index(mes_selecionado) + 1

with col_a:
    anos_lista = list(range(2025, 2036))
    ano_selecionado = st.selectbox("Selecione o Ano:", anos_lista, index=anos_lista.index(datetime.now().year))

# Identificador do período selecionado (formato AAAA-MM)
periodo_ativo = f"{ano_selecionado}-{mes_num:02d}"

# --- NAVEGAÇÃO POR ABAS (Mobile Friendly) ---
abas = st.tabs(["📊 Resumo", "💵 Ganhos", "🏠 Fixas", "🛍️ Avulsos", "👥 Terceiros", "🔒 Guardado", "⚙️ Senha"])

# ----------------- ABA 1: RESUMO GERAL & RELATÓRIOS -----------------
with abas[0]:
    st.markdown(f"<h3 class='titulo-secao'>📊 Painel Financeiro ({mes_selecionado}/{ano_selecionado})</h3>", unsafe_allow_html=True)
    
    # Tipo de relatório: Mensal ou Anual
    tipo_relatorio = st.radio("Escolha o tipo de Relatório:", ["Relatório Mensal", "Relatório Anual"], horizontal=True)
    
    if tipo_relatorio == "Relatório Mensal":
        # Filtrar dados do mês selecionado
        receitas_mes = [r for r in dados.get("receitas", []) if r["data"].startswith(periodo_ativo)]
        gastos_fixos_mes = [g for g in dados.get("gastos_fixos", []) if g["data"].startswith(periodo_ativo)]
        gastos_avulsos_mes = [g for g in dados.get("gastos_avulsos", []) if g["data"].startswith(periodo_ativo)]
        
        total_receitas = sum(r["valor"] for r in receitas_mes)
        total_fixos = sum(g["valor"] for g in gastos_fixos_mes)
        total_avulsos = sum(g["valor"] for g in gastos_avulsos_mes)
        total_gastos = total_fixos + total_avulsos
        saldo_livre = total_receitas - total_gastos
        
        # Terceiros pendentes no cartão do mês
        total_cartao_terceiros = sum(t["valor"] for t in dados.get("gastos_terceiros_cartao", []) if t["data"].startswith(periodo_ativo) and not t["pago"])
        # Empréstimos acumulados (Dinheiro/PIX) - pendentes globais
        total_emprestimos_pendentes = sum(e["valor"] for e in dados.get("gastos_terceiros_emprestimo", []) if not e["pago"])
        
        # Métricas na tela
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric(label="Minhas Receitas (+)", value=f"R$ {total_receitas:,.2f}")
            st.metric(label="Meus Gastos (-)", value=f"R$ {total_gastos:,.2f}")
        with col_m2:
            st.metric(label="Saldo do Mês (Livre)", value=f"R$ {saldo_livre:,.2f}", delta=f"R$ {saldo_livre:,.2f}" if saldo_livre >= 0 else f"R$ {saldo_livre:,.2f}")
            st.metric(label="Reservas Guardadas", value=f"R$ {dados['conta_isolada']['saldo_principal'] + dados['conta_isolada']['caixinha_nu']:,.2f}")
            
        # Alertas de Terceiros
        st.markdown("#### 👥 Dinheiro de Terceiros a Receber:")
        c_t1, c_t2 = st.columns(2)
        with c_t1:
            if total_cartao_terceiros > 0:
                st.warning(f"💳 **Cartão de Crédito:**\n\nR$ {total_cartao_terceiros:,.2f} pendentes neste mês.")
            else:
                st.success("💳 **Cartão de Crédito:**\n\nNenhum reembolso pendente neste mês.")
        with c_t2:
            if total_emprestimos_pendentes > 0:
                st.warning(f"💸 **Empréstimos (PIX/Dinheiro):**\n\nR$ {total_emprestimos_pendentes:,.2f} a receber no total.")
            else:
                st.success("💸 **Empréstimos (PIX/Dinheiro):**\n\nTodos os empréstimos pagos!")
                
        # Gráfico de Pizza do Mês
        if total_gastos > 0:
            st.markdown("#### 📈 Divisão das Despesas")
            df_pizza = pd.DataFrame([
                {"Categoria": "Gastos Fixos/Parcelas", "Valor": total_fixos},
                {"Categoria": "Gastos Avulsos (Dia a Dia)", "Valor": total_avulsos}
            ])
            fig = px.pie(df_pizza, values="Valor", names="Categoria", hole=0.4,
                         color_discrete_sequence=["#8257E5", "#FF4757"])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="#FFFFFF",
                margin=dict(t=10, b=10, l=10, r=10),
                height=220
            )
            st.plotly_chart(fig, use_container_width=True)
            
    else:
        # --- RELATÓRIO ANUAL CONSOLIDADO ---
        st.markdown(f"### 📅 Relatório Anual - Ano: **{ano_selecionado}**")
        
        # Consolidar dados de todos os 12 meses do ano selecionado
        dados_ano = []
        for m in range(1, 13):
            prefixo_busca = f"{ano_selecionado}-{m:02d}"
            rec_ano = sum(r["valor"] for r in dados.get("receitas", []) if r["data"].startswith(prefixo_busca))
            fix_ano = sum(g["valor"] for g in dados.get("gastos_fixos", []) if g["data"].startswith(prefixo_busca))
            av_ano = sum(g["valor"] for g in dados.get("gastos_avulsos", []) if g["data"].startswith(periodo_ativo))
            gastos_totais = fix_ano + av_ano
            dados_ano.append({
                "Mês": meses_lista[m-1][:3], # Três primeiras letras do mês
                "Ganhos": rec_ano,
                "Gastos": gastos_totais,
                "Balanço": rec_ano - gastos_totais
            })
            
        df_ano = pd.DataFrame(dados_ano)
        
        # Totais Anuais
        total_ganhos_ano = df_ano["Ganhos"].sum()
        total_gastos_ano = df_ano["Gastos"].sum()
        saldo_anual_acumulado = total_ganhos_ano - total_gastos_ano
        
        col_an1, col_an2, col_an3 = st.columns(3)
        col_an1.metric("Ganhos no Ano", f"R$ {total_ganhos_ano:,.2f}")
        col_an2.metric("Gastos no Ano", f"R$ {total_gastos_ano:,.2f}")
        col_an3.metric("Balanço Acumulado", f"R$ {saldo_anual_acumulado:,.2f}", 
                        delta=f"R$ {saldo_anual_acumulado:,.2f}" if saldo_anual_acumulado >= 0 else f"R$ {saldo_anual_acumulado:,.2f}")
        
        # Gráfico de Barras Consolidado
        st.markdown("#### 📊 Comparativo Mensal de Ganhos vs. Gastos")
        df_melted = df_ano.melt(id_vars="Mês", value_vars=["Ganhos", "Gastos"], var_name="Tipo", value_name="Valor (R$)")
        fig_bar = px.bar(df_melted, x="Mês", y="Valor (R$)", color="Tipo", barmode="group",
                         color_discrete_map={"Ganhos": "#26DE81", "Gastos": "#FF4757"})
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="#FFFFFF",
            margin=dict(t=10, b=10, l=10, r=10),
            height=280
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ----------------- ABA 2: GANHOS (RECEITAS) -----------------
with abas[1]:
    st.markdown("<h3 class='titulo-secao'>💵 Registro de Ganhos</h3>", unsafe_allow_html=True)
    
    with st.form("form_receita", clear_on_submit=True):
        st.markdown("**Adicionar Nova Receita**")
        desc = st.text_input("Descrição (Ex: Salário, PIX, Freelance)")
        val = st.number_input("Valor (R$)", min_value=0.0, step=50.0, format="%.2f")
        # Força a data para ser no mês/ano selecionado para evitar confusão
        data_padrao = datetime(ano_selecionado, mes_num, min(datetime.now().day, 28))
        data_rec = st.date_input("Data do Recebimento", data_padrao)
        
        enviar = st.form_submit_button("Salvar Receita")
        if enviar and desc and val > 0:
            nova_rec = {"data": str(data_rec), "descricao": desc, "valor": val}
            dados.setdefault("receitas", []).append(nova_rec)
            salvar_dados_usuario(usuario_atual, dados)
            st.success("Receita adicionada com sucesso!")
            st.rerun()

    # Mostrar Receitas do Mês Selecionado
    receitas_mes = [r for r in dados.get("receitas", []) if r["data"].startswith(periodo_ativo)]
    if receitas_mes:
        st.markdown("#### Suas Receitas Registradas neste Mês")
        df_rec = pd.DataFrame(receitas_mes)
        df_rec.columns = ["Data", "Descrição", "Valor (R$)"]
        st.dataframe(df_rec, use_container_width=True)
        
        if st.button("Limpar Histórico de Receitas (Mês)", key="limpar_rec"):
            dados["receitas"] = [r for r in dados.get("receitas", []) if not r["data"].startswith(periodo_ativo)]
            salvar_dados_usuario(usuario_atual, dados)
            st.rerun()

# ----------------- ABA 3: MEUS GASTOS FIXOS -----------------
with abas[2]:
    st.markdown("<h3 class='titulo-secao'>🏠 Meus Gastos Fixos & Parcelas</h3>", unsafe_allow_html=True)
    st.caption("Gastos repetitivos ou parcelados de longo prazo.")

    with st.form("form_fixo", clear_on_submit=True):
        st.markdown("**Adicionar Gasto Fixo / Parcelado**")
        desc = st.text_input("Descrição do Gasto (Ex: Aluguel, Parcela de Notebook)")
        val = st.number_input("Valor Mensal (R$)", min_value=0.0, step=10.0, format="%.2f")
        
        # Lógica de Parcelamento
        is_parcelado = st.checkbox("Esta despesa é parcelada?")
        total_parc = st.number_input("Número total de parcelas:", min_value=1, max_value=48, value=1, step=1)
        
        pago = st.checkbox("Marcar primeira parcela como já paga?")
        
        enviar = st.form_submit_button("Salvar Despesa")
        if enviar and desc and val > 0:
            data_inicial = datetime(ano_selecionado, mes_num, 1)
            
            if is_parcelado:
                lista_periodos = get_proximos_meses(data_inicial, total_parc)
                for i, periodo in enumerate(lista_periodos):
                    novo_gasto = {
                        "data": f"{periodo}-01",
                        "descricao": f"{desc} (Parc. {i+1}/{total_parc})",
                        "valor": val,
                        "pago": pago if i == 0 else False
                    }
                    dados.setdefault("gastos_fixos", []).append(novo_gasto)
            else:
                novo_gasto = {
                    "data": f"{periodo_ativo}-01",
                    "descricao": desc,
                    "valor": val,
                    "pago": pago
                }
                dados.setdefault("gastos_fixos", []).append(novo_gasto)
                
            salvar_dados_usuario(usuario_atual, dados)
            st.success("Despesa adicionada com sucesso!")
            st.rerun()

    # Mostrar Gastos Fixos com checkbox de pagamento
    gastos_fixos_mes = [g for g in dados.get("gastos_fixos", []) if g["data"].startswith(periodo_ativo)]
    if gastos_fixos_mes:
        st.markdown("#### Controle de Pagamentos de Despesas Fixas")
        for idx, item in enumerate(dados["gastos_fixos"]):
            if item["data"].startswith(periodo_ativo):
                col_d, col_v, col_p = st.columns([2, 1, 1])
                col_d.markdown(f"**{item['descricao']}**")
                col_v.markdown(f"R$ {item['valor']:,.2f}")
                
                status_pago = col_p.checkbox("Pago", value=item["pago"], key=f"fixo_{idx}_{periodo_ativo}")
                if status_pago != item["pago"]:
                    dados["gastos_fixos"][idx]["pago"] = status_pago
                    salvar_dados_usuario(usuario_atual, dados)
                    st.rerun()
                    
        if st.button("Limpar Todos os Gastos Fixos (Deste Mês)", key="limpar_fixos"):
            dados["gastos_fixos"] = [g for g in dados.get("gastos_fixos", []) if not g["data"].startswith(periodo_ativo)]
            salvar_dados_usuario(usuario_atual, dados)
            st.rerun()

# ----------------- ABA 4: GASTOS AVULSOS -----------------
with abas[3]:
    st.markdown("<h3 class='titulo-secao'>🛍️ Meus Gastos Avulsos</h3>", unsafe_allow_html=True)
    st.caption("Gastos diários variáveis (Ifood, Uber, Compras rápidas)")

    with st.form("form_avulso", clear_on_submit=True):
        st.markdown("**Adicionar Gasto Avulso**")
        desc = st.text_input("O que você comprou?")
        val = st.number_input("Valor Pago (R$)", min_value=0.0, step=10.0, format="%.2f")
        data_padrao = datetime(ano_selecionado, mes_num, min(datetime.now().day, 28))
        data_gasto = st.date_input("Data do Gasto", data_padrao)
        
        enviar = st.form_submit_button("Salvar Gasto Avulso")
        if enviar and desc and val > 0:
            novo_avulso = {"data": str(data_gasto), "descricao": desc, "valor": val}
            dados.setdefault("gastos_avulsos", []).append(novo_avulso)
            salvar_dados_usuario(usuario_atual, dados)
            st.success("Gasto avulso adicionado!")
            st.rerun()

    # Mostrar Gastos Avulsos
    gastos_avulsos_mes = [g for g in dados.get("gastos_avulsos", []) if g["data"].startswith(periodo_ativo)]
    if gastos_avulsos_mes:
        st.markdown("#### Seus Gastos Avulsos Registrados")
        df_av = pd.DataFrame(gastos_avulsos_mes)
        df_av.columns = ["Data", "Descrição", "Valor (R$)"]
        st.dataframe(df_av, use_container_width=True)
        
        if st.button("Limpar Histórico de Avulsos (Mês)", key="limpar_avulsos"):
            dados["gastos_avulsos"] = [g for g in dados.get("gastos_avulsos", []) if not g["data"].startswith(periodo_ativo)]
            salvar_dados_usuario(usuario_atual, dados)
            st.rerun()

# ----------------- ABA 5: GASTOS DE TERCEIROS (CARTÃO VS EMPRÉSTIMO) -----------------
with abas[4]:
    st.markdown("<h3 class='titulo-secao'>👥 Amigos & Terceiros no Meu Cartão / Empréstimos</h3>", unsafe_allow_html=True)
    
    sub_abas_terceiros = st.tabs(["💳 Compras no Meu Cartão", "💸 Empréstimos (PIX/Dinheiro)"])
    
    # SUB-ABA 5.1: COMPRAS NO MEU CARTÃO
    with sub_abas_terceiros[0]:
        st.markdown("**Cadastro de Compras de Terceiros no seu Cartão de Crédito**")
        st.caption("Quando alguém usa seu cartão para comprar parcelado ou à vista.")
        
        with st.form("form_cartao_terceiros", clear_on_submit=True):
            nome = st.text_input("Nome de quem comprou:")
            desc = st.text_input("Descrição da compra (Ex: Pizza, Tênis)")
            val = st.number_input("Valor da compra/parcela (R$)", min_value=0.0, step=10.0, format="%.2f")
            
            is_parc_terc = st.checkbox("Esta compra de terceiro é parcelada?")
            total_parc_terc = st.number_input("Número de parcelas de terceiro:", min_value=1, max_value=48, value=1, step=1)
            pago_terc = st.checkbox("Já te pagou a primeira parcela?")
            
            enviar_c = st.form_submit_button("Salvar Compra no Cartão")
            if enviar_c and nome and desc and val > 0:
                data_inicial = datetime(ano_selecionado, mes_num, 1)
                
                if is_parc_terc:
                    lista_periodos = get_proximos_meses(data_inicial, total_parc_terc)
                    for i, periodo in enumerate(lista_periodos):
                        nova_compra = {
                            "data": f"{periodo}-01",
                            "nome": nome.title(),
                            "descricao": f"{desc} (Parc. {i+1}/{total_parc_terc})",
                            "valor": val,
                            "pago": pago_terc if i == 0 else False
                        }
                        dados.setdefault("gastos_terceiros_cartao", []).append(nova_compra)
                else:
                    nova_compra = {
                        "data": f"{periodo_ativo}-01",
                        "nome": nome.title(),
                        "descricao": desc,
                        "valor": val,
                        "pago": pago_terc
                    }
                    dados.setdefault("gastos_terceiros_cartao", []).append(nova_compra)
                    
                salvar_dados_usuario(usuario_atual, dados)
                st.success("Compra no cartão adicionada com sucesso!")
                st.rerun()

        # Visualizar faturas do mês de terceiros
        cartao_mes = [t for t in dados.get("gastos_terceiros_cartao", []) if t["data"].startswith(periodo_ativo)]
        if cartao_mes:
            st.markdown(f"#### Reembolsos de Fatura de Terceiros - {mes_selecionado}/{ano_selecionado}")
            for idx, item in enumerate(dados["gastos_terceiros_cartao"]):
                if item["data"].startswith(periodo_ativo):
                    c_det, c_status = st.columns([3, 1])
                    status_txt = "✅ Recebido" if item["pago"] else "❌ Pendente"
                    c_det.markdown(f"👤 **{item['nome']}** - {item['descricao']} (R$ {item['valor']:,.2f}) [{status_txt}]")
                    
                    pago_atualizado = c_status.checkbox("Recebido", value=item["pago"], key=f"cartao_terc_{idx}_{periodo_ativo}")
                    if pago_atualizado != item["pago"]:
                        dados["gastos_terceiros_cartao"][idx]["pago"] = pago_atualizado
                        salvar_dados_usuario(usuario_atual, dados)
                        st.rerun()
                        
    # SUB-ABA 5.2: EMPRÉSTIMOS (PIX/DINHEIRO)
    with sub_abas_terceiros[1]:
        st.markdown("**Cadastro de Empréstimos (Dinheiro físico ou PIX)**")
        st.caption("Dinheiro que saiu da sua conta e que deve retornar direto para sua conta.")
        
        with st.form("form_emprestimo_terceiros", clear_on_submit=True):
            nome_emp = st.text_input("Quem pediu o empréstimo?")
            desc_emp = st.text_input("Motivo do empréstimo (Ex: Empréstimo para Luz, PIX Uber)")
            val_emp = st.number_input("Valor Emprestado (R$)", min_value=0.0, step=10.0, format="%.2f")
            
            enviar_e = st.form_submit_button("Registrar Empréstimo")
            if enviar_e and nome_emp and val_emp > 0:
                novo_emp = {
                    "data": str(datetime.now().date()),
                    "nome": nome_emp.title(),
                    "descricao": desc_emp,
                    "valor": val_emp,
                    "pago": False
                }
                dados.setdefault("gastos_terceiros_emprestimo", []).append(novo_emp)
                salvar_dados_usuario(usuario_atual, dados)
                st.success("Empréstimo registrado!")
                st.rerun()

        # Lista total de empréstimos pendentes
        emprestimos_todos = dados.get("gastos_terceiros_emprestimo", [])
        if emprestimos_todos:
            st.markdown("#### Histórico Geral de Empréstimos (Dinheiro/PIX)")
            
            # Resumo por pessoa
            divida_pessoa = {}
            for e in emprestimos_todos:
                if not e["pago"]:
                    divida_pessoa[e["nome"]] = divida_pessoa.get(e["nome"], 0.0) + e["valor"]
                    
            if divida_pessoa:
                st.markdown("**Saldos de Devedores de Empréstimo:**")
                for pessoa, valor in divida_pessoa.items():
                    st.info(f"👤 **{pessoa}** te deve um total de: **R$ {valor:,.2f}**")
                    
            st.markdown("---")
            st.markdown("**Atualizar Reembolso de Empréstimo:**")
            for idx, item in enumerate(dados["gastos_terceiros_emprestimo"]):
                col_e_det, col_e_st = st.columns([3, 1])
                status_txt = "✅ Pago" if item["pago"] else "❌ Pendente"
                col_e_det.markdown(f"**{item['nome']}** - {item['descricao']} (R$ {item['valor']:,.2f}) [{status_txt}]")
                
                pago_atualizado = col_e_st.checkbox("Recebi de volta", value=item["pago"], key=f"emp_{idx}")
                if pago_atualizado != item["pago"]:
                    dados["gastos_terceiros_emprestimo"][idx]["pago"] = pago_atualizado
                    salvar_dados_usuario(usuario_atual, dados)
                    st.rerun()

# ----------------- ABA 6: CONTA ISOLADA & CAIXINHAS -----------------
with abas[5]:
    st.markdown("<h3 class='titulo-secao'>🔒 Dinheiro Guardado & Caixinhas Nubank</h3>", unsafe_allow_html=True)
    
    saldo_isolada = dados["conta_isolada"]["saldo_principal"]
    saldo_caixinha = dados["conta_isolada"]["caixinha_nu"]
    total_reservas = saldo_isolada + saldo_caixinha
    
    col_sal1, col_sal2 = st.columns(2)
    with col_sal1:
        st.metric("Conta Isolada Principal", value=f"R$ {saldo_isolada:,.2f}")
    with col_sal2:
        st.metric("Caixinha NU (Rendimento)", value=f"R$ {saldo_caixinha:,.2f}")
    st.info(f"💰 **Total Guardado Acumulado:** R$ {total_reservas:,.2f}")

    # Atualização manual rápida de saldos
    st.markdown("#### ⚡ Atualizar Saldos Atuais")
    with st.form("form_saldos_reserva"):
        novo_saldo_isolada = st.number_input("Saldo Atual na Conta Isolada (R$)", value=saldo_isolada, min_value=0.0, format="%.2f")
        novo_saldo_caixinha = st.number_input("Saldo Atual nas Caixinhas Nubank (R$)", value=saldo_caixinha, min_value=0.0, format="%.2f")
        
        salvar_saldos = st.form_submit_button("Salvar Novos Saldos")
        if salvar_saldos:
            dados["conta_isolada"]["saldo_principal"] = novo_saldo_isolada
            dados["conta_isolada"]["caixinha_nu"] = novo_saldo_caixinha
            salvar_dados_usuario(usuario_atual, dados)
            st.success("Saldos atualizados com sucesso!")
            st.rerun()

    # Registrar Novo Depósito no histórico
    st.markdown("#### 📥 Registrar Nova Economia Guardada")
    with st.form("form_deposito", clear_on_submit=True):
        valor_dep = st.number_input("Valor Guardado (R$)", min_value=0.0, step=50.0, format="%.2f")
        destino_dep = st.selectbox("Destino do depósito:", ["Conta Isolada Principal", "Caixinha NU"])
        
        enviar_dep = st.form_submit_button("Registrar Depósito")
        if enviar_dep and valor_dep > 0:
            novo_dep = {
                "data": str(datetime.now().date()),
                "valor": valor_dep,
                "destino": destino_dep
            }
            dados["conta_isolada"].setdefault("historico_depositos", []).append(novo_dep)
            
            # Somar automaticamente ao saldo
            if destino_dep == "Conta Isolada Principal":
                dados["conta_isolada"]["saldo_principal"] += valor_dep
            else:
                dados["conta_isolada"]["caixinha_nu"] += valor_dep
                
            salvar_dados_usuario(usuario_atual, dados)
            st.success("Depósito registrado e somado com sucesso!")
            st.rerun()

    if dados["conta_isolada"].get("historico_depositos", []):
        st.markdown("#### Histórico de Economias Recentes")
        df_dep = pd.DataFrame(dados["conta_isolada"]["historico_depositos"])
        df_dep.columns = ["Data", "Valor Guardado (R$)", "Destino"]
        st.dataframe(df_dep, use_container_width=True)

# ----------------- ABA 7: ALTERAÇÃO DE SENHA (PIN) -----------------
with abas[6]:
    st.markdown("<h3 class='titulo-secao'>⚙️ Alterar Sua Senha (PIN)</h3>", unsafe_allow_html=True)
    st.caption("Sua senha garante a privacidade dos seus dados financeiros se outras pessoas usarem o mesmo aplicativo.")
    
    with st.form("form_alterar_senha"):
        senha_atual = st.text_input("Digite o PIN atual (6 dígitos):", type="password", max_chars=6)
        nova_senha = st.text_input("Digite o NOVO PIN (6 dígitos numéricos):", type="password", max_chars=6)
        nova_senha_conf = st.text_input("Confirme o NOVO PIN (6 dígitos numéricos):", type="password", max_chars=6)
        
        atualizar_btn = st.form_submit_button("Alterar Senha")
        if atualizar_btn:
            if senha_atual != dados.get("pin", "123456"):
                st.error("PIN atual incorreto!")
            elif not nova_senha.isdigit() or len(nova_senha) != 6:
                st.error("O novo PIN deve conter exatamente 6 números.")
            elif nova_senha != nova_senha_conf:
                st.error("A confirmação da nova senha está diferente!")
            else:
                dados["pin"] = nova_senha
                salvar_dados_usuario(usuario_atual, dados)
                st.success("Sua senha (PIN) de 6 dígitos foi alterada com sucesso!")
                st.rerun()
