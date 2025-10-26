import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import altair as alt


# Эту функцию можно разместить вверху скрипта или в отдельном файле
def create_performance_analytics_tab(
        df_filtered: pd.DataFrame,
        metric_options: dict,
        metric_key_prefix: str,
        unit_label: str,
        tier_a_leaders_list: list
):
    """
    Генерирует одну подвкладку (GHG, Energy, Waste, Water)
    """

    # 1. Выбор метрики
    selected_metric_name = st.radio(
        f"Select a {metric_key_prefix} metric:",
        options=metric_options.keys(),
        key=f"{metric_key_prefix}_metric_radio",
    )
    selected_sub_codes = metric_options[selected_metric_name]

    # 2. Фильтрация данных
    df_metric = df_filtered[
        (df_filtered["sub_code"].isin(selected_sub_codes))
    ].copy()

    if df_metric.empty:
        st.warning(f"No data found for '{selected_metric_name}'.")
        return  # Выходим, если данных нет

    # 3. Расчет средних (ВАШ СУЩЕСТВУЮЩИЙ КОД)
    df_annual_sums = (
        df_metric.groupby(["company", "year"])["value"].sum().reset_index()
    )
    company_averages = []
    for company in df_annual_sums["company"].unique():
        df_company_data = df_annual_sums[
            df_annual_sums["company"] == company
            ].sort_values(by="year", ascending=False)
        latest_3_values = df_company_data.head(3)["value"]
        if not latest_3_values.empty:
            avg_value = latest_3_values.mean()
            company_averages.append(
                {
                    "company": company,
                    "average_value": avg_value,  # Используем общее имя
                    "years_of_data": len(latest_3_values),
                }
            )

    if not company_averages:
        st.warning("Not enough data to calculate averages.")
        return

    df_avg_results = pd.DataFrame(company_averages).sort_values(
        by="average_value", ascending=False
    )

    def get_company_type(company_name):
        if company_name in tier_a_leaders_list:
            return "Tier A Leader"
        else:
            return "Other Company"

    df_avg_results['Company Type'] = df_avg_results['company'].apply(get_company_type)

    st.subheader(f"Average {selected_metric_name} Distribution")

    # 4. Выбор типа графика
    chart_type = st.radio(
        "Выберите тип графика:",
        ('Histogram', 'Violin Plot', 'Treemap', 'Bar Chart'),
        horizontal=True,
        label_visibility="collapsed",
        key=f"{metric_key_prefix}_chart_type",
    )

    # 5. Отрисовка графиков (ВАШ КОД, но с 'average_value' и unit_label)

    if chart_type == "Histogram":
        st.markdown("###### Distribution (Histogram)")
        q_low = df_avg_results["average_value"].quantile(0.05)
        q_high = df_avg_results["average_value"].quantile(0.95)
        df_hist = df_avg_results[
            (df_avg_results["average_value"] >= q_low)
            & (df_avg_results["average_value"] <= q_high)
            ]
        df_hist['Company Type'] = df_hist['company'].apply(get_company_type)
        st.warning(
            "Histogram excludes the lowest and highest 5% of values to reduce outlier impact."
        )
        fig_hist = px.histogram(
            df_hist,
            x="average_value",
            nbins=30,
            title=f"Histogram of Average {selected_metric_name}",
            labels={"average_value": f"Average {unit_label}"},
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    elif chart_type == "Violin Plot":
        if len(df_avg_results) < 2:
            st.warning("Not enough data points (minimum 2) to draw a violin plot.")
        else:
            st.markdown(f"###### Key Statistics ({unit_label})")
            avg_val = df_avg_results["average_value"].mean()
            median_val = df_avg_results["average_value"].median()
            # ... (ваши st.columns с метриками)
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            stat_col1.metric("Average", f"{avg_val:,.2f}")
            stat_col2.metric("Median", f"{median_val:,.2f}")
            # ...

            st.markdown("###### Distribution (Violin Plot)")
            fig_violin = px.violin(
                df_avg_results,
                x="average_value",
                box=True,
                points="all",
                title=f"Distribution of Average {selected_metric_name}",
                labels={"average_value": f"Average {unit_label}"},
            )
            st.plotly_chart(fig_violin, use_container_width=True)

    elif chart_type == 'Treemap':
        st.markdown("###### Comparison (Treemap)")
        df_treemap = df_avg_results[df_avg_results['average_value'] > 0]
        if df_treemap.empty:
            st.warning(f"No positive {unit_label} data available for Treemap.")
        else:
            fig_treemap = px.treemap(
                df_treemap,
                path=[px.Constant("All Companies"), 'company'],
                values='average_value',
                title=f"Average {selected_metric_name} by Company",
                hover_data=['average_value']
            )
            st.plotly_chart(fig_treemap, use_container_width=True)

    elif chart_type == 'Bar Chart':
        st.markdown("###### Company Ranking (Top 50)")

        # Берем Top 50, иначе график будет нечитаемым
        df_bar = df_avg_results.head(50)

        fig_bar = px.bar(
            df_bar.sort_values(by="average_value", ascending=True),  # Сортируем для Bar chart
            y="company",
            x="average_value",
            color="Company Type",  # <--- ВОТ ВАШИ "ФЛАЖКИ" С ПОДПИСЯМИ
            title=f"Top 50 Companies by {selected_metric_name}",
            labels={"average_value": f"Average {unit_label}", "company": "Company"},
            color_discrete_map={
                'Tier A Leader': 'orange',
                'Other Company': 'steelblue'
            },
            height=800  # Может понадобиться высота для 50 компаний
        )
        fig_bar.update_layout(yaxis_title="Company")
        st.plotly_chart(fig_bar, use_container_width=True)

    # 6. Экспандер с данными
    with st.expander("Show detailed average data (including outliers)"):
        st.dataframe(
            df_avg_results,
            column_config={
                "average_value": st.column_config.NumberColumn(
                    f"Avg. {unit_label}", format="%.2f"
                ),
                "years_of_data": st.column_config.NumberColumn(
                    "Data Points (Max 3)", format="%d"
                ),
            },
            use_container_width=True,
            hide_index=True,
        )

# --- Основная часть приложения ---

# 1. Настройка страницы
st.set_page_config(layout="wide", page_title="Industry Overview Dashboard")
st.title("Industry Overview Dashboard")

# 2. Загрузка данных
# В реальном коде замените это на:
try:
    df_metrics = pd.read_csv("comparable_metrics.csv")
    df_topics = pd.read_csv("material_topics.csv")
    df_leaders = pd.read_csv("industry_leaders.csv")

    size_map = df_metrics[['company', 'company_size']].drop_duplicates()
    # 1. Обогащаем 'df_leaders' данными о размере
    df_leaders_merged = df_leaders.merge(size_map, on='company', how='left')

except FileNotFoundError:
    st.error(
        "Error: CSV files not found. Make sure 'comparable_metrics.csv', 'material_topics.csv' and 'industry_leaders.csv' are in the same folder."
    )
    st.stop()
# df_metrics, df_topics = load_mock_data()

# 3. Фильтры в боковой панели
st.sidebar.header("Filters")

# Фильтр по стране
unique_countries = sorted(df_metrics['country'].unique())
select_all_countries = st.sidebar.checkbox("Select All Countries", value=True)

if select_all_countries:
    selected_countries = st.sidebar.multiselect(
        'Country',
        options=unique_countries,
        default=list(unique_countries)
    )
else:
    selected_countries = st.sidebar.multiselect(
        'Country',
        options=unique_countries,
        default=[]
    )

# Фильтр по размеру компании
st.sidebar.markdown("---")
st.sidebar.subheader('Company Size')
unique_sizes = sorted(df_metrics['company_size'].unique())
selected_sizes = []

for size in unique_sizes:
    if st.sidebar.checkbox(size, value=True):
        selected_sizes.append(size)

# 4. Применение фильтров
df_filtered = df_metrics[
    (df_metrics['country'].isin(selected_countries)) &
    (df_metrics['company_size'].isin(selected_sizes))
    ]

# Проверка, есть ли данные после фильтрации
if df_filtered.empty:
    st.warning("No data for selected filters.")
    st.stop()

# --- Подготовка общих данных для вкладок ---
# Карта 'company' -> 'company_size' (нужна для df_topics и df_leaders)
# (Перенесено из вкладки 2)
size_map = df_metrics[['company', 'company_size']].drop_duplicates()

# 5. Блок 1: Статистические данные (KPIs)
st.header("Our Database Statistics")
st.markdown("---")

cols = st.columns(5)  # Создаем 5 колонок для метрик

# Метрика 1: Количество экстрагированных метрик
kpi_metric_count = df_filtered.shape[0]
cols[0].metric(label="Total Data Points", value=kpi_metric_count)

# Метрика 2: Количество уникальных бандлов
kpi_bundle_count = df_filtered['bundle_id'].nunique()
cols[1].metric(label="Unique Reports", value=kpi_bundle_count)

# Метрика 3: Количество компаний
kpi_company_count = df_filtered['company_id'].nunique()
cols[2].metric(label="Unique Companies", value=kpi_company_count)

# Метрика 4: Количество стран
kpi_country_count = df_filtered['country'].nunique()
cols[3].metric(label="Countries Covered", value=kpi_country_count)

# Метрика 5: Диапазон годов
min_year = df_filtered['year'].min()
max_year = df_filtered['year'].max()
cols[4].metric(label="Year Range", value=f"{min_year} - {max_year}")

st.markdown("---")

# 6. Блок 2: Таблица со списком использованных файлов (под спойлером)
st.header("Reports Used")

with st.expander("Click to show list", expanded=True):
    # Добавляем "фейковую" кнопку "Compare" (теперь ВНУТРИ спойлера)
    st.button("Compare selected", key="compare_main")

    # Готовим таблицу: компания, страна, индустрия, год
    # Нам нужны только уникальные комбинации
    df_reports_list = df_filtered[
        ['company', 'country', 'industry', 'year']
    ].drop_duplicates().sort_values(by=['company', 'year']).reset_index(drop=True)

    # 1. Добавляем поле для чекбокса "compare"
    df_reports_list['compare'] = False

    # 2. Добавляем поле-placeholder для ссылки
    df_reports_list['report_link'] = "http://etoso.io/placeholder_link"

    # Используем st.data_editor для интерактивной таблицы
    edited_df = st.data_editor(
        df_reports_list,
        column_config={
            "compare": st.column_config.CheckboxColumn(
                "To Comparison",
                default=False,
            ),
            "report_link": st.column_config.LinkColumn(
                "Report Link",
                display_text="🔗 View"
            )
        },
        # Меняем порядок столбцов, 'compare' теперь последний
        column_order=('company', 'country', 'industry', 'year', 'report_link', 'compare'),
        use_container_width=True,
        hide_index=True,
    )

st.markdown("---")

# 1. Фильтруем 'df_leaders_merged' по *фильтрам сайдбара*
# (df_leaders_merged у нас уже загружен и кэширован)
df_leaders_sidebar_filtered = df_leaders_merged[
    (df_leaders_merged['country'].isin(selected_countries)) &
    (df_leaders_merged['company_size'].isin(selected_sizes))
]

# 2. Из них выбираем *только* Tier A и получаем уникальный список
tier_a_companies_list = df_leaders_sidebar_filtered[
    df_leaders_sidebar_filtered['tier'] == "A"

]['company'].unique().tolist()
# 7. Блок 3: Вкладки с аналитикой (НОВЫЙ БЛОК)
st.header("Industry Overview")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Geography", "Common Disclosures", "Industry Leaders", "Performance", "Trends"])

# --- Вкладка 1: География ---
with tab1:
    st.subheader("Companies Map")

    # Готовим данные для карты: считаем уникальные компании по странам
    df_geo = df_filtered.groupby(['country', 'country_iso3'])['company_id'].nunique().reset_index(name='company_count')

    if df_geo.empty:
        st.warning("Нет данных для отображения карты.")
    else:
        fig = px.choropleth(
            df_geo,
            locations="country_iso3",  # Используем ISO код для построения
            color="company_count",  # Раскрашиваем по кол-ву компаний
            hover_name="country",  # Показываем имя страны при наведении
            color_continuous_scale=px.colors.sequential.Plasma,
            title="Unique Companies by Country"
        )
        # Убираем лишние отступы, чтобы карта занимала больше места
        fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
        st.plotly_chart(fig, use_container_width=True)

# --- Вкладка 2: Common Disclosures ---
with tab2:
    st.subheader("Common Disclosures (Top 10)")
    st.write("Click on a category to see the top 10 topics for that category.")

    # 1. Обогащаем df_topics информацией о размере
    df_topics_merged = df_topics.merge(size_map, on='company', how='left')

    # 2. Фильтруем df_topics по фильтрам из сайдбара
    df_topics_filtered = df_topics_merged[
        (df_topics_merged['country'].isin(selected_countries)) &
        (df_topics_merged['company_size'].isin(selected_sizes))
        ]

    if df_topics_filtered.empty or kpi_company_count == 0:
        st.warning("Нет данных по темам для выбранных фильтров.")
    else:
        # 3. Готовим данные для ГРАФИКА 1 (Категории)
        companies_per_category = df_topics_filtered.groupby('category_name')['company'].nunique().reset_index(
            name='company_count')
        companies_per_category['share_pct'] = (companies_per_category['company_count'] / kpi_company_count) * 100
        # Берем Топ-10
        top_10_categories = companies_per_category.nlargest(10, 'share_pct')

        # 4. Готовим данные для ГРАФИКА 2 (Топики)
        # ВАЖНО: здесь мы берем ВСЕ топики, а не топ-10,
        # так как Топ-10 будет считаться *после* фильтрации
        companies_per_topic = df_topics_filtered.groupby(['category_name', 'topic_name'])[
            'company'].nunique().reset_index(name='company_count')
        companies_per_topic['share_pct'] = (companies_per_topic['company_count'] / kpi_company_count) * 100

        # 5. Создаем селектор (выбор)
        # empty='all' означает, что по умолчанию выбраны ВСЕ категории
        category_selection = alt.selection_point(
            fields=['category_name'], empty='all'
        )

        # 6. Создаем колонки для графиков
        col1, col2 = st.columns(2)

        with col1:
            # --- ГРАФИК 1: КАТЕГОРИИ ---
            st.subheader("Top 10 Categories")
            chart_cat = alt.Chart(top_10_categories).mark_bar().encode(
                x=alt.X('share_pct', title="Доля компаний (%)"),
                y=alt.Y('category_name', title="Категория", sort='-x'),
                # Цвет меняется при клике
                color=alt.condition(
                    category_selection,
                    alt.value('orange'),  # Цвет при выборе
                    alt.value('steelblue') # Стандартный цвет
                ),
                tooltip=[
                    alt.Tooltip('category_name', title='Категория'),
                    alt.Tooltip('company_count', title='Кол-во компаний'),
                    alt.Tooltip('share_pct', title='Доля', format='.1f')
                ]
            ).add_params(
                category_selection # Применяем селектор
            ).properties(
                title="Top 10 Categories by disclosure frequency"
            ).interactive() # Позволяет зумить (хотя здесь не нужно, но полезно)


        with col2:
            # --- ГРАФИК 2: ТОПИКИ (Фильтруемый) ---
            st.subheader("Top 10 topics")

            chart_topic = alt.Chart(companies_per_topic).mark_bar().encode(
                x=alt.X('share_pct', title="Доля компаний (%)"),
                y=alt.Y('topic_name', title="Топик", sort='-x'), # Сортировка по убыванию
                tooltip=[
                    alt.Tooltip('topic_name', title='Топик'),
                    alt.Tooltip('company_count', title='Кол-во компаний'),
                    alt.Tooltip('share_pct', title='Доля', format='.1f')
                ]
            ).transform_filter(
                category_selection # <--- ГЛАВНАЯ СВЯЗЬ: фильтруем по выбору
            ).transform_window(
                # Ранжируем топики *после* фильтрации
                rank='rank()',
                sort=[alt.SortField('share_pct', order='descending')]
            ).transform_filter(
                alt.datum.rank <= 10 # Оставляем только Топ 10
            ).properties(
                title="Top 10 topics in selected category"
            ).interactive()

    combined_chart = chart_cat | chart_topic
    st.altair_chart(combined_chart, use_container_width=True)

# --- Вкладка 3: Industry Leaders ---
with tab3:
    st.subheader("Industry Leaders")

    # 3.1 Фильтры для Tier
    cols_tier = st.columns(2)
    tier_a_selected = cols_tier[0].checkbox("Tier A", value=True)
    tier_b_selected = cols_tier[1].checkbox("Tier B", value=True)

    selected_tiers = []
    if tier_a_selected:
        selected_tiers.append("A")
    if tier_b_selected:
        selected_tiers.append("B")

    # 3.2 Фильтрация данных df_leaders

    # 2. Применяем все фильтры (из сайдбара и из вкладки)
    df_leaders_filtered = df_leaders_merged[
        (df_leaders_merged['country'].isin(selected_countries)) &
        (df_leaders_merged['company_size'].isin(selected_sizes)) &
        (df_leaders_merged['tier'].isin(selected_tiers))
        ]

    if df_leaders_filtered.empty:
        st.warning("Нет данных, соответствующих выбранным фильтрам.")
    else:
        # 3.3 Кнопка Сравнения
        st.button("Compare selected Leaders", key="compare_leaders")

        # 3.4 Подготовка таблицы
        # (bundle_id,company,year,tier,country)
        df_leaders_display = df_leaders_filtered[
            ['company', 'country', 'year', 'tier']
        ].drop_duplicates().sort_values(by=['company', 'year'])

        # Добавляем 'compare' и 'report_link'
        df_leaders_display['compare'] = False
        df_leaders_display['report_link'] = "http://etoso.io/leader_report_link"

        # 3.5 Отображение таблицы
        st.data_editor(
            df_leaders_display,
            column_config={
                "compare": st.column_config.CheckboxColumn(
                    "To comparison",
                    default=False,
                ),
                "report_link": st.column_config.LinkColumn(
                    "Report Link",
                    display_text="🔗 View"
                )
            },
            column_order=('company', 'country', 'year', 'tier', 'report_link', 'compare'),
            use_container_width=True,
            hide_index=True,
        )

# --- Tab 4: Performance ---
with tab4:
    st.subheader("Performance Analytics")

    # Создаем подвкладки
    subtab_ghg, subtab_energy, subtab_waste, subtab_water = st.tabs(
        ["GHG Emissions", "Energy Consumption", "Waste", "Water"])

    # --- Подвкладка 1: GHG (как и была) ---
    with subtab_ghg:
        st.subheader("GHG Emissions (Scope 1, 2, 3) Analysis")

        # Чекбоксы для Scopes
        st.markdown("**Select Scopes to aggregate:**")
        cols_scope = st.columns(3)
        use_scope1 = cols_scope[0].checkbox("Scope 1 (GRI 305-1-a)", value=True, key="ghg_scope1")
        use_scope2 = cols_scope[1].checkbox("Scope 2 (GRI 305-2-a)", value=True, key="ghg_scope2")
        use_scope3 = cols_scope[2].checkbox("Scope 3 (GRI 305-3-a)", value=True, key="ghg_scope3")

        selected_scopes = []
        if use_scope1: selected_scopes.append('305-1-a')
        if use_scope2: selected_scopes.append('305-2-a')
        if use_scope3: selected_scopes.append('305-3-a')

        if not selected_scopes:
            st.warning("Please select at least one Scope.")
        else:
            df_ghg = df_filtered[df_filtered['sub_code'].isin(selected_scopes)].copy()

            if df_ghg.empty:
                st.warning("No GHG data found for the selected filters and Scopes.")
            else:
                df_annual_sums = df_ghg.groupby(['company', 'year'])['value'].sum().reset_index()
                company_averages = []

                for company in df_annual_sums['company'].unique():
                    df_company_data = df_annual_sums[df_annual_sums['company'] == company].sort_values(by='year',
                                                                                                       ascending=False)
                    latest_3_values = df_company_data.head(3)['value']

                    if not latest_3_values.empty:
                        avg_value = latest_3_values.mean()
                        company_averages.append({
                            'company': company,
                            'average_ghg': avg_value,
                            'years_of_data': len(latest_3_values)
                        })

                if not company_averages:
                    st.warning("Not enough data to calculate averages.")
                else:
                    df_avg_results = pd.DataFrame(company_averages).sort_values(by='average_ghg', ascending=False)
                    st.subheader("Average Emissions Distribution")

                    chart_type = st.radio(
                        "Выберите тип графика:",
                        ('Histogram', 'Violin Plot', 'Treemap'),
                        horizontal=True,
                        label_visibility="collapsed",
                        key="ghg_chart_type"
                    )

                    if chart_type == 'Histogram':
                        st.markdown("###### Distribution (Histogram)")
                        # Exclude 5% outliers on each side for histogram
                        q_low = df_avg_results['average_ghg'].quantile(0.05)
                        q_high = df_avg_results['average_ghg'].quantile(0.95)
                        df_hist = df_avg_results[
                            (df_avg_results['average_ghg'] >= q_low) & (df_avg_results['average_ghg'] <= q_high)
                        ]
                        st.warning("Histogram excludes the lowest and highest 5% of values to reduce outlier impact.")
                        fig_ghg_hist = px.histogram(
                            df_hist,
                            x='average_ghg',
                            nbins=30,
                            title="Histogram of Average GHG Emissions per Company",
                            labels={'average_ghg': 'Average Emissions (tCO2e)'}
                        )
                        fig_ghg_hist.update_layout(xaxis_title="Average Emissions (tCO2e)", yaxis_title="Count")
                        st.plotly_chart(fig_ghg_hist, use_container_width=True)

                    elif chart_type == 'Violin Plot':
                        if len(df_avg_results) < 2:
                            st.warning("Not enough data points (minimum 2) to draw a violin plot.")
                        else:
                            # --- START: Новый блок статистики ---
                            st.markdown("###### Key Statistics (tCO2e)")
                            avg_val = df_avg_results['average_ghg'].mean()
                            median_val = df_avg_results['average_ghg'].median()
                            min_val = df_avg_results['average_ghg'].min()
                            max_val = df_avg_results['average_ghg'].max()

                            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                            stat_col1.metric("Average", f"{avg_val:,.2f}")
                            stat_col2.metric("Median", f"{median_val:,.2f}")
                            stat_col3.metric("Min", f"{min_val:,.2f}")
                            stat_col4.metric("Max", f"{max_val:,.2f}")
                            # --- END: Новый блок статистики ---

                            st.markdown("###### Distribution (Violin Plot)")
                            fig_ghg_violin = px.violin(
                                df_avg_results,
                                x='average_ghg',
                                box=True,
                                points='all',
                                title="Distribution of Average GHG Emissions per Company",
                                labels={'average_ghg': 'Average Emissions (tCO2e)'}
                            )
                            fig_ghg_violin.update_layout(xaxis_title="Average Emissions (tCO2e)")
                            st.plotly_chart(fig_ghg_violin, use_container_width=True)

                    elif chart_type == 'Treemap':
                        st.markdown("###### Comparison (Treemap)")
                        df_treemap = df_avg_results[df_avg_results['average_ghg'] > 0]
                        if df_treemap.empty:
                            st.warning("No positive emission data available for Treemap.")
                        else:
                            fig_ghg_treemap = px.treemap(
                                df_treemap,
                                path=[px.Constant("All Companies"), 'company'],
                                values='average_ghg',
                                title="Average GHG Emissions by Company (Treemap)",
                                hover_data=['average_ghg']
                            )
                            fig_ghg_treemap.update_traces(textinfo="label+value")
                            st.plotly_chart(fig_ghg_treemap, use_container_width=True)

                    with st.expander("Show detailed average data (including outliers)"):
                        st.dataframe(
                            df_avg_results,
                            column_config={
                                "average_ghg": st.column_config.NumberColumn("Avg. GHG", format="%.2f"),
                                "years_of_data": st.column_config.NumberColumn("Data Points (Max 3)", format="%d")
                            },
                            use_container_width=True,
                            hide_index=True
                        )

        # --- Подвкладка 2: Energy Consumption ---

    with subtab_energy:
        metric_options = {
            "Total energy consumption (GRI 302-1-e)": ['302-1-e'],
            "Consumption of electricity, heating, etc. (GRI 302-1-c)": ['302-1-c'],
            "Fuel consumption (GRI 302-1-a + 302-1-b)": ['302-1-a', '302-1-b']
        }
        create_performance_analytics_tab(
            df_filtered,
            metric_options,
            metric_key_prefix="energy",
            unit_label="GJ",
            tier_a_leaders_list=tier_a_companies_list
        )

    with subtab_waste:
        metric_options = {
            "Generated waste (GRI 306-3-a)": ['306-3-a'],
            "Recycled waste (GRI 306-4-a)": ['306-4-a'],
            "Landfilled waste (GRI 306-5-c)": ['306-5-c'],
            "Incinerated waste (GRI 306-5-a)": ['306-5-a']
        }
        create_performance_analytics_tab(
            df_filtered,
            metric_options,
            metric_key_prefix="waste",
            unit_label="tons",
            tier_a_leaders_list=tier_a_companies_list
        )

    with subtab_water:
        metric_options = {
            "Water consumption (GRI 303-5-a)": ['303-5-a'],
            "Water consumption from water-stressed areas (GRI 303-5-b)": ['303-5-b']
        }
        create_performance_analytics_tab(
            df_filtered,
            metric_options,
            metric_key_prefix="water",
            unit_label="m3",
            tier_a_leaders_list=tier_a_companies_list
        )

# --- Tab 5: Trends ---
with tab5:
    st.subheader("Year-over-Year Trends")
    st.write("Analyze the average relative percentage change in metrics across companies.")

    # Metric selection
    trend_metrics = {
        "GHG Emissions (Scope 1+2+3)": ['305-1-a', '305-2-a', '305-3-a'],
        "Total Energy Consumption (GRI 302-1-e)": ['302-1-e'],
        "Generated Waste (GRI 306-3-a)": ['306-3-a'],
        "Water Consumption (GRI 303-5-a)": ['303-5-a']
    }

    selected_trend_metric = st.selectbox(
        "Select metric to analyze:",
        options=trend_metrics.keys(),
        key="trend_metric_select"
    )

    selected_trend_codes = trend_metrics[selected_trend_metric]

    # Filter data
    df_trend = df_filtered[df_filtered['sub_code'].isin(selected_trend_codes)].copy()

    if df_trend.empty:
        st.warning(f"No data found for '{selected_trend_metric}'.")
    else:
        # Sum values by company and year (in case multiple sub_codes are selected)
        df_company_year = df_trend.groupby(['company', 'year'])['value'].sum().reset_index()
        df_company_year = df_company_year.sort_values(by=['company', 'year'])

        # Calculate YoY change for each company
        company_changes = []

        for company in df_company_year['company'].unique():
            df_company = df_company_year[df_company_year['company'] == company].copy()

            # Calculate percentage change for this company
            df_company['yoy_change_pct'] = df_company['value'].pct_change() * 100

            # Only keep rows with valid YoY changes
            df_company_valid = df_company[df_company['yoy_change_pct'].notna()]

            # Add to our list
            for _, row in df_company_valid.iterrows():
                company_changes.append({
                    'company': company,
                    'year': row['year'],
                    'yoy_change_pct': row['yoy_change_pct']
                })

        if not company_changes:
            st.warning(
                "Not enough data to calculate year-over-year changes. Each company needs at least 2 consecutive years of data.")
        else:
            df_company_changes = pd.DataFrame(company_changes)

            # Calculate average YoY change per year across all companies
            df_avg_yoy = df_company_changes.groupby('year').agg({
                'yoy_change_pct': ['mean', 'median', 'count']
            }).reset_index()

            # Flatten column names
            df_avg_yoy.columns = ['year', 'mean_yoy_change', 'median_yoy_change', 'company_count']
            df_avg_yoy = df_avg_yoy.sort_values(by='year')

            # Create line chart
            st.markdown("###### Average Year-over-Year Percentage Change")

            # Key insights
            st.markdown("###### Key Insights")
            cols_insights = st.columns(3)

            # Average growth rate
            overall_avg = df_avg_yoy['mean_yoy_change'].mean()
            cols_insights[0].metric("Overall Average YoY Change", f"{overall_avg:.2f}%")

            # Max growth
            max_growth = df_avg_yoy['mean_yoy_change'].max()
            max_growth_year = df_avg_yoy.loc[df_avg_yoy['mean_yoy_change'].idxmax(), 'year']
            cols_insights[1].metric(
                "Highest Average Growth",
                f"{max_growth:.2f}%",
                delta=f"in {int(max_growth_year)}"
            )

            # Max decline
            min_growth = df_avg_yoy['mean_yoy_change'].min()
            min_growth_year = df_avg_yoy.loc[df_avg_yoy['mean_yoy_change'].idxmin(), 'year']
            cols_insights[2].metric(
                "Largest Average Decline",
                f"{min_growth:.2f}%",
                delta=f"in {int(min_growth_year)}"
            )

            st.info(f"This chart shows the average YoY change calculated across individual companies for each year.")

            fig_trend = px.line(
                df_avg_yoy,
                x='year',
                y='mean_yoy_change',
                markers=True,
                title=f"Average Year-over-Year Change in {selected_trend_metric}",
                labels={
                    'year': 'Year',
                    'mean_yoy_change': 'Average YoY Change (%)'
                }
            )

            # Add a horizontal line at y=0 for reference
            fig_trend.add_hline(
                y=0,
                line_dash="dash",
                line_color="gray",
                annotation_text="No change",
                annotation_position="right"
            )

            # Color code positive/negative changes
            fig_trend.update_traces(
                line=dict(color='steelblue', width=3),
                marker=dict(size=10)
            )

            # Add custom hover data
            fig_trend.update_traces(
                customdata=df_avg_yoy[['company_count']],
                hovertemplate='<b>Year: %{x}</b><br>Avg YoY Change: %{y:.2f}%<br>Companies: %{customdata[0]}<extra></extra>'
            )

            fig_trend.update_layout(
                xaxis_title="Year",
                yaxis_title="Average Year-over-Year Change (%)",
                hovermode='x unified'
            )

            st.plotly_chart(fig_trend, use_container_width=True)

            # Show detailed data in expander
            with st.expander("Show detailed trend data"):
                display_df = df_avg_yoy.copy()
                display_df.columns = ['Year', 'Mean YoY Change (%)', 'Median YoY Change (%)', 'Number of Companies']
                st.dataframe(
                    display_df,
                    column_config={
                        "Year": st.column_config.NumberColumn("Year", format="%d"),
                        "Mean YoY Change (%)": st.column_config.NumberColumn("Mean YoY Change (%)", format="%.2f"),
                        "Median YoY Change (%)": st.column_config.NumberColumn("Median YoY Change (%)", format="%.2f"),
                        "Number of Companies": st.column_config.NumberColumn("Companies", format="%d")
                    },
                    use_container_width=True,
                    hide_index=True
                )
