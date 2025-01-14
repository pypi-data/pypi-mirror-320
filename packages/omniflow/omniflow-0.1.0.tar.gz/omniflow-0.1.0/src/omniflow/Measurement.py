import os
import polars as pl
import sys
from omniflow import _queries, _utils


class Measurement:
    """
    Class Measurement.
    Supports measurement extraction for any measurement_concept_id for data structured in the OMOP CDM.
    """

    def __init__(self, database="aou", measurement_cid=None):
        """
        Instantiate based on parameter database
        :param database: supports:
            "aou": All of Us OMOP database
        :param measurement_id: OMOP measurement_id provided as an integer
        """
        self.database = database

        if database == "aou":
            self.cdr = os.getenv("WORKSPACE_CDR")
            self.measurement_query = _queries.measurement_cid_query(self.cdr, measurement_cid)
            print("\033[1mStart querying measurement...")
            self.measurement_events = _utils.polars_gbq(self.measurement_query)
            
        else:
            print("Invalid database. Parameter database only accepts \"aou\" (All of Us) or \"custom\".")
            sys.exit(0)

        print("\033[1mDone!")
        
    def query_summary(self):
        grouped = (
            self.measurement_events
            .group_by(["standard_concept_name", "measurement_concept_id"])
            .agg([
                pl.col("value_as_number").count().alias("measurement_count"),
                pl.col("person_id").n_unique().alias("participant_count"),
                pl.col("src_id").n_unique().alias("site_count"),
                pl.col("unit_concept_name").n_unique().alias("unit_count")
            ])
        )
        return grouped