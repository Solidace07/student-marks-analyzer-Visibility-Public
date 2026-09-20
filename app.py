import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Student Marks Analyzer",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>
    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #777;
        margin-bottom: 25px;
    }

    .metric-card {
        padding: 10px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">📊 Student Marks Analyzer</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Analyze marks, rankings, grades and subject performance automatically.'
    '</div>',
    unsafe_allow_html=True
)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙️ Settings")

pass_mark = st.sidebar.number_input(
    "Pass mark",
    min_value=0,
    max_value=100,
    value=35
)

st.sidebar.info(
    "Upload a CSV containing student names and marks."
)

# =========================================================
# FILE UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "📁 Upload your student CSV file",
    type=["csv"]
)

if uploaded_file is None:

    st.info(
        "👆 Upload a CSV file to start the analysis."
    )

    st.markdown("### Example CSV")

    example = pd.DataFrame({
        "Name": ["Arun", "Bala", "Kavin", "Rahul", "Vijay"],
        "Class": [11, 11, 11, 11, 11],
        "Maths": [87, 72, 95, 64, 91],
        "Physics": [91, 70, 89, 67, 88],
        "Chemistry": [84, 76, 94, 61, 90]
    })

    st.dataframe(
        example,
        use_container_width=True,
        hide_index=True
    )

    st.stop()

# =========================================================
# READ CSV
# =========================================================

try:

    df = pd.read_csv(uploaded_file)

except Exception as e:

    st.error(
        f"❌ Could not read the CSV file.\n\n{e}"
    )

    st.stop()

# =========================================================
# BASIC CSV VALIDATION
# =========================================================

errors = []

warnings = []

# Empty file
if df.empty:

    errors.append(
        "The CSV file is empty."
    )

# Name column
if "Name" not in df.columns:

    errors.append(
        "Missing required column: Name"
    )

# Find numeric columns
numeric_columns = df.select_dtypes(
    include="number"
).columns.tolist()

# Remove Class from marks
mark_columns = [
    col for col in numeric_columns
    if col.lower() not in ["class", "roll", "rollno", "id"]
]

if len(mark_columns) == 0:

    errors.append(
        "No numeric subject/mark columns were found."
    )

# Check marks
for column in mark_columns:

    if df[column].isna().any():

        warnings.append(
            f"'{column}' contains empty marks."
        )

    invalid_values = (
        (df[column] < 0) |
        (df[column] > 100)
    ).sum()

    if invalid_values > 0:

        warnings.append(
            f"'{column}' contains {invalid_values} "
            "mark(s) outside 0–100."
        )

# Duplicate names
if "Name" in df.columns:

    duplicate_count = df["Name"].duplicated().sum()

    if duplicate_count > 0:

        warnings.append(
            f"{duplicate_count} duplicate student name(s) found."
        )

# =========================================================
# DISPLAY VALIDATION RESULTS
# =========================================================

if errors:

    st.error("❌ CSV validation failed.")

    for error in errors:

        st.write(
            f"• {error}"
        )

    st.stop()

if warnings:

    with st.expander(
        "⚠️ CSV warnings"
    ):

        for warning in warnings:

            st.write(
                f"• {warning}"
            )

# =========================================================
# DATA PREVIEW
# =========================================================

with st.expander(
    "📋 View uploaded data"
):

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

# =========================================================
# TOTAL STUDENTS
# =========================================================

total_students = len(df)

# =========================================================
# CALCULATE AVERAGE
# =========================================================

df["Average"] = df[mark_columns].mean(
    axis=1
)

# =========================================================
# TOTAL MARKS
# =========================================================

df["Total"] = df[mark_columns].sum(
    axis=1
)

# =========================================================
# RANK
# =========================================================

df["Rank"] = df["Average"].rank(
    ascending=False,
    method="min"
).astype(int)

# =========================================================
# GRADE FUNCTION
# =========================================================

def get_grade(mark):

    if mark >= 90:
        return "A+"

    elif mark >= 80:
        return "A"

    elif mark >= 70:
        return "B"

    elif mark >= 60:
        return "C"

    elif mark >= 50:
        return "D"

    elif mark >= pass_mark:
        return "E"

    else:
        return "F"


df["Grade"] = df["Average"].apply(
    get_grade
)

# =========================================================
# PASS / FAIL
# =========================================================

df["Result"] = df["Average"].apply(
    lambda x: "Pass"
    if x >= pass_mark
    else "Fail"
)

# =========================================================
# DASHBOARD METRICS
# =========================================================

st.subheader("📌 Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "👥 Students",
    total_students
)

col2.metric(
    "📚 Subjects",
    len(mark_columns)
)

col3.metric(
    "📈 Class Average",
    f"{df['Average'].mean():.2f}"
)

col4.metric(
    "🏆 Highest Average",
    f"{df['Average'].max():.2f}"
)

# =========================================================
# RANKING TABLE
# =========================================================

st.subheader("🏆 Student Ranking")

ranking_columns = [
    "Rank",
    "Name"
]

if "Class" in df.columns:
    ranking_columns.append("Class")

ranking_columns += [
    "Total",
    "Average",
    "Grade",
    "Result"
]

ranking = df.sort_values(
    "Rank"
)[ranking_columns]

st.dataframe(
    ranking,
    use_container_width=True,
    hide_index=True
)

# =========================================================
# SUBJECT-WISE ANALYSIS
# =========================================================

st.subheader("📊 Subject-wise Analysis")

subject_average = (
    df[mark_columns]
    .mean()
    .sort_values(ascending=False)
)

subject_table = pd.DataFrame({
    "Subject": subject_average.index,
    "Average Mark": subject_average.values
})

st.dataframe(
    subject_table,
    use_container_width=True,
    hide_index=True
)

# =========================================================
# SUBJECT PERFORMANCE CHART
# =========================================================

fig_subject = px.bar(
    subject_table,
    x="Subject",
    y="Average Mark",
    title="Average Marks by Subject",
    text_auto=".2f"
)

fig_subject.update_layout(
    yaxis_title="Average Mark",
    xaxis_title="Subject"
)

st.plotly_chart(
    fig_subject,
    use_container_width=True
)

# =========================================================
# TOP STUDENTS
# =========================================================

st.subheader("🥇 Top Students")

top_students = df.sort_values(
    "Average",
    ascending=False
).head(10)

fig_top = px.bar(
    top_students,
    x="Name",
    y="Average",
    title="Top 10 Students",
    text_auto=".2f"
)

st.plotly_chart(
    fig_top,
    use_container_width=True
)

# =========================================================
# PASS / FAIL
# =========================================================

st.subheader("✅ Pass / ❌ Fail")

pass_count = (
    df["Result"] == "Pass"
).sum()

fail_count = (
    df["Result"] == "Fail"
).sum()

col1, col2 = st.columns(2)

col1.metric(
    "✅ Passed",
    int(pass_count)
)

col2.metric(
    "❌ Failed",
    int(fail_count)
)

result_data = pd.DataFrame({
    "Result": ["Pass", "Fail"],
    "Students": [pass_count, fail_count]
})

fig_result = px.pie(
    result_data,
    names="Result",
    values="Students",
    title="Pass vs Fail"
)

st.plotly_chart(
    fig_result,
    use_container_width=True
)

# =========================================================
# GRADE DISTRIBUTION
# =========================================================

st.subheader("🎯 Grade Distribution")

grade_order = [
    "A+",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F"
]

grade_counts = (
    df["Grade"]
    .value_counts()
    .reindex(
        grade_order,
        fill_value=0
    )
)

grade_data = pd.DataFrame({
    "Grade": grade_counts.index,
    "Students": grade_counts.values
})

fig_grade = px.bar(
    grade_data,
    x="Grade",
    y="Students",
    title="Grade Distribution",
    text_auto=True
)

st.plotly_chart(
    fig_grade,
    use_container_width=True
)

# =========================================================
# STUDENT PERFORMANCE HEATMAP
# =========================================================

st.subheader("🔥 Student Performance Heatmap")

heatmap_data = df[
    ["Name"] + mark_columns
].set_index("Name")

fig_heatmap = px.imshow(
    heatmap_data,
    text_auto=True,
    aspect="auto",
    title="Marks by Student and Subject"
)

st.plotly_chart(
    fig_heatmap,
    use_container_width=True
)

# =========================================================
# DOWNLOAD REPORT
# =========================================================

st.subheader("📄 Download Report")

report_columns = []

for column in [
    "Rank",
    "Name",
    "Class"
]:

    if column in df.columns:

        report_columns.append(
            column
        )

report_columns += mark_columns

report_columns += [
    "Total",
    "Average",
    "Grade",
    "Result"
]

report = df[
    report_columns
].sort_values(
    "Rank"
)

csv_data = report.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Analysis Report",
    data=csv_data,
    file_name="student_analysis_report.csv",
    mime="text/csv"
)

# =========================================================
# FINAL MESSAGE
# =========================================================

st.success(
    "✅ Analysis completed successfully!"
)

st.caption(
    "Student Marks Analyzer • Built with Python, "
    "Pandas, Plotly and Streamlit"
)