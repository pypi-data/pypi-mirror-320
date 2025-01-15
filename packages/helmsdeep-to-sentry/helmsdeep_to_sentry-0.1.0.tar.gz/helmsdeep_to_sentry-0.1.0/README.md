# HelmsdeepToSentry
The purpose of this package is to query helmsdeep for the relevant metadata and format it to be put into sentry.

## Credentials
You must have a ```.env``` file with your helmsdeep credentials in the working 
directory or provide the .env path to the ```get_database_url``` function.

## Usage
```
from helmsdeep_to_sentry import *

# Set up the connection to helmsdeep
url = get_database_url(dotenv_path="path/to/.env") # or omit kwarg
session = get_local_session(url)

# Create a query for the experiment of interest
query_str = get_experiment_query_str("Screen Frodo") # or manually write query

# Query helmsdeep
result = query_database(session, query_str)

# Format the metadata for Sentry
result_df = result_to_df(result)
sentry_metadata = result_df_to_metadata(result_df)
```