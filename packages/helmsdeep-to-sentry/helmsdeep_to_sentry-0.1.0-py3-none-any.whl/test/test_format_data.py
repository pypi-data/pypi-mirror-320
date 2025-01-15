import unittest
import pandas as pd
from helmsdeep_to_sentry import format_data


class TestResultProcessing(unittest.TestCase):

    def test_result_to_df(self):
        # Input data
        result = {
            "data": [
                ("path/to/file1", "A549", "C001-001", "A1", 1, 1),
                ("path/to/file2", "HeLa", "C002-001", "B1", 2, 1)
            ],
            "columns": ["s3_path", 
                        "cell_type", 
                        "compound_batch_id", 
                        "well_position", 
                        "set_number", 
                        "rep_number"]
        }

        # Expected output
        expected_df = pd.DataFrame(
            result["data"],
            columns=result["columns"]
        )

        # Call the function
        result_df = format_data.result_to_df(result)

        # Assert
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_result_df_to_metadata(self):
        # Input DataFrame
        input_df = pd.DataFrame({
            "s3_path": ["path/to/file1", "path/to/file2"],
            "cell_type": ["A549", "HeLa"],
            "compound_batch_id": ["C001-001", "C002-001"],
            "well_position": ["A1", "B1"],
            "set_number": [1, 2],
            "rep_number": [1, 1]
        })

        # Expected output DataFrame
        expected_df = pd.DataFrame({
            "Data_File_Name": ["file1", "file2"],
            "Cell_Type": ["A549", "HeLa"],
            "Compound_ID": ["C001", "C002"],
            "Treatment_Well": ["A1", "B1"],
            "Compound_Set": ["SET1REP1", "SET2REP1"]
        })

        # Call the function
        final_df = format_data.result_df_to_metadata(input_df)

        # Assert
        pd.testing.assert_frame_equal(final_df, expected_df)

if __name__ == "__main__":
    unittest.main()
