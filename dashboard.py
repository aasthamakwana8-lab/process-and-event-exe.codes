import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Process Monitor", layout="wide")


st.markdown(
    "<h1 style='text-align:center; color:#4CAF50;'>🖥️ Process Monitoring Dashboard</h1>",
    unsafe_allow_html=True
)

st.markdown("---")

json_file = "output/events.json"


if os.path.exists(json_file):

    with open(json_file, "r") as f:
        lines = f.readlines()

    data = []
    for line in lines:
        line = line.strip()
        if line:
            try:
                data.append(json.loads(line))
            except:
                pass

    if len(data) == 0:
        st.warning("No data available")
        st.stop()

    df = pd.DataFrame(data)

   
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Events", len(df))

    if "action" in df.columns:
        col2.metric("Active Events", len(df[df["action"] != "stop"]))
        col3.metric("Stop Events", len(df[df["action"] == "stop"]))

    st.markdown("---")

  
    left, right = st.columns(2)

    with left:
        st.subheader("📊 Event Distribution")
        if "action" in df.columns:
            st.bar_chart(df["action"].value_counts())

    with right:
        st.subheader("⚡ Live Insights")

        if "process_name" in df.columns:
            top_process = df["process_name"].value_counts().head(5)
            st.write("Top Processes:")
            st.dataframe(top_process)

    st.markdown("---")

   
    st.subheader("📋 Process Activity Log")

    columns = ["timestamp", "process_name", "pid", "parent_pid", "action"]
    available_cols = [c for c in columns if c in df.columns]

    st.dataframe(df[available_cols], use_container_width=True)

else:
    st.error("events.json not found. Run main.py first.")