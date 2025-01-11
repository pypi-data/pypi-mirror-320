# Query responses
EXPECTED_ADD_CONNECTION_RESPONSE_FIELD = "addConnection"
EXPECTED_GENERIC_DB_GQL_RESPONSE_FIELD = "testDatabaseCredentials"
EXPECTED_HIVE_S3_GQL_RESPONSE_FIELD = "testS3Credentials"
EXPECTED_HIVE_SQL_GQL_RESPONSE_FIELD = "testHiveCredentials"
EXPECTED_PRESTO_SQL_GQL_RESPONSE_FIELD = "testPrestoCredentials"
EXPECTED_PRESTO_S3_GQL_RESPONSE_FIELD = "testS3Credentials"
EXPECTED_GLUE_GQL_RESPONSE_FIELD = "testGlueCredentials"
EXPECTED_ATHENA_GQL_RESPONSE_FIELD = "testAthenaCredentials"
EXPECTED_SPARK_GQL_RESPONSE_FIELD = "testSparkCredentials"
EXPECTED_DATABRICKS_GQL_RESPONSE_FIELD = "testDatabricksCredentials"
EXPECTED_SNOWFLAKE_GQL_RESPONSE_FIELD = "testSnowflakeCredentials"
EXPECTED_BQ_GQL_RESPONSE_FIELD = "testBqCredentials"
EXPECTED_SELF_HOSTED_GQL_RESPONSE_FIELD = "testSelfHostedCredentials"
EXPECTED_CONFIGURE_METADATA_EVENTS_GQL_RESPONSE_FIELD = "configureMetadataEvents"
EXPECTED_CONFIGURE_QUERY_LOG_EVENTS_GQL_RESPONSE_FIELD = "configureQueryLogEvents"
EXPECTED_DISABLE_METADATA_EVENTS_GQL_RESPONSE_FIELD = "disableMetadataEvents"
EXPECTED_DISABLE_QUERY_LOG_EVENTS_GQL_RESPONSE_FIELD = "disableQueryLogEvents"
EXPECTED_UPDATE_CREDENTIALS_RESPONSE_FIELD = "updateCredentials"
EXPECTED_REMOVE_CONNECTION_RESPONSE_FIELD = "removeConnection"
EXPECTED_TEST_EXISTING_RESPONSE_FIELD = "testExistingConnection"
EXPECTED_TEST_TABLEAU_RESPONSE_FIELD = "testTableauCredentials"
EXPECTED_TEST_AIRFLOW_RESPONSE_FIELD = "testAirflowCredentialsV2"
EXPECTED_LOOKER_METADATA_RESPONSE_FIELD = "testLookerCredentials"
EXPECTED_LOOKER_GIT_SSH_RESPONSE_FILED = "testLookerGitSshCredentials"
EXPECTED_LOOKER_GIT_CLONE_RESPONSE_FIELD = "testLookerGitCloneCredentials"
EXPECTED_POWER_BI_RESPONSE_FIELD = "testPowerBiCredentials"
EXPECTED_DBT_CLOUD_RESPONSE_FIELD = "testDbtCloudCredentials"
EXPECTED_ADD_BI_RESPONSE_FIELD = "addBiConnection"
EXPECTED_FIVETRAN_RESPONSE_FIELD = "testFivetranCredentials"
EXPECTED_INFORMATICA_RESPONSE_FIELD = "testInformaticaCredentials"
EXPECTED_AZURE_DATA_FACTORY_RESPONSE_FIELD = "testAzureDataFactoryCredentials"
EXPECTED_DATABRICKS_SQL_WAREHOUSE_GQL_RESPONSE_FIELD = "testDatabricksSqlWarehouseCredentials"
EXPECTED_ADD_ETL_CONNECTION_RESPONSE_FIELD = "addEtlConnection"
EXPECTED_ADD_STREAMING_SYSTEM_RESPONSE_FIELD = "addStreamingSystem"
EXPECTED_ADD_CONFLUENT_CLUSTER_CONNECTION_RESPONSE_FIELD = "addStreamingConnection"
EXPECTED_GET_STREAMING_SYSTEMS_RESPONSE_FIELD = "getStreamingSystems"
EXPECTED_TEST_CONFLUENT_KAFKA_CRED_RESPONSE_FIELD = "testConfluentKafkaCredentials"
EXPECTED_TEST_CONFLUENT_KAFKA_CONNECT_CRED_RESPONSE_FIELD = "testConfluentKafkaConnectCredentials"
EXPECTED_TEST_MSK_KAFKA_CRED_RESPONSE_FIELD = "testMskKafkaCredentials"
EXPECTED_TEST_MSK_KAFKA_CONNECT_CRED_RESPONSE_FIELD = "testMskKafkaConnectCredentials"
EXPECTED_TEST_SELF_HOSTED_KAFKA_CRED_RESPONSE_FIELD = "testSelfHostedKafkaCredentials"
EXPECTED_TEST_SELF_HOSTED_KAFKA_CONNECT_CRED_RESPONSE_FIELD = (
    "testSelfHostedKafkaConnectCredentials"
)
EXPECTED_TEST_PINECONE_CREDENTIALS_RESPONSE_FIELD = "testPineconeCredentials"
EXPECTED_TEST_TRANSACTIONAL_DB_CREDENTIALS_RESPONSE_FIELD = "testTransactionalDbCredentials"
EXPECTED_TEST_INFORMATICA_CREDENTIALS_RESPONSE_FIELD = "testInformaticaCredentials"
EXPECTED_TEST_AZURE_DATA_FACTORY_RESPONSE_FIELD = "testAzureDataFactoryCredentials"

# Available connections types
ATHENA_CONNECTION_TYPE = "athena"
BQ_CONNECTION_TYPE = "bigquery"
DATABRICKS_DELTA_CONNECTION_TYPE = "databricks-delta"
DATABRICKS_METASTORE_CONNECTION_TYPE = "databricks-metastore"
DATABRICKS_SQL_WAREHOUSE_CONNECTION_TYPE = "databricks-sql-warehouse"
DATABRICKS_METASTORE_SQL_WAREHOUSE_CONNECTION_TYPE = "databricks-metastore-sql-warehouse"
DBT_CLOUD_WEBHOOK_CONNECTION_TYPE = "dbt-cloud-webhook"
DBT_CORE_CONNECTION_TYPE = "dbt-core"
FIVETRAN_CONNECTION_TYPE = "fivetran"
GLUE_CONNECTION_TYPE = "glue"
HIVE_MYSQL_CONNECTION_TYPE = "hive-mysql"
HIVE_S3_CONNECTION_TYPE = "hive-s3"
HIVE_SQL_CONNECTION_TYPE = "hive"
INFORMATICA_CONNECTION_TYPE = "informatica"
LOOKER_GIT_CLONE_CONNECTION_TYPE = "looker-git-clone"
LOOKER_GIT_SSH_CONNECTION_TYPE = "looker-git-ssh"
LOOKER_MD_CONNECTION_TYPE = "looker"
POWER_BI_CONNECTION_TYPE = "power-bi"
PRESTO_S3_CONNECTION_TYPE = "presto-s3"
PRESTO_SQL_CONNECTION_TYPE = "presto"
REDSHIFT_CONNECTION_TYPE = "redshift"
SNOWFLAKE_CONNECTION_TYPE = "snowflake"
SPARK_CONNECTION_TYPE = "spark"
TABLEAU_CONNECTION_TYPE = "tableau"
TRANSACTIONAL_CONNECTION_TYPE = "transactional-db"
AIRFLOW_CONNECTION_TYPE = "airflow"
CONFLUENT_KAFKA_CONNECTION_TYPE = "confluent-kafka"
CONFLUENT_KAFKA_CONNECT_CONNECTION_TYPE = "confluent-kafka-connect"
MSK_KAFKA_CONNECTION_TYPE = "msk-kafka"
MSK_KAFKA_CONNECT_CONNECTION_TYPE = "msk-kafka-connect"
SELF_HOSTED_KAFKA_CONNECTION_TYPE = "self-hosted-kafka"
SELF_HOSTED_KAFKA_CONNECT_CONNECTION_TYPE = "self-hosted-kafka-connect"
AZURE_DATA_FACTORY_CONNECTION_TYPE = "azure-data-factory"
PINECONE_CONNECTION_TYPE = "pinecone"

# Available transactional-db framework connection types
POSTGRES_DB_TYPE = "postgres"
SQL_SERVER_DB_TYPE = "sql-server"
MYSQL_DB_TYPE = "mysql"
ORACLE_DB_TYPE = "oracle"
MARIADB_DB_TYPE = "mariadb"
TERADATA_DB_TYPE = "teradata"
AZURE_DEDICATED_SQL_POOL_TYPE = "azure-dedicated-sql-pool"
AZURE_SQL_DATABASE_TYPE = "azure-sql-database"
SAP_HANA_DATABASE_TYPE = "sap-hana"
MOTHERDUCK_DATABASE_TYPE = "motherduck"
DREMIO_DATABASE_TYPE = "dremio"

METASTORE_CONNECTION_TYPES = (
    HIVE_MYSQL_CONNECTION_TYPE,
    GLUE_CONNECTION_TYPE,
    DATABRICKS_METASTORE_CONNECTION_TYPE,
    DATABRICKS_METASTORE_SQL_WAREHOUSE_CONNECTION_TYPE,
)

# Every warehouse must have one and only one of these.
MAIN_CONNECTION_TYPES = frozenset(
    [
        BQ_CONNECTION_TYPE,
        REDSHIFT_CONNECTION_TYPE,
        SNOWFLAKE_CONNECTION_TYPE,
        *METASTORE_CONNECTION_TYPES,
    ]
)

# Available warehouse types
DATA_LAKE_WAREHOUSE_TYPE = "data-lake"
REDSHIFT_WAREHOUSE_TYPE = REDSHIFT_CONNECTION_TYPE
SNOWFLAKE_WAREHOUSE_TYPE = SNOWFLAKE_CONNECTION_TYPE
BQ_WAREHOUSE_TYPE = BQ_CONNECTION_TYPE
TRANSACTIONAL_WAREHOUSE_TYPE = TRANSACTIONAL_CONNECTION_TYPE
AIRFLOW_WAREHOUSE_TYPE = "etl"
PINECONE_WAREHOUSE_TYPE = PINECONE_CONNECTION_TYPE

CONNECTION_TO_WAREHOUSE_TYPE_MAP = {
    BQ_CONNECTION_TYPE: BQ_WAREHOUSE_TYPE,
    REDSHIFT_CONNECTION_TYPE: REDSHIFT_WAREHOUSE_TYPE,
    SNOWFLAKE_CONNECTION_TYPE: SNOWFLAKE_WAREHOUSE_TYPE,
}

# Available BI types
LOOKER_BI_TYPE = "looker"
TABLEAU_BI_TYPE = "tableau"
POWER_BI_BI_TYPE = "power-bi"

# Available Streaming cluster types
CONFLUENT_KAFKA_CLUSTER_TYPE = "confluent-kafka"
CONFLUENT_KAFKA_CONNECT_CLUSTER_TYPE = "confluent-kafka-connect"
MSK_KAFKA_CLUSTER_TYPE = "msk-kafka"
MSK_KAFKA_CONNECT_CLUSTER_TYPE = "msk-kafka-connect"
SELF_HOSTED_KAFKA_CLUSTER_TYPE = "self-hosted-kafka"
SELF_HOSTED_KAFKA_CONNECT_CLUSTER_TYPE = "self-hosted-kafka-connect"


# Available credential self-hosting mechanisms
SECRETS_MANAGER_CREDENTIAL_MECHANISM = "secretsmanager"
SELF_HOSTING_MECHANISMS = [SECRETS_MANAGER_CREDENTIAL_MECHANISM]

# S3 event types
S3_METADATA_EVENT_TYPE = "s3_metadata_events"
S3_QL_EVENT_TYPE = "s3_ql_events"

# Job types
QL_JOB_TYPE = ["query_logs"]

# Job limits
PRESTO_CATALOG_KEY = "catalog_name"
HIVE_GET_PARTS_KEY = "get_partition_locations"
HIVE_MAX_PARTS_KEY = "max_partition_locations"
HIVE_MAX_PARTS_DEFAULT_VALUE = 50

# Certificate details
S3_CERT_MECHANISM = "dc-s3"
PRESTO_CERT_PREFIX = "certificates/presto/"
AWS_RDS_CA_CERT = "https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem"

# Connections to friendly name (i.e. human presentable) map
GQL_TO_FRIENDLY_CONNECTION_MAP = {
    ATHENA_CONNECTION_TYPE: "Athena",
    BQ_CONNECTION_TYPE: "BigQuery",
    DATABRICKS_DELTA_CONNECTION_TYPE: "Databricks (Delta lake)",
    DATABRICKS_METASTORE_CONNECTION_TYPE: "Databricks (metastore)",
    DATABRICKS_METASTORE_SQL_WAREHOUSE_CONNECTION_TYPE: "Databricks Metastore Sql Warehouse",
    DBT_CLOUD_WEBHOOK_CONNECTION_TYPE: "dbt Cloud (webhook)",
    DBT_CORE_CONNECTION_TYPE: "dbt Core",
    FIVETRAN_CONNECTION_TYPE: "Fivetran",
    GLUE_CONNECTION_TYPE: GLUE_CONNECTION_TYPE.capitalize(),
    HIVE_MYSQL_CONNECTION_TYPE: "Hive (metastore)",
    HIVE_S3_CONNECTION_TYPE: "Hive (EMR logs)",
    HIVE_SQL_CONNECTION_TYPE: "Hive (SQL)",
    LOOKER_GIT_CLONE_CONNECTION_TYPE: "Looker ML (git)",
    LOOKER_GIT_SSH_CONNECTION_TYPE: "Looker ML (git)",
    LOOKER_MD_CONNECTION_TYPE: "Looker (metadata)",
    POWER_BI_CONNECTION_TYPE: "Power BI",
    PRESTO_S3_CONNECTION_TYPE: "Presto (logs)",
    PRESTO_SQL_CONNECTION_TYPE: PRESTO_SQL_CONNECTION_TYPE.capitalize(),
    REDSHIFT_CONNECTION_TYPE: REDSHIFT_CONNECTION_TYPE.capitalize(),
    SNOWFLAKE_CONNECTION_TYPE: SNOWFLAKE_CONNECTION_TYPE.capitalize(),
    SPARK_CONNECTION_TYPE: "Spark (SQL)",
    TABLEAU_CONNECTION_TYPE: "Tableau",
    TRANSACTIONAL_CONNECTION_TYPE: "Transactional Database",
}

# Verbiage
CONNECTION_TEST_SUCCESS_VERBIAGE = "Connection test was successful!"
CONNECTION_TEST_FAILED_VERBIAGE = "Connection test failed!"
ADD_CONNECTION_SUCCESS_VERBIAGE = "Success! Added connection for "
ADD_CONNECTION_FAILED_VERBIAGE = "Failed to add connection!"
VALIDATIONS_FAILED_VERBIAGE = (
    "Some validations failed. Would you like to create the connection anyway?"
)
OPERATION_ERROR_VERBIAGE = (
    "Operation failed - This might not be a valid connection for your account. "
    "Please contact Monte Carlo."
)
CONFIRM_CONNECTION_VERBIAGE = "Please confirm you want to add this connection"
SKIP_ADD_CONNECTION_VERBIAGE = "Skipping adding the connection."
