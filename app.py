import streamlit as st
import pandas as pd

# Налаштування сторінки
st.set_page_config(page_title='Дашборд Університету', page_icon='🎓', layout='wide')

st.title('🎓 Дашборд успішності студентів')

# --- 1. Завантаження даних через RAW-посилання ---
@st.cache_data
def load_data():
    # ТУТ ВСТАВТЕ ВАШЕ RAW-ПОСИЛАННЯ З GITHUB
    csv_url = "https://raw.githubusercontent.com/spammm2003/ab_task_2/refs/heads/main/students_data.csv"
    
    # Pandas автоматично завантажує та читає CSV за прямим посиланням
    return pd.read_csv(csv_url)

try:
    with st.spinner('Завантаження даних з репозиторію...'):
        df = load_data()
except Exception as e:
    st.error(f"🚨 Помилка завантаження даних. Перевірте правильність RAW-посилання.\n\n**Деталі помилки:** {e}")
    st.stop()

# --- 2. Бічна панель з фільтрами ---
st.sidebar.header('Фільтри')

# Отримуємо унікальні значення для фільтрів
groups = df['Група'].unique()
semesters = df['Семестр'].unique()
subjects = df['Предмет'].unique()

# Віджети фільтрів (мульти-вибір)
selected_groups = st.sidebar.multiselect('Оберіть групу:', groups, default=groups)
selected_semesters = st.sidebar.multiselect('Оберіть семестр:', semesters, default=semesters)
selected_subjects = st.sidebar.multiselect('Оберіть предмет:', subjects, default=subjects)

# Застосовуємо фільтри до DataFrame
filtered_df = df[
    (df['Група'].isin(selected_groups)) &
    (df['Семестр'].isin(selected_semesters)) &
    (df['Предмет'].isin(selected_subjects))
]

# --- 3. Відображення таблиці та базової статистики ---
st.subheader('Таблиця успішності')
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

if filtered_df.empty:
    st.warning("Немає даних за обраними фільтрами.")
    st.stop()

# --- 4. Діаграми середніх оцінок ---
st.divider()
st.subheader('📊 Діаграми середніх оцінок')

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Середній бал за предметами**")
    # Групуємо за предметом і рахуємо середнє
    avg_by_subject = filtered_df.groupby('Предмет')['Оцінка'].mean().reset_index()
    # Робимо Предмет індексом для красивого графіка
    st.bar_chart(avg_by_subject.set_index('Предмет'))

with col2:
    st.markdown("**Середній бал за групами**")
    # Групуємо за групою
    avg_by_group = filtered_df.groupby('Група')['Оцінка'].mean().reset_index()
    st.bar_chart(avg_by_group.set_index('Група'))

# --- 5. Аналіз кореляцій між предметами ---
st.divider()
st.subheader('🔗 Аналіз кореляцій між предметами')
st.write("Кореляційна матриця показує, як оцінки з одного предмета пов'язані з оцінками з іншого. Значення від -1 до 1.")

# Рядки - це студенти (і семестри), колонки - предмети, значення - оцінки
pivot_df = df.pivot_table(index=['Студент', 'Семестр'], columns='Предмет', values='Оцінка')

# Рахуємо матрицю кореляцій
corr_matrix = pivot_df.corr()

# Відображаємо матрицю з кольоровим градієнтом
st.dataframe(
    corr_matrix.style.background_gradient(cmap='coolwarm', axis=None).format("{:.2f}"),
    use_container_width=True
)

st.info("💡 **Як читати матрицю:** Якщо коефіцієнт наближається до 1, це означає сильну пряму залежність (студент, який добре знає 'Програмування', також добре здає 'Бази даних').")
