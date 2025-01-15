import pandas as pd

def result_to_df(result):
    return pd.DataFrame(result["data"], columns=result["columns"])

def result_df_to_metadata(result_df: pd.DataFrame) -> pd.DataFrame:
    final_df = result_df.copy()
    final_df["s3_path"] = final_df["s3_path"].apply(lambda path: path.split("/")[-1])
    final_df["compound_batch_id"] = final_df["compound_batch_id"].apply(lambda compound: compound.split("-")[0])
    final_df["Compound_Set"] = (
        "SET" + final_df["set_number"].astype(str) + 
        "REP" + final_df["rep_number"].astype(str)
    )
    final_df = final_df.rename(columns={
        "s3_path": "Data_File_Name",
        "cell_type": "Cell_Type",
        "compound_batch_id": "Compound_ID",
        "well_position": "Treatment_Well"})
    final_df = final_df.drop(columns=["set_number", "rep_number"])
    return final_df