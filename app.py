import streamlit as st
import pandas as pd

from pathlib import Path
import re

st.title("IDs from BBM")

p = Path("data")

id_dfs = {}
for file in p.iterdir():
    if file.name.startswith("ids-"):
        match = re.match(r"^ids-(.+)\.csv$", file.name)
        if match:
            tourn = match.group(1)
            id_dfs[tourn] = pd.read_csv(file)

bbm_ranks_file = st.file_uploader("Upload your BBM rankings (must contain an 'id' column)", type="csv", accept_multiple_files=False)

contests = sorted(id_dfs.keys())
bbm_index = contests.index("BBM")

# Will add other ids here
df_merged = id_dfs["BBM"].copy()

for contest, df_contest in id_dfs.items():
    if contest == "BBM":
        continue
    df_contest = df_contest.rename({"id": f"id-{contest}"}, axis=1)
    df_merged = df_merged.merge(df_contest[["firstName", "lastName", "slotName", f"id-{contest}"]], on=["firstName", "lastName", "slotName"])

choice = st.selectbox("Select what contest you want to produce ranks for", 
                      contests, index=bbm_index)

if bbm_ranks_file:
    if choice == "BBM":
        st.write("Select one of the other contests to produce ranks.")
    else:
        df_upload = pd.read_csv(bbm_ranks_file)
        assert "id" in df_upload.columns, "'id' must be one of the columns"
        # Sort by the uploaded values
        df_sorted = df_merged.set_index(f"id", drop=True).loc[df_upload["id"]]
        output_csv = df_sorted[[f"id-{choice}", "firstName", "lastName", "slotName"]].rename(
            {f"id-{choice}": "id"}, axis=1
        ).to_csv().encode("utf-8")
        st.download_button(
            label="Download ranks",
            data=output_csv,
            file_name=f"ranks-{choice}.csv",
            mime="text/csv",
            icon=":material/download:",
        )
