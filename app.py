import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# Configuração da Página
st.set_page_config(page_title="Scanner Profissional - Swing Trade B3", layout="wide")

# --- SISTEMA DE SEGURANÇA ---
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
            st.error("Chave incorreta. Fale com o administrador.")
    st.stop()

# --- LISTA DE ATIVOS (EXEMPLO COM OS PRINCIPAIS, EXPANSÍVEL) ---
# Aqui você pode listar todos os 178. Abaixo estão os principais para teste.
ativos_b3 = [
    "RRRP3.SA", "ALOS3.SA", "ALPA4.SA", "ABEV3.SA", "ARZZ3.SA", "ASAI3.SA", "AZUL4.SA", "B3SA3.SA", 
    "BBAS3.SA", "BBDC3.SA", "BBDC4.SA", "BBSE3.SA", "BEEF3.SA", "BPAC11.SA", "BRAP4.SA", "BRFS3.SA", 
    "BRKM5.SA", "CCRO3.SA", "CIEL3.SA", "CMIG4.SA", "CMIN3.SA", "COGN3.SA", "CPFE3.SA", "CPLE6.SA", 
    "CRFB3.SA", "CSAN3.SA", "CSNA3.SA", "CVCB3.SA", "CYRE3.SA", "DXCO3.SA", "ELET3.SA", "ELET6.SA", 
    "EMBR3.SA", "ENGI11.SA", "ENEV3.SA", "EGIE3.SA", "EQTL3.SA", "EZTC3.SA", "FLRY3.SA", "GGBR4.SA", 
    "GOAU4.SA", "HAPV3.SA", "HYPE3.SA", "ITSA4.SA", "ITUB4.SA", "JBSS3.SA", "KLBN11.SA", "LREN3.SA", 
    "LWSA3.SA", "MGLU3.SA", "MRFG3.SA", "MRVE3.SA", "MULT3.SA", "NTCO3.SA", "PETR3.SA", "PETR4.SA", 
    "RECV3.SA", "RAIL3.SA", "RDOR3.SA", "RADL3.SA", "RAIZ4.SA", "RENT3.SA", "SANB11.SA", "SBSP3.SA", 
    "SLCE3.SA", "SMTO3.SA", "SOMA3.SA", "SUZB3.SA", "TAEE11.SA", "TOTS3.SA", "TRPL4.SA", "UGPA3.SA", 
    "USIM5.SA", "VALE3.SA", "VAMO3.SA", "VBBR3.SA", "VIVA3.SA", "VIVT3.SA", "WEGE3.SA", "YDUQ3.SA",
    "BOVA11.SA", "IVVB11.SA", "SMALL11.SA", "AAPL34.SA", "AMZO34.SA", "GOGL34.SA", "MELI34.SA"
    # Adicione os demais códigos seguidos de .SA para completar os 178
]

# --- FUNÇÕES TÉCNICAS ---
def calcular_indicadores(df):
    # Estocástico (14, 3, 3)
    stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3, smooth_k=3)
    # DMI / ADX (14)
    adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
    return pd.concat([df, stoch, adx], axis=1)

def analisar_candle(df):
    ultimo = df.iloc[-1]
    anterior = df.iloc[-2]
    corpo = abs(ultimo['Close'] - ultimo['Open'])
    range_total = ultimo['High'] - ultimo['Low']
    sombra_sup = ultimo['High'] - max(ultimo['Close'], ultimo['Open'])
    sombra_inf = min(ultimo['Close'], ultimo['Open']) - ultimo['Low']
    
    # Critérios do Manual: Fechamento > Anterior, Fechado perto da máxima, Corpo > Sombras
    f_alta = ultimo['Close'] > anterior['Close']
    p_maxima = ultimo['Close'] >= (ultimo['High'] - (range_total * 0.25))
    c_dominante = corpo > (sombra_sup + sombra_inf)
    
    # Filtro de Neutro (Range entre 40% e 60% é proibido)
    posicao_relativa = (ultimo['Close'] - ultimo['Low']) / range_total if range_total != 0 else 0.5
    nao_neutro = not (0.4 <= posicao_relativa <= 0.6)
    
    return f_alta and p_maxima and c_dominante and nao_neutro

# --- INTERFACE ---
st.title("🎯 Scanner Swing Trade - Estratégia Buy Side")
st.markdown("---")

col_setup, col_res = st.columns([1, 3])

with col_setup:
    st.write("### ⚙️ Configuração")
    ativo = st.selectbox("Escolha o ativo para análise:", sorted(ativos_b3))
    botao = st.button("VERIFICAR COMPRA")

if botao:
    with st.spinner('Validando Filtros Semanais e Diários...'):
        # Coleta Dados
        df_d = yf.download(ativo, period="100d", interval="1d")
        df_w = yf.download(ativo, period="1y", interval="1wk")

        if not df_d.empty and len(df_w) > 3:
            df_d = calcular_indicadores(df_d)
            df_w = calcular_indicadores(df_w)

            # 1. FILTRO SEMANAL (Semana anterior fechada)
            # Regra: Estocástico subindo ou lateral (não caindo) + D+ > D-
            stoch_w_agora = df_w['STOCHk_14_3_3'].iloc[-2]
            stoch_w_antes = df_w['STOCHk_14_3_3'].iloc[-3]
            dplus_w = df_w['DMP_14'].iloc[-2]
            dminus_w = df_w['DMN_14'].iloc[-2]
            
            semanal_ok = (stoch_w_agora >= stoch_w_antes) and (dplus_w > dminus_w)

            # 2. FILTRO DIÁRIO (Candle do Sinal)
            # Regra: Estocástico K > D + D+ > D-
            stoch_d_k = df_d['STOCHk_14_3_3'].iloc[-1]
            stoch_d_d = df_d['STOCHd_14_3_3'].iloc[-1]
            dplus_d = df_d['DMP_14'].iloc[-1]
            dminus_d = df_d['DMN_14'].iloc[-1]
            
            diario_ok = (stoch_d_k > stoch_d_d) and (dplus_d > dminus_d)
            candle_valido = analisar_candle(df_d)

            # --- RESULTADOS ---
            with col_res:
                st.write(f"## Análise de {ativo}")
                
                # Classificação de Probabilidade
                if semanal_ok and diario_ok and candle_valido:
                    st.success("💎 **CLASSIFICAÇÃO: OURO** (Alta Probabilidade Estatística)")
                    st.write("✅ Tendência Semanal Alinhada | ✅ Momentum Diário Positivo | ✅ Candle de Força")
                elif semanal_ok:
                    st.warning("🥈 **CLASSIFICAÇÃO: PRATA** (Tendência OK, mas sem gatilho de entrada)")
                    st.write("✅ Tendência Semanal Alinhada | ❌ Gatilho Diário ou Candle não confirmou.")
                else:
                    st.error("🚫 **CLASSIFICAÇÃO: BRONZE** (Risco Alto - Fora da Tendência Semanal)")
                    st.write("❌ Sem vantagem estatística no gráfico semanal. Estocástico semanal caindo ou D- dominante.")

                # Gestão de Risco Estrita
                st.divider()
                st.write("### 📈 Parâmetros da Operação")
                
                preco = df_d['Close'].iloc[-1]
                # Determina tipo de ativo
                if "34" in ativo: # BDR
                    stop_p, gain_p, cap = 0.04, 0.06, 2500
                elif "11" in ativo: # ETF
                    stop_p, gain_p, cap = 0.03, 0.045, 3300
                else: # Ação
                    stop_p, gain_p, cap = 0.05, 0.075, 2000

                c1, c2, c3 = st.columns(3)
                c1.metric("Entrada sugerida", f"R$ {preco:.2f}")
                c2.metric("Stop Loss (Fixo)", f"R$ {preco*(1-stop_p):.2f}")
                c3.metric("Alvo (Gain)", f"R$ {preco*(1+gain_p):.2f}")

                st.info(f"💰 **GESTÃO DE CAPITAL:** Alocação máxima permitida para este trade: **R$ {cap:.2f}**")
                st.line_chart(df_d['Close'])
