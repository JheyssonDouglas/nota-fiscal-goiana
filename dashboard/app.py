import pandas as pd
import streamlit as st
import plotly.express as px
from src.data import load_data, format_brl

DATA_PATH = "data/resultados_nota_fiscal_goiana.csv"
LARGE_PRIZE_THRESHOLD = 10_000

def brl_axis(value):
    return f"R$ {value:,.0f}".replace(",", ".")

def main():
    st.title("Nota Fiscal Goiana")
    st.caption("Entenda quem ganhou, onde os prêmios saíram e quanto foi distribuído.")

    try:
        df = load_data(DATA_PATH)
    except Exception as exc:
        st.error(f"Não foi possível carregar a base: {exc}")
        st.stop()

    if df.empty:
        st.warning("A base não possui registros.")
        st.stop()

    # Filtros
    with st.sidebar:
        st.header("Personalize a consulta")
        draws = sorted(df["sorteio"].dropna().astype(int).unique().tolist())
        selected_draws = st.multiselect("Quais sorteios deseja analisar?", draws, default=draws)
        cities = sorted(df["municipio"].dropna().unique().tolist())
        selected_cities = st.multiselect("Quais municípios?", cities)
        name_search = st.text_input("Pesquisar uma pessoa")

    filtered = df[df["sorteio"].isin(selected_draws)].copy()
    if selected_cities:
        filtered = filtered[filtered["municipio"].isin(selected_cities)]
    if name_search.strip():
        filtered = filtered[filtered["nome"].str.contains(name_search.strip(), case=False, na=False)]

    if filtered.empty:
        st.info("Nenhum registro encontrado para os filtros selecionados.")
        st.stop()

    # KPIs
    total_prize = filtered["valor"].sum()
    people = filtered["nome_normalizado"].nunique()
    cities_count = filtered["municipio"].nunique()
    total_records = len(filtered)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Premiações registradas", f"{total_records:,}".replace(",", "."))
    k2.metric("Pessoas premiadas*", f"{people:,}".replace(",", "."))
    k3.metric("Municípios", f"{cities_count:,}".replace(",", "."))
    k4.metric("Dinheiro distribuído", format_brl(total_prize))
    st.caption("*Pessoas agrupadas pelo nome. Sem um identificador individual, nomes iguais podem representar pessoas diferentes.")

    overview, cities_tab, winners_tab, draws_tab, data_tab = st.tabs(
        ["Resumo", "Municípios", "Ganhadores", "Sorteios", "Consultar registros"]
    )

    with overview:
        st.subheader("Como os sorteios se comparam?")
        summary = filtered.groupby("sorteio", as_index=False).agg(
            premiacoes=("bilhete", "count"),
            total_distribuido=("valor", "sum")
        ).sort_values("sorteio")
        left, right = st.columns(2)
        with left:
            st.markdown("**Quantas premiações saíram em cada sorteio**")
            fig = px.bar(summary, x="sorteio", y="premiacoes",
                         labels={"sorteio": "Número do sorteio", "premiacoes": "Quantidade de premiações"})
            fig.update_layout(xaxis_type="category")
            st.plotly_chart(fig, use_container_width=True)
        with right:
            st.markdown("**Quanto dinheiro foi distribuído em cada sorteio**")
            fig = px.bar(summary, x="sorteio", y="total_distribuido",
                         labels={"sorteio": "Número do sorteio", "total_distribuido": "Total distribuído (R$)"})
            fig.update_traces(hovertemplate="Sorteio %{x}<br>Total: R$ %{y:,.2f}<extra></extra>")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Quais valores de prêmio aparecem com mais frequência?")
        low = filtered[filtered["valor"] <= LARGE_PRIZE_THRESHOLD]
        high = filtered[filtered["valor"] > LARGE_PRIZE_THRESHOLD]
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Prêmios de até R$ 10 mil**")
            st.caption("Esta visualização mostra os valores menores sem serem comprimidos pelos grandes prêmios.")
            low_counts = low.groupby("valor").size().reset_index(name="quantidade").sort_values("valor")
            if not low_counts.empty:
                low_counts["valor_legivel"] = low_counts["valor"].map(format_brl)
                fig = px.bar(low_counts, x="valor_legivel", y="quantidade",
                             labels={"valor_legivel": "Valor do prêmio", "quantidade": "Número de vezes"})
                fig.update_layout(xaxis_title="Valor do prêmio", yaxis_title="Quantidade")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Não há prêmios nessa faixa para os filtros selecionados.")
        with c2:
            st.markdown("**Prêmios acima de R$ 10 mil**")
            st.caption("Os prêmios maiores ficam separados para facilitar a comparação.")
            high_counts = high.groupby("valor").size().reset_index(name="quantidade").sort_values("valor", ascending=False)
            if not high_counts.empty:
                high_counts["valor_legivel"] = high_counts["valor"].map(format_brl)
                fig = px.bar(high_counts, x="valor_legivel", y="quantidade",
                             labels={"valor_legivel": "Valor do prêmio", "quantidade": "Número de vezes"})
                fig.update_layout(xaxis_title="Valor do prêmio", yaxis_title="Quantidade")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Não há prêmios acima de R$ 10 mil para os filtros selecionados.")

    with cities_tab:
        st.subheader("Quais municípios tiveram mais ganhadores?")
        city = filtered.groupby("municipio", as_index=False).agg(
            premiacoes=("bilhete", "count"),
            pessoas_premiadas=("nome_normalizado", "nunique"),
            valor_total=("valor", "sum")
        ).sort_values("premiacoes", ascending=False)
        exclude_goiania = st.checkbox("Retirar Goiânia do ranking", value=False)
        city_rank = city[~city["municipio"].str.upper().isin(["GOIANIA", "GOIÂNIA"])] if exclude_goiania else city
        n = st.slider("Mostrar quantos municípios?", 5, 30, 15)
        top_city = city_rank.head(n).copy()
        if not top_city.empty:
            top_city["valor_total"] = top_city["valor_total"].map(format_brl)
            st.dataframe(top_city.rename(columns={
                "municipio": "Município", "premiacoes": "Premiações",
                "pessoas_premiadas": "Pessoas premiadas", "valor_total": "Total em prêmios"
            }), use_container_width=True, hide_index=True)
            chart_data = city_rank.head(n).sort_values("premiacoes")
            fig = px.bar(chart_data, x="premiacoes", y="municipio", orientation="h",
                         text="premiacoes",
                         labels={"premiacoes": "Quantidade de premiações", "municipio": "Município"})
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Municípios que receberam mais dinheiro")
        money = city.sort_values("valor_total", ascending=False).head(n).copy()
        money["valor_total"] = money["valor_total"].map(format_brl)
        st.dataframe(money.rename(columns={
            "municipio": "Município", "premiacoes": "Premiações",
            "pessoas_premiadas": "Pessoas premiadas", "valor_total": "Total em prêmios"
        }), use_container_width=True, hide_index=True)

    with winners_tab:
        st.subheader("Quem mais ganhou?")
        winners = filtered.groupby("nome_normalizado", as_index=False).agg(
            ganhador=("nome", "first"),
            vezes_premiado=("bilhete", "count"),
            total_recebido=("valor", "sum"),
            maior_premio=("valor", "max"),
            sorteios=("sorteio", lambda x: sorted(set(int(v) for v in x.dropna()))),
        )
        winners["sorteios_em_que_ganhou"] = winners["sorteios"].map(
            lambda values: ", ".join(str(v) for v in values)
        )
        winners["quantidade_sorteios"] = winners["sorteios"].map(len)
        winners = winners.sort_values(
            ["vezes_premiado", "total_recebido", "ganhador"],
            ascending=[False, False, True]
        )
        st.caption("A lista mostra todos os números dos sorteios em que cada pessoa foi premiada. A identificação é aproximada pelo nome.")
        winners_display = winners[[
            "ganhador", "vezes_premiado", "quantidade_sorteios",
            "sorteios_em_que_ganhou", "total_recebido", "maior_premio"
        ]].head(100).copy()
        winners_display["total_recebido"] = winners_display["total_recebido"].map(format_brl)
        winners_display["maior_premio"] = winners_display["maior_premio"].map(format_brl)
        st.dataframe(winners_display.rename(columns={
            "ganhador": "Ganhador", "vezes_premiado": "Quantidade de prêmios",
            "quantidade_sorteios": "Sorteios distintos",
            "sorteios_em_que_ganhou": "Números dos sorteios",
            "total_recebido": "Total recebido", "maior_premio": "Maior prêmio"
        }), use_container_width=True, hide_index=True)

        st.subheader("Quem recebeu os maiores valores acumulados?")
        top_money = winners.sort_values("total_recebido", ascending=False).head(15).sort_values("total_recebido")
        fig = px.bar(top_money, x="total_recebido", y="ganhador", orientation="h",
                     text=top_money["total_recebido"].map(format_brl),
                     labels={"total_recebido": "Total recebido (R$)", "ganhador": "Ganhador"})
        fig.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Detalhar uma pessoa")
        options = winners["ganhador"].drop_duplicates().sort_values().tolist()
        selected_person = st.selectbox("Escolha um ganhador", options)
        person = winners[winners["ganhador"] == selected_person].iloc[0]
        a, b, c = st.columns(3)
        a.metric("Quantidade de premiações", int(person["vezes_premiado"]))
        b.metric("Total recebido", format_brl(person["total_recebido"]))
        c.metric("Maior prêmio", format_brl(person["maior_premio"]))
        st.write("**Sorteios em que ganhou:**", person["sorteios_em_que_ganhou"])

    with draws_tab:
        st.subheader("Resumo de cada sorteio")
        draw_summary = filtered.groupby("sorteio", as_index=False).agg(
            data=("data_sorteio", "first"),
            premiacoes=("bilhete", "count"),
            municipios=("municipio", "nunique"),
            total_distribuido=("valor", "sum"),
            maior_premio=("valor", "max")
        ).sort_values("sorteio", ascending=False)
        display = draw_summary.copy()
        display["data"] = display["data"].dt.strftime("%d/%m/%Y")
        display["total_distribuido"] = display["total_distribuido"].map(format_brl)
        display["maior_premio"] = display["maior_premio"].map(format_brl)
        st.dataframe(display.rename(columns={
            "sorteio": "Sorteio", "data": "Data", "premiacoes": "Premiações",
            "municipios": "Municípios contemplados",
            "total_distribuido": "Total distribuído", "maior_premio": "Maior prêmio"
        }), use_container_width=True, hide_index=True)

    with data_tab:
        st.subheader("Consulte os registros individuais")
        data_view = filtered[["indice", "sorteio", "data_sorteio", "posicao", "bilhete",
                              "nome", "municipio", "valor"]].copy()
        data_view["data_sorteio"] = data_view["data_sorteio"].dt.strftime("%d/%m/%Y")
        data_view["valor"] = data_view["valor"].map(format_brl)
        st.dataframe(data_view.rename(columns={
            "indice": "Índice", "sorteio": "Sorteio", "data_sorteio": "Data",
            "posicao": "Posição no sorteio", "bilhete": "Bilhete",
            "nome": "Ganhador", "municipio": "Município", "valor": "Valor do prêmio"
        }), use_container_width=True, hide_index=True)
        csv = filtered[["indice", "sorteio", "data_sorteio", "posicao", "bilhete",
                        "nome", "municipio", "valor"]].to_csv(index=False).encode("utf-8-sig")
        st.download_button("Baixar registros filtrados (CSV)", csv,
                           "nota_fiscal_goiana_filtrado.csv", "text/csv")

    st.divider()
    st.caption(
        f"Base: {len(df):,} registros | Último sorteio: {int(df['sorteio'].max())} | "
        "Os valores são apresentados em reais."
    )
