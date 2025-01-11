from pyspark.context import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql import functions as F
from nextdata.core.glue.connections.dsql import DSQLGlueJobArgs, generate_dsql_password
from nextdata.core.glue.glue_entrypoint import glue_job, GlueJobArgs
from nextdata.core.glue.connections.jdbc import JDBCGlueJobArgs


@glue_job(job_args_type=GlueJobArgs)
def main(spark: SparkContext, job_args: GlueJobArgs):
    # Read source data into a Spark DataFrame
    if job_args.sql_query:
        base_query = job_args.sql_query
    else:
        base_query = f"SELECT * FROM {job_args.sql_table}"
    connection_conf = None
    password = None
    if job_args.connection_type == "dsql":
        connection_conf = DSQLGlueJobArgs(**job_args.connection_properties)
        password = generate_dsql_password(connection_conf.host)
    elif job_args.connection_type == "jdbc":
        connection_conf = JDBCGlueJobArgs(**job_args.connection_properties)
        password = connection_conf.password
    else:
        raise ValueError(f"Unsupported connection type: {job_args.connection_type}")
    sql_context = SQLContext(spark)
    source_df = (
        sql_context.read.format("jdbc")
        .options(
            url=f"jdbc:{connection_conf.protocol}://{connection_conf.host}:{connection_conf.port}/{connection_conf.database}",
            query=base_query,
            user=connection_conf.username,
            password=password,
        )
        .load()
    )

    # Register the DataFrame as a temp view to use with Spark SQL
    source_df = source_df.withColumn("ds", F.current_date())
    source_df.createOrReplaceTempView("source_data")

    # Get the schema from the source DataFrame
    schema_columns = ", ".join(
        [
            f"{field.name} {field.dataType.simpleString()}"
            for field in source_df.schema.fields
        ]
        + ["ds timestamp"]
    )

    # Create the Iceberg table if it doesn't exist
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {job_args.output_s3_path} (
        {schema_columns}
    )
    USING iceberg
    """
    spark.sql(create_table_sql)

    # Insert or merge data based on incremental settings
    if not job_args.is_full_load and job_args.incremental_column:
        # Merge for incremental updates
        merge_sql = f"""
        MERGE INTO {job_args.output_s3_path} target
        USING source_data source
        ON source.{job_args.incremental_column} = target.{job_args.incremental_column}
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
        """
        spark.sql(merge_sql)
    else:
        # Full load - overwrite the table
        insert_sql = f"""
        INSERT OVERWRITE INTO {job_args.output_s3_path}
        SELECT * FROM source_data
        """
        spark.sql(insert_sql)


if __name__ == "__main__":
    main()
