import unittest
from unittest.mock import patch, MagicMock
from helmsdeep_to_sentry import query_helmsdeep

class TestGetLocalSession(unittest.TestCase):
    @patch("helmsdeep_to_sentry.query_helmsdeep.create_engine")
    @patch("helmsdeep_to_sentry.query_helmsdeep.sessionmaker")

    def test_get_local_session(self, mock_sessionmaker, mock_create_engine):
        # Mocking the engine and session
        mock_engine = MagicMock()
        mock_sessionmaker.return_value = MagicMock()
        mock_create_engine.return_value = mock_engine

        # Call the function
        url = "sqlite:///:memory:"  
        session = query_helmsdeep.get_local_session(url)

        # Assertions
        mock_create_engine.assert_called_once_with(
            url, connect_args={"ssl_ca": "/etc/ssl/cert.pem"}
        )
        mock_sessionmaker.assert_called_once_with(bind=mock_engine)
        self.assertIsNotNone(session)  # Ensure the session is created

class TestQueryDatabase(unittest.TestCase):
    def test_query_database_success(self):
        # Mocking the session and result
        mock_session = MagicMock()
        mock_execute = mock_session.__enter__.return_value.execute
        mock_execute.return_value.fetchall.return_value = [("row1",), ("row2",)]

        sql_query = "SELECT * FROM table"
        result = query_helmsdeep.query_database(mock_session, sql_query)

        # Assertions
        mock_execute.assert_called_once()
        self.assertEqual(result["data"], [("row1",), ("row2",)])
    
    def test_query_database_no_results(self):
        # Mocking the session and result
        mock_session = MagicMock()
        mock_execute = mock_session.__enter__.return_value.execute
        mock_execute.return_value.fetchall.return_value = []

        sql_query = "SELECT * FROM table"
        result = query_helmsdeep.query_database(mock_session, sql_query)

        # Assertions
        mock_execute.assert_called_once()
        self.assertEqual(result["data"], [])

    def test_query_database_exception(self):
        # Mocking the session and exception
        mock_session = MagicMock()
        mock_execute = mock_session.__enter__.return_value.execute
        mock_execute.side_effect = Exception("Database error")

        sql_query = "SELECT * FROM table"
        result = query_helmsdeep.query_database(mock_session, sql_query)

        # Assertions
        mock_execute.assert_called_once()
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()