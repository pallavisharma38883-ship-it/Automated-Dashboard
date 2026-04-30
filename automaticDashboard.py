import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("📊 Automatic Dashboard Generator")

# ---------------- UPLOAD FILE ----------------
file = st.file_uploader("Upload Excel or CSV file", type=["csv", "xlsx"])

if file is not None:

    # ---------------- READ DATA ----------------
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    st.write("### Data Preview")
    st.dataframe(df)

    # ---------------- COLUMN DETECTION ----------------
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    # ---------------- SIDEBAR FILTERS ----------------
    st.sidebar.header("🔍 Filters")

    used_cols = []

    if len(categorical_cols) > 0:
        cat_col = st.sidebar.selectbox("📍 Category Column", categorical_cols)

        selected_cat = st.sidebar.multiselect(
            "Filter Category",
            df[cat_col].unique(),
            default=df[cat_col].unique()
        )

        df = df[df[cat_col].isin(selected_cat)]
        used_cols.append(cat_col)

    if len(categorical_cols) > 0:
        remaining = [c for c in categorical_cols if c not in used_cols]

        if len(remaining) > 0:
            cust_col = st.sidebar.selectbox("👤 Customer Column", remaining)

            selected_cust = st.sidebar.multiselect(
                "Filter Customer",
                df[cust_col].unique(),
                default=df[cust_col].unique()
            )

            df = df[df[cust_col].isin(selected_cust)]

    if len(numeric_cols) > 0:
        num_col = st.sidebar.selectbox("💰 Numeric Column", numeric_cols)

        min_val = float(df[num_col].min())
        max_val = float(df[num_col].max())

        range_val = st.sidebar.slider(
            "Range",
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val)
        )

        df = df[(df[num_col] >= range_val[0]) & (df[num_col] <= range_val[1])]

    # ---------------- TABS ----------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📊 KPIs", "📈 Charts", "🥧 Pie Chart", "📥 Download", "📋 Data Table"]
    )

    # ---------------- KPIs ----------------
    with tab1:
        st.write("## 📊 Key Metrics")
        if len(numeric_cols) > 0:
            cols = st.columns(len(numeric_cols))
            for i, col in enumerate(numeric_cols):
                with cols[i]:
                    st.metric(f"Total {col}", df[col].sum())

    # ---------------- CHARTS ----------------
    with tab2:

        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            st.write("## 📊 Bar Chart")
            data = df.groupby(categorical_cols[0])[numeric_cols[0]].sum()
            fig, ax = plt.subplots()
            data.plot(kind='bar', ax=ax)
            st.pyplot(fig)

        if len(numeric_cols) > 0:
            st.write("## 📈 Line Chart")
            fig, ax = plt.subplots()
            df[numeric_cols].plot(ax=ax)
            st.pyplot(fig)

        if len(numeric_cols) > 0:
            st.write("## 📊 Histogram")
            fig, ax = plt.subplots()
            df[numeric_cols[0]].plot(kind='hist', bins=20, ax=ax)
            st.pyplot(fig)

    # ---------------- PIE ----------------
    with tab3:
        if len(categorical_cols) > 0:
            st.write("## 🥧 Pie Chart")
            pie_data = df[categorical_cols[0]].value_counts()
            fig, ax = plt.subplots()
            ax.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%')
            st.pyplot(fig)

    # ---------------- DOWNLOAD ----------------
    with tab4:
        csv = df.to_csv(index=False)
        st.download_button("⬇ Download CSV", data=csv, file_name="filtered_data.csv")

    # ---------------- DATA TABLE ----------------
    with tab5:
        St. Write ("##  Dynamic Data Table")
        search = st.text_input("Search")

        if search:
            df_filtered = df[df.astype(str).apply(
                lambda row: row.str.contains(search, case=False).any(), axis=1)]
        else:
            df_filtered = df.copy()

        sort_col = st.selectbox("Sort by", df_filtered.columns)
        order = st.radio("Order", ["Ascending", "Descending"])

        df_filtered = df_filtered.sort_values(
            by=sort_col,
            ascending=(order == "Ascending")
        )

        st.dataframe(df_filtered, use_container_width=True)
