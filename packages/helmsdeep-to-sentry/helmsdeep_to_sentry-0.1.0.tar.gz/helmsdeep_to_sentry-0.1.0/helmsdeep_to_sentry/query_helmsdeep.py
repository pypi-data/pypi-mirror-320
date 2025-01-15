import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from typing import Union

def get_database_url(dotenv_path: Union[str, os.PathLike]=None) -> str:
    load_dotenv(dotenv_path=dotenv_path)
    database_url = (
    f"mysql+mysqlconnector://{os.getenv('DATABASE_USERNAME')}:"
    f"{os.getenv('DATABASE_PASSWORD')}@"
    f"{os.getenv('DATABASE_HOST')}/{os.getenv('DATABASE')}"
    )
    return database_url

def get_local_session(url: str) -> Session:
    """Get a local session to interact with the database."""
    ssl_args = {"ssl_ca": "/etc/ssl/cert.pem"}
    engine = create_engine(url, connect_args=ssl_args)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def query_database(local_session: Session, sql_query: str) -> dict:
    with local_session as session:
        try:
            result_proxy = session.execute(text(sql_query))
            result = result_proxy.fetchall()
            column_names = list(result_proxy.keys())
            return {"columns": column_names, "data": result}
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

def get_experiment_query_str(experiment_name: str) -> str:
    return f'''SELECT 
        ms_run.s3_path, 
        ms_run.well_position, 
        cell_culture_registry.cell_type, 
        compound_stock_registry.compound_batch_id, 
        wellplate.set_number,  
        wellplate.rep_number  
    FROM 
        cell_culture_registry
    INNER JOIN 
        cell_culture_active_properties
        ON cell_culture_registry.id = 
            cell_culture_active_properties.id
    INNER JOIN 
        compound_stock_registry
        ON cell_culture_active_properties.treatment_compound_stock_id = 
            compound_stock_registry.id
    JOIN 
        cell_fraction
        ON cell_culture_registry.id = 
            cell_fraction.parent_culture
    JOIN 
        peptide_digest
        ON cell_fraction.id = 
            peptide_digest.parent_fraction_id
    JOIN 
        ms_run
        ON peptide_digest.id = 
            peptide_digest_id-1
    JOIN 
        experiment
        ON ms_run.experiment_id = 
            experiment.id
    JOIN 
        wellplate  
        ON ms_run.wellplate_id = 
            wellplate.id 
    WHERE 
        experiment.name = "{experiment_name}";
    '''