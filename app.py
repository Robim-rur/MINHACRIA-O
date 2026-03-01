import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SETUP PRIVADO - B3", layout="wide")

# --- SISTEMA DE ACESSO ---
SENHA_CORRETA = "mestre10"
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acesso Restrito")
    senha = st.text_input("Digite sua Chave de Ativação:", type="password")
    if st.button("Liberar Acesso"):
        if senha == SENHA_CORRETA:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Chave incorreta.")
    st.stop()

# --- LISTA FIXA DE ATIVOS (178) ---
ativos_scan = sorted(set([
    "RRRP3.SA","ALOS3.SA","ALPA4.SA","ABEV3.SA","ARZZ3.SA","ASAI3.SA","AZUL4.SA","B3SA3.SA","BBAS3.SA","BBDC3.SA",
    "BBDC4.SA","BBSE3.SA","BEEF3.SA","BPAC11.SA","BRAP4.SA","BRFS3.SA","BRKM5.SA","CCRO3.SA","CMIG4.SA","CMIN3.SA",
    "COGN3.SA","CPFE3.SA","CPLE6.SA","CRFB3.SA","CSAN3.SA","CSNA3.SA","CYRE3.SA","DXCO3.SA","EGIE3.SA","ELET3.SA",
    "ELET6.SA","EMBR3.SA","ENEV3.SA","ENGI11.SA","EQTL3.SA","EZTC3.SA","FLRY3.SA","GGBR4.SA","GOAU4.SA","GOLL4.SA",
    "HAPV3.SA","HYPE3.SA","ITSA4.SA","ITUB4.SA","JBSS3.SA","KLBN11.SA","LREN3.SA","LWSA3.SA","MGLU3.SA","MRFG3.SA",
    "MRVE3.SA","MULT3.SA","NTCO3.SA","PETR3.SA","PETR4.SA","PRIO3.SA","RADL3.SA","RAIL3.SA","RAIZ4.SA","RENT3.SA",
    "RECV3.SA","SANB11.SA","SBSP3.SA","SLCE3.SA","SMTO3.SA","SUZB3.SA","TAEE11.SA","TIMS3.SA","TOTS3.SA","TRPL4.SA",
    "UGPA3.SA","USIM5.SA","VALE3.SA","VIVT3.SA","VIVA3.SA","WEGE3.SA","YDUQ3.SA","AURE3.SA","BHIA3.SA","CASH3.SA",
    "CVCB3.SA","DIRR3.SA","ENAT3.SA","GMAT3.SA","IFCM3.SA","INTB3.SA","JHSF3.SA","KEPL3.SA","MOVI3.SA","ORVR3.SA",
    "PETZ3.SA","PLAS3.SA","POMO4.SA","POSI3.SA","RANI3.SA","RAPT4.SA","STBP3.SA","TEND3.SA","TUPY3.SA",
    "BRSR6.SA","CXSE3.SA","AAPL34.SA","AMZO34.SA","GOGL34.SA","MSFT34.SA","TSLA34.SA","META34.SA","NFLX34.SA",
    "NVDC34.SA","MELI34.SA","BABA34.SA","DISB34.SA","PYPL34.SA","JNJB34.SA","PGCO34.SA","KOCH34.SA","VISA34.SA",
    "WMTB34.SA","NIKE34.SA","ADBE34.SA","AVGO34.SA","CSCO34.SA","COST34.SA","CVSH34.SA","GECO34.SA","GSGI34.SA",
    "HDCO34.SA","INTC34.SA","JPMC34.SA","MAEL34.SA","MCDP34.SA","MDLZ34.SA","MRCK34.SA","ORCL34.SA","PEP334.SA",
    "PFIZ34.SA","PMIC34.SA","QCOM34.SA","SBUX34.SA","TGTB34.SA","TMOS34.SA","TXN34.SA","UNHH34.SA","UPSB34.SA",
    "VZUA34.SA","ABTT34.SA","AMGN34.SA","AXPB34.SA","BAOO34.SA","CATP34.SA","HONB34.SA","BOVA11.SA","IVVB11.SA",
    "SMAL11.SA","HASH11.SA","GOLD11.SA","GARE11.SA","HGLG11.SA","XPLG11.SA","VILG11.SA","BRCO11.SA","BTLG11.SA",
    "XPML11.SA","VISC11.SA","HSML11.SA","MALL11.SA","KNRI11.SA","JSRE11.SA","PVBI11.SA","HGRE11.SA","MXRF11.SA",
    "KNCR11.SA","KNIP11.SA","CPTS11.SA","IRDM11.SA","DIVO11.SA","NDIV11.SA","SPUB11.SA"
]))

# --- LÓGICA TÉCNICA ---
def analisar_ativo(ticker):
    # Gráfico Semanal (Tendência)
    df_w = yf.download(ticker, period="1y", interval="1wk", progress=False)
    # Gráfico Diário (Gatilho)
    df_d = yf.download(ticker, period="100d", interval="1d", progress=False)

    if df_w.empty or df_d.empty:
        return None

    # Indicadores Semanais
    stoch_w = ta.stoch(df_w['High'], df_w['Low'], df_w['Close'], k=14, d=3, smooth_k=3)
    dmi_w = ta.adx(df_w['High'], df_w['Low'], df_w['Close'], length=14)
    
    # Filtro Semanal (Semana Anterior Encerrada)
    semanal_ok = (stoch_w['STOCHk_14_3_3'].iloc[-2] >= stoch_w['STOCHk_14_3_3'].iloc[-3]) and \
                 (dmi_w['DMP_14'].iloc[-2] > dmi_w['DMN_14'].iloc[-2])

    # Indicadores Diários
    stoch_d = ta.stoch(df_d['High'], df_d['Low'], df_d['Close'], k=14, d=3, smooth_k=3)
    dmi_d = ta.adx(df_d['High'], df_d['Low'], df_d['Close'], length=14)
    
    # Gatilho Diário
    diario_ok = (stoch_d['STOCHk_14_3_3'].iloc[-1] > stoch_d['STOCHd_14_3_3'].iloc[-1]) and \
                (dmi_d['DMP_14'].iloc[-1] > dmi_d['DMN_14'].iloc[-1])

    # Anatomia do Candle (Item 6)
    u = df_d.iloc[-1]
    a = df_d.iloc[-2]
    corpo = abs(u['Close'] - u['Open'])
    range_t = u['High'] - u['Low']
    posicao_f = (u['Close'] - u['Low']) / range_t if range_t != 0 else 0.5
    pavios = (u['High'] - max(u['Close'], u['Open'])) + (min(u['Close'], u['Open']) - u['Low'])
    
    candle_ok = (u['Close'] > a['Close']) and (u['Close'] >= (u['High'] - (range_t * 0.2))) and \
                (corpo > pavios) and not (0.4 <= posicao_f <= 0.6)

    return {
        "semanal": semanal_ok,
        "diario": diario_ok,
        "candle": candle_ok,
        "preco": u['Close'],
        "historico": df_d['Close']
    }

# --- INTERFACE ---
st.title("🎯 SCANNER TENDÊNCIA B3")
st.write("Análise de Final de Semana - Buy Side Only")

selecionado = st.selectbox("Selecione o ativo da lista de 178:", ativos_scan)

if st.button("VERIFICAR ESTRUTURA"):
    with st.spinner('Processando dados...'):
        res = analisar_ativo(selecionado)
        
        if res:
            st.divider()
            # Ranking de Probabilidade
            if res['semanal'] and res['diario'] and res['candle']:
                st.success("💎 RANKING OURO: Alta Probabilidade de Gain")
            elif res['semanal']:
                st.warning("🥈 RANKING PRATA: Tendência Semanal OK (Aguardar Gatilho)")
            else:
                st.error("🚫 RANKING BRONZE: Fora da Tendência ou Candle Neutro")

            # Gestão de Capital (Item 11)
            col1, col2, col3 = st.columns(3)
            p = res['preco']
            
            # Define Stop e Alvo por tipo de ativo
            if "34" in selecionado: stop_p, gain_p, cap = 0.04, 0.06, 2500
            elif "11" in selecionado: stop_p, gain_p, cap = 0.03, 0.045, 3300
            else: stop_p, gain_p, cap = 0.05, 0.075, 2000

            col1.metric("Entrada", f"R$ {p:.2f}")
            col2.metric("Stop Loss", f"R$ {p*(1-stop_p):.2f}")
            col3.metric("Alvo (Gain)", f"R$ {p*(1+gain_p):.2f}")
            
            st.info(f"💰 Gestão: Alocação sugerida de R$ {cap:.2f} (Risco 1% do Capital)")
            st.line_chart(res['historico'])
        else:
            st.error("Erro ao baixar dados do Yahoo Finance. Tente novamente.")
