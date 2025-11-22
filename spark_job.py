import sys
import glob
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col, when, lit, to_timestamp, concat, round as spark_round
)

# -----------------------------------------------------------------------------
# Processing Logic
# -----------------------------------------------------------------------------
def process_transactions(
    trans_df: DataFrame,
    cardholders_df: DataFrame,
    time_format: str = "HH:mm:ss"
) -> DataFrame:

    df = trans_df.filter(
        (col("transaction_amount") > 0) &
        (col("transaction_status").isin("SUCCESS", "FAILED", "PENDING")) &
        col("cardholder_id").isNotNull() &
        col("merchant_id").isNotNull()
    )

    df = (
        df.withColumn(
            "transaction_category",
            when(col("transaction_amount") <= 100, lit("Low"))
            .when((col("transaction_amount") > 100) & (col("transaction_amount") <= 500), lit("Medium"))
            .otherwise(lit("High"))
        )
        .withColumn("transaction_timestamp", to_timestamp(col("transaction_timestamp")))
        .withColumn(
            "high_risk",
            (col("fraud_flag") == True) |
            (col("transaction_amount") > 10000) |
            (col("transaction_category") == "High")
        )
        .withColumn(
            "merchant_info",
            concat(col("merchant_name"), lit(" - "), col("merchant_location"))
        )
    )

    df = df.join(cardholders_df, on="cardholder_id", how="left")

    df = df.withColumn(
        "updated_reward_points",
        col("reward_points") + spark_round(col("transaction_amount") / 10)
    )

    df = df.withColumn(
        "fraud_risk_level",
        when(col("high_risk"), lit("Critical"))
        .when((col("risk_score") > 0.3) | (col("fraud_flag")), lit("High"))
        .otherwise(lit("Low"))
    )

    return df


# -----------------------------------------------------------------------------
# Main Entrypoint
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    spark = SparkSession.builder \
        .appName("Advanced Credit Card Transactions Processor") \
        .getOrCreate()

    # -------------------------
    # 1. INPUT PATH HANDLING
    # -------------------------
    # Airflow passes entire folder path now
    input_folder = sys.argv[1] if len(sys.argv) > 1 else "gs://credit-card-data-analysis-dir/transactions/"

    # Convert to wildcard path for reading
    json_path = input_folder.rstrip("/") + "/*.json"

    print(f"[INFO] Reading JSON files from: {json_path}")

    # -------------------------
    # 2. Load BigQuery Lookup Table
    # -------------------------
    BQ_PROJECT = "p101-473210"
    BQ_DATASET = "credit_card"
    BQ_CARDHOLDERS_TABLE = f"{BQ_PROJECT}.{BQ_DATASET}.cardholders_tb"
    BQ_TRANSACTIONS_TABLE = f"{BQ_PROJECT}.{BQ_DATASET}.transactions"

    cardholders_df = spark.read.format("bigquery") \
        .option("table", BQ_CARDHOLDERS_TABLE) \
        .load()

    # -------------------------
    # 3. Load JSON files with schema inference protection
    # -------------------------
    try:
        transactions_df = spark.read.option("multiline", "true").json(json_path)
    except Exception as e:
        print("[ERROR] Failed to load JSON — likely no files in folder")
        raise

    print(f"[INFO] Loaded {transactions_df.count()} transaction records")

    # -------------------------
    # 4. Process Transformation
    # -------------------------
    enriched_df = process_transactions(transactions_df, cardholders_df)

    # -------------------------
    # 5. Write Back to BigQuery
    # -------------------------
    enriched_df.write.format("bigquery") \
        .option("table", BQ_TRANSACTIONS_TABLE) \
        .option("temporaryGcsBucket", "bq-temp-p101-473210") \
        .option("createDisposition", "CREATE_IF_NEEDED") \
        .option("writeDisposition", "WRITE_APPEND") \
        .save()

    print("Advanced Transactions Processing Completed Successfully!")
    spark.stop()
