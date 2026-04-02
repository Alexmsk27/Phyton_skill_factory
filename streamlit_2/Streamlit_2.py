import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from datetime import datetime

# Настройка страницы (широкий режим для удобства)
st.set_page_config(
    page_title="CSV Аналитик",
    page_icon="📊",
    layout="wide"
)

# Заголовок приложения
st.title("📊 Анализ CSV файлов")
st.markdown("---")

# Боковая панель для загрузки файла
with st.sidebar:
    st.header("📁 Загрузка данных")

    # Загрузка CSV файла
    uploaded_file = st.file_uploader(
        "Выберите CSV файл",
        type=['csv'],
        help="Загрузите файл в формате CSV"
    )

    st.markdown("---")
    st.markdown("### ℹ️ Инструкция")
    st.markdown("""
    1. Загрузите CSV файл
    2. Просмотрите данные
    3. Выберите столбцы для анализа
    4. Постройте графики
    """)

# Проверяем, загружен ли файл
if uploaded_file is not None:
    # Читаем CSV файл
    try:
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ Файл '{uploaded_file.name}' успешно загружен!")
        st.info(f"📊 Размер данных: {df.shape[0]} строк × {df.shape[1]} столбцов")
    except Exception as e:
        st.error(f"Ошибка при загрузке файла: {e}")
        st.stop()

    # Создаем вкладки для разных функций
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Просмотр данных",
        "📊 Статистика",
        "📈 Графики",
        "💾 Экспорт"
    ])

    # ==================== ВКЛАДКА 1: ПРОСМОТР ДАННЫХ ====================
    with tab1:
        st.subheader("Просмотр данных")

        # Настройка отображения
        rows_count = st.slider("Количество строк для отображения", 5, 50, 10)

        # Выбор столбцов для отображения
        all_columns = df.columns.tolist()
        selected_columns = st.multiselect(
            "Выберите столбцы для отображения",
            all_columns,
            default=all_columns[:3]  # По умолчанию показываем первые 3 столбца
        )

        # Показываем таблицу
        if selected_columns:
            st.dataframe(df[selected_columns].head(rows_count))
        else:
            st.warning("Выберите хотя бы один столбец для отображения")

        # Информация о типах данных
        st.subheader("Информация о столбцах")
        info_df = pd.DataFrame({
            'Столбец': df.columns,
            'Тип данных': df.dtypes.astype(str),
            'Уникальных значений': [df[col].nunique() for col in df.columns],
            'Пропусков': [df[col].isnull().sum() for col in df.columns]
        })
        st.dataframe(info_df)

    # ==================== ВКЛАДКА 2: СТАТИСТИКА ====================
    with tab2:
        st.subheader("Статистический анализ")

        # Находим только числовые столбцы
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_columns) > 0:
            # Выбираем столбец для анализа
            selected_col = st.selectbox(
                "Выберите числовой столбец для анализа",
                numeric_columns
            )

            if selected_col:
                # Убираем пустые значения
                data = df[selected_col].dropna()

                # Рассчитываем статистику
                mean_value = data.mean()
                median_value = data.median()
                std_value = data.std()
                min_value = data.min()
                max_value = data.max()

                # Показываем статистику в виде метрик
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Среднее", f"{mean_value:.2f}")
                    st.metric("Медиана", f"{median_value:.2f}")

                with col2:
                    st.metric("Стандартное отклонение", f"{std_value:.2f}")
                    st.metric("Размах", f"{max_value - min_value:.2f}")

                with col3:
                    st.metric("Минимум", f"{min_value:.2f}")
                    st.metric("Максимум", f"{max_value:.2f}")

                with col4:
                    st.metric("Количество значений", len(data))
                    st.metric("Пропущено", df[selected_col].isnull().sum())

                # Показываем полную описательную статистику
                st.subheader("Детальная статистика")
                st.dataframe(df[selected_col].describe())
        else:
            st.warning("Нет числовых столбцов для анализа")

    # ==================== ВКЛАДКА 3: ГРАФИКИ ====================
    with tab3:
        st.subheader("Построение графиков")

        # Находим числовые столбцы
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_columns) >= 2:
            # Выбор типа графика
            graph_type = st.selectbox(
                "Выберите тип графика",
                ["Линейный график", "Диаграмма рассеяния", "Гистограмма", "Box Plot"]
            )

            if graph_type == "Линейный график":
                col1, col2 = st.columns(2)

                with col1:
                    x_column = st.selectbox("Ось X", df.columns)

                with col2:
                    y_column = st.selectbox("Ось Y", numeric_columns)

                if st.button("Построить график"):
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.plot(df[x_column], df[y_column], marker='o', linewidth=2, markersize=4)
                    ax.set_xlabel(x_column, fontsize=12)
                    ax.set_ylabel(y_column, fontsize=12)
                    ax.set_title(f"График зависимости {y_column} от {x_column}", fontsize=14)
                    ax.grid(True, alpha=0.3)
                    plt.xticks(rotation=45)
                    st.pyplot(fig)

                    # Сохраняем график в сессию для экспорта
                    st.session_state['current_plot'] = fig

            elif graph_type == "Диаграмма рассеяния":
                col1, col2 = st.columns(2)

                with col1:
                    x_column = st.selectbox("Ось X", numeric_columns)

                with col2:
                    y_column = st.selectbox("Ось Y", numeric_columns)

                if st.button("Построить график"):
                    fig, ax = plt.subplots(figsize=(10, 8))
                    ax.scatter(df[x_column], df[y_column], alpha=0.6, c='blue')
                    ax.set_xlabel(x_column, fontsize=12)
                    ax.set_ylabel(y_column, fontsize=12)
                    ax.set_title(f"Диаграмма рассеяния: {y_column} vs {x_column}", fontsize=14)
                    ax.grid(True, alpha=0.3)
                    st.pyplot(fig)
                    st.session_state['current_plot'] = fig

            elif graph_type == "Гистограмма":
                selected_col = st.selectbox("Выберите столбец", numeric_columns)
                bins_count = st.slider("Количество столбцов гистограммы", 5, 50, 20)

                if st.button("Построить график"):
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.hist(df[selected_col].dropna(), bins=bins_count, edgecolor='black', alpha=0.7)
                    ax.set_xlabel(selected_col, fontsize=12)
                    ax.set_ylabel("Частота", fontsize=12)
                    ax.set_title(f"Распределение {selected_col}", fontsize=14)
                    ax.grid(True, alpha=0.3)
                    st.pyplot(fig)
                    st.session_state['current_plot'] = fig

            elif graph_type == "Box Plot":
                selected_cols = st.multiselect(
                    "Выберите столбцы для Box Plot",
                    numeric_columns,
                    default=numeric_columns[:2]
                )

                if selected_cols and st.button("Построить график"):
                    fig, ax = plt.subplots(figsize=(10, 6))
                    df[selected_cols].boxplot(ax=ax)
                    ax.set_title("Box Plot - Распределение данных", fontsize=14)
                    ax.set_ylabel("Значения", fontsize=12)
                    ax.grid(True, alpha=0.3)
                    st.pyplot(fig)
                    st.session_state['current_plot'] = fig

        else:
            st.warning(f"Недостаточно числовых столбцов для построения графиков. Найдено: {len(numeric_columns)}")

    # ==================== ВКЛАДКА 4: ЭКСПОРТ ====================
    with tab4:
        st.subheader("Экспорт результатов")

        # Экспорт графика
        if 'current_plot' in st.session_state and st.session_state['current_plot'] is not None:
            st.markdown("### Сохранить график")

            # Конвертируем график в PNG
            buf = BytesIO()
            st.session_state['current_plot'].savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)

            # Создаем ссылку для скачивания
            b64 = base64.b64encode(buf.read()).decode()
            filename = f"graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            href = f'<a href="data:image/png;base64,{b64}" download="{filename}">📥 Скачать график (PNG)</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.info("Сначала постройте график на вкладке 'Графики'")

        st.markdown("---")

        # Экспорт данных
        st.markdown("### Сохранить данные")

        # Выбор формата экспорта
        export_format = st.selectbox("Выберите формат", ["CSV", "Excel"])

        if st.button("Экспортировать данные"):
            if export_format == "CSV":
                # Конвертируем в CSV
                csv_data = df.to_csv(index=False)
                b64 = base64.b64encode(csv_data.encode()).decode()
                filename = f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Скачать CSV</a>'
                st.markdown(href, unsafe_allow_html=True)

            elif export_format == "Excel":
                # Конвертируем в Excel
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Data')
                output.seek(0)
                b64 = base64.b64encode(output.read()).decode()
                filename = f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">📥 Скачать Excel</a>'
                st.markdown(href, unsafe_allow_html=True)

        # Информация о текущем файле
        st.markdown("---")
        st.markdown("### Информация о файле")
        st.write(f"**Имя файла:** {uploaded_file.name}")
        st.write(f"**Строк:** {df.shape[0]}")
        st.write(f"**Столбцов:** {df.shape[1]}")
        st.write(f"**Числовых столбцов:** {len(numeric_columns)}")

else:
    # Если файл не загружен, показываем инструкцию
    st.info("👈 Загрузите CSV файл через боковую панель для начала работы")

    st.markdown("""
    ### Как пользоваться:

    1. **Загрузите CSV файл** с левой боковой панели
    2. **Просмотрите данные** в первой вкладке
    3. **Проанализируйте статистику** числовых столбцов
    4. **Постройте графики** для визуализации
    5. **Экспортируйте результаты** в нужном формате

    ### Поддерживаемые возможности:
    - ✅ Просмотр и фильтрация данных
    - ✅ Статистический анализ (среднее, медиана, std)
    - ✅ Построение графиков (линейные, scatter, гистограммы)
    - ✅ Экспорт в CSV и Excel
    - ✅ Сохранение графиков в PNG
    """)