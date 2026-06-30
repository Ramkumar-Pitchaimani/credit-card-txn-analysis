# 💳 Credit Card Fraud Analytics Pipeline on Google Cloud

## Overview

The **Credit Card Fraud Analytics Pipeline** is an end-to-end cloud-native data engineering solution built on **Google Cloud Platform (GCP)** for detecting and analyzing potentially fraudulent credit card transactions.

The platform ingests transaction events, validates and enriches the data, processes transactions using Apache Beam on Google Cloud Dataflow, applies fraud detection rules, stores analytical data in BigQuery, and generates alerts for suspicious transactions.

This project demonstrates modern streaming analytics, event-driven architecture, scalable ETL pipelines, and real-time fraud detection commonly used in banking and fintech organizations.

---

# Business Problem

Banks process millions of credit card transactions every day.

Fraudulent transactions can lead to significant financial losses and damage customer trust.

The organization requires a scalable platform capable of:

- Processing transactions in real time
- Detecting suspicious activity
- Generating alerts immediately
- Maintaining historical transaction records
- Supporting fraud investigation and reporting

This project demonstrates a simplified fraud detection pipeline using Google Cloud services.

---

# Solution Architecture

```

                   Credit Card Transaction API
                               │
                               ▼
                     Google Pub/Sub Topic
                    transaction-events
                               │
                               ▼
                    Google Cloud Dataflow
          ---------------------------------------
          • Read Streaming Transactions
          • Parse JSON
          • Validate Records
          • Apply Fraud Rules
          • Detect High-Risk Transactions
          • Write Transactions to BigQuery
          • Publish Fraud Alerts
          ---------------------------------------
                    │                     │
                    ▼                     ▼
            BigQuery                Pub/Sub Topic
         transaction_fact          fraud-alerts
                                           │
                                           ▼
                                   Cloud Function
                             -----------------------
                             • Receive Alert
                             • Send Email
                             • Send SMS
                             • Log Alert
                             • Store Alert History
                             -----------------------
                                           │
                                           ▼
                                      BigQuery
                                   fraud_alerts

```

---

# Technology Stack

| Layer | Technology |
|--------|------------|
| Cloud Platform | Google Cloud Platform |
| Streaming | Google Pub/Sub |
| Data Processing | Google Cloud Dataflow |
| Processing Framework | Apache Beam |
| Compute | Cloud Functions |
| Data Warehouse | BigQuery |
| Programming Language | Python |
| Analytics | SQL / Looker Studio |

---

# Project Workflow

## Step 1 – Transaction Ingestion

Credit card transactions are published into Google Pub/Sub.

Example Transaction

```json
{
  "transaction_id":"TX10001",
  "card_number":"XXXX-XXXX-XXXX-4589",
  "merchant":"Amazon",
  "amount":9500,
  "country":"India",
  "transaction_time":"2026-07-01T10:15:00Z"
}
```

Topic

```
transaction-events
```

---

## Step 2 – Streaming Processing

Google Cloud Dataflow continuously consumes incoming transactions.

The pipeline performs:

- JSON Parsing
- Schema Validation
- Duplicate Detection
- Data Enrichment
- Fraud Rule Evaluation

---

## Step 3 – Fraud Detection Rules

Example fraud rules include:

- High transaction amount
- Multiple transactions within a short time
- International transaction immediately after a domestic transaction
- Blacklisted merchant
- Suspicious transaction frequency

Transactions matching these rules are marked as **Potential Fraud**.

---

## Step 4 – Store Transaction History

All validated transactions are stored in BigQuery.

Dataset

```
banking_dw
```

Table

```
transaction_fact
```

---

## Step 5 – Publish Fraud Alerts

When a suspicious transaction is detected, Dataflow publishes an event to Pub/Sub.

Topic

```
fraud-alerts
```

Example Alert

```json
{
  "transaction_id":"TX10001",
  "card_number":"XXXX4589",
  "fraud_reason":"High Amount",
  "risk_score":95
}
```

---

## Step 6 – Alert Processing

Cloud Function receives the fraud alert.

Responsibilities:

- Send Email Notification
- Send SMS Notification
- Log Alert
- Persist Alert History

---

## Step 7 – Store Fraud Alerts

Dataset

```
banking_dw
```

Table

```
fraud_alerts
```

This table supports fraud investigations and auditing.

---

# Dataflow Processing Logic

The streaming pipeline performs:

- Read Pub/Sub messages
- Parse JSON
- Validate schema
- Apply fraud detection rules
- Assign risk score
- Write transactions to BigQuery
- Publish fraud alerts
- Monitor processing metrics

---

# Pub/Sub Topics

| Topic | Purpose |
|--------|---------|
| transaction-events | Incoming card transactions |
| fraud-alerts | Fraud notifications |

---

# BigQuery Tables

## transaction_fact

| Column | Type |
|---------|------|
| transaction_id | STRING |
| card_number | STRING |
| merchant | STRING |
| amount | FLOAT |
| country | STRING |
| transaction_time | TIMESTAMP |
| fraud_flag | BOOLEAN |
| risk_score | INTEGER |

---

## fraud_alerts

| Column | Type |
|---------|------|
| alert_id | STRING |
| transaction_id | STRING |
| fraud_reason | STRING |
| risk_score | INTEGER |
| alert_timestamp | TIMESTAMP |

---

# Sample SQL Queries

## Top Fraudulent Merchants

```sql
SELECT
merchant,
COUNT(*) AS fraud_count
FROM banking_dw.transaction_fact
WHERE fraud_flag = TRUE
GROUP BY merchant
ORDER BY fraud_count DESC;
```

---

## Daily Fraud Trend

```sql
SELECT
DATE(transaction_time) AS transaction_date,
COUNT(*) AS fraud_transactions
FROM banking_dw.transaction_fact
WHERE fraud_flag = TRUE
GROUP BY transaction_date
ORDER BY transaction_date;
```

---

## High Risk Transactions

```sql
SELECT
transaction_id,
merchant,
amount,
risk_score
FROM banking_dw.transaction_fact
WHERE risk_score >= 90
ORDER BY amount DESC;
```

---

# Repository Structure

```
credit-card-fraud-analytics-pipeline/

│
├── dataflow/
│      fraud_detection_pipeline.py
│
├── cloud-function/
│      fraud_alert_function.py
│
├── pubsub/
│      transaction_publisher.py
│
├── sql/
│      create_tables.sql
│
├── architecture/
│      architecture.png
│
├── deployment/
│      deployment-guide.png
│
├── screenshots/
│
├── sample_data/
│
├── README.md
```

---

# Features

- Real-Time Transaction Processing
- Event-Driven Architecture
- Fraud Rule Engine
- Streaming Analytics
- Google Pub/Sub Integration
- Apache Beam Processing
- Cloud Functions Alerting
- BigQuery Analytics
- Historical Fraud Reporting
- Enterprise Data Pipeline Design

---

# Skills 

- Google Cloud Platform
- Pub/Sub
- Dataflow
- Apache Beam
- Cloud Functions
- BigQuery
- Python
- Streaming ETL
- Fraud Detection Pipeline
- Event-Driven Architecture
- Real-Time Analytics

---
