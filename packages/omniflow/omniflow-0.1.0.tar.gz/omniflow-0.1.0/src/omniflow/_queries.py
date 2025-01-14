def measurement_cid_query(database, measurement_cid):
    """
    Optimized query for All of Us database.

    :param database: Google BigQuery dataset ID containing OMOP data tables
    :return: a SQL query that can generate a table of measurement events
    """
    
    measurement_query: str = f"""
                                SELECT DISTINCT person_id
                                , measurement_concept_id
                                , src_id
                                , measurement_datetime
                                , cm.concept_name as standard_concept_name
                                , cm.concept_code as standard_concept_code
                                , cm.vocabulary_id as standard_vocabulary
                                , u.concept_name as unit_concept_name 
                                , value_as_number
                                , co.concept_name as operator_concept_name
                                , unit_concept_id                      
                                , value_as_concept_id
                                , LOWER(cv.concept_name) as value_as_concept_name
                                , operator_concept_id                                              
                                , measurement_source_concept_id
                                , LOWER(measurement_source_value) AS measurement_source_value
                                , LOWER(unit_source_value) AS unit_source_value

                                FROM `{database}.measurement` m 
                                join `{database}.measurement_ext` using (measurement_id)
                                LEFT JOIN `{database}.concept` as cm on cm.concept_id = measurement_concept_id
                                LEFT JOIN `{database}.concept` as co on co.concept_id = operator_concept_id
                                LEFT JOIN `{database}.concept` as u on u.concept_id = unit_concept_id
                                LEFT JOIN `{database}.concept` as cv on cv.concept_id = value_as_concept_id
                                
                                WHERE measurement_concept_id = {measurement_cid}
                                """

    return measurement_query