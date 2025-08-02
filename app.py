import streamlit as st
import pandas as pd

# ===== PAGE CONFIG =====
st.set_page_config(page_title="NRFI/YRFI Model", layout="wide")

# Hide Streamlit menu and footer
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Back to Homepage button
st.markdown(
    """
    <a href="https://lineupwire.com" target="_self">
        <button style="
            background-color: black;
            color: white;
            padding: 8px 16px;
            border-radius: 8px;
            border: none;
            font-size: 16px;
            cursor: pointer;
        ">Back to Homepage</button>
    </a>
    """,
    unsafe_allow_html=True
)

st.title("🔴🟢 NRFI/YRFI Model")

# ===== LOAD DATA (replace with your Google Sheet or data source) =====
try:
    df = pd.read_csv("nrfi_model.csv")

    # Format confidence as whole numbers
    df["Confidence %"] = df["Confidence %"].astype(int)

    # Sort by confidence descending
    df = df.sort_values("Confidence %", ascending=False)

    # Create NRFI/YRFI color cells
    def color_cell(row):
        color = "red" if row["NRFI/YRFI"] == "NRFI" else "green"
        return f'<td style="background-color:{color};color:black">{row["NRFI/YRFI"]}</td>'

    # Build HTML manually to color NRFI/YRFI cell
    html = "<table class='styled-table'>"
    # Header
    html += "<tr>" + "".join([f"<th>{col}</th>" for col in df.columns]) + "</tr>"
    # Rows
    for _, row in df.iterrows():
        html += "<tr>"
        for col in df.columns:
            if col == "NRFI/YRFI":
                color = "red" if row[col] == "NRFI" else "green"
                html += f'<td style="background-color:{color};color:black">{row[col]}</td>'
            else:
                html += f"<td>{row[col]}</td>"
        html += "</tr>"
    html += "</table>"

    # Add table styling with rounded red/blue border
    st.markdown(
        """
        <style>
        .styled-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 16px;
            text-align: center;
            border: 2px solid blue;
            border-radius: 10px;
            overflow: hidden;
        }
        .styled-table th, .styled-table td {
            border: 1px solid red;
            padding: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(html, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error loading NRFI/YRFI Model: {e}")
