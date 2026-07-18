# Deployment & Installation Guide

This guide provides a comprehensive, step-by-step walkthrough to deploy and execute the NYC Taxi Medallion Data Pipeline from scratch.

---

## Prerequisite Software

Ensure you have the following installed locally if you wish to run queries manually:

* Git
* Databricks CLI (`pip install databricks-cli`)
* Python 3.10 or higher

---

## Step 1: AWS S3 & IAM Infrastructure Setup

### 1.1. S3 Bucket Architecture

1. Log into your **AWS Management Console**.
2. Navigate to **Amazon S3** and click **Create bucket**.
3. Name your bucket (e.g., `awae-yellow-taxi-case`) and select your preferred region (e.g., `us-east-1`).
4. Under **Block Public Access settings**, ensure **Block *all* public access** is checked.
5. Click **Create bucket**.
6. Open your new bucket, click **Create folder**, and establish the exact directory structure below:
* `landing/`
* `bronze`
* `silver/`
* `gold/`

### 1.2. IAM Security User & Permissions Policy

1. Navigate to the **IAM Console** on AWS.
2. In the left menu, click **Users** > **Create user**.
3. Name the user `databricks-streamlit-s3-user` and advance without granting console management access.
4. In the permissions step, select **Attach policies directly** and click **Create policy**.
5. Switch to the **JSON** tab, clear the text editor, and paste the following code:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["s3:ListBucket"],
            "Resource": ["arn:aws:s3:::awae-yellow-taxi-case"]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": ["arn:aws:s3:::awae-yellow-taxi-case/*"]
        }
    ]
}

```

6. Click **Next**, name the policy `S3-Access-iFood-Case`, and click **Create policy**.
7. Return to the user creation wizard, attach the `S3-Access-iFood-Case` policy, and complete the creation.
8. Open the newly created user profile, navigate to the **Security credentials** tab, scroll to **Access keys**, and click **Create access key** (select *Application running outside AWS*).
9. Copy and save both the **Access key ID** and **Secret access key** safely.

---

## Step 2: Databricks Environment Configuration

### 2.1. Git Integration

1. Log into your **Databricks Workspace**.
2. Click your profile email on the bottom-left corner and go to **User Settings**.
3. Access the **Git Integration** tab.
4. Set **Git Provider** to *GitHub* and input your GitHub username.
5. In your personal GitHub account, go to *Settings > Developer Settings > Personal Access Tokens (Classic)*, generate a token with the `repo` scope enabled, copy it, and paste it into the **Token / Password** field in Databricks. Save changes.
6. In the Databricks sidebar, go to **Workspace** > **Git Folders**.
7. Click **Add Git Folder**, paste your repository HTTPS URL, and complete the clone.

### 2.2. Registering External Location in Unity Catalog

1. In the Databricks sidebar, click **Catalog**.
2. Expand the connections menu and go to **External Locations** > **Create external location**.
3. Name it `s3-taxi-case-root`.
4. In **URL**, input your bucket URI: `s3://awae-yellow-taxi-case/`.
5. Select **AWS Quickstart (Recommended)** and click **Next**.
6. Databricks will redirect you to the **AWS CloudFormation** dashboard with a pre-filled stack template.
7. Scroll to the bottom of the CloudFormation page, check the IAM capabilities acknowledgment box, and click **Create stack**.
8. Wait 1-2 minutes until the status shifts to `CREATE_COMPLETE`. Return to Databricks to verify the connected status.

### 2.3. Configuring Databricks Secrets Vault

1. Go to **User Settings** > **Developer** and click **Manage** next to *Access tokens*.
2. Click **Generate new token**, name it `CLI-Scope-Token`, check the `workspace` API scope, and click **Generate**. Copy the token.
3. Open a terminal interface on your local machine and execute:

```bash
pip install databricks-cli
databricks configure --token --profile default

```

4. Input your Workspace base URL (e.g., `[https://community.cloud.databricks.com](https://community.cloud.databricks.com)`) and paste your API token.
5. Build the secure secrets scope and load your AWS keys by running:

```bash
databricks secrets create-scope --scope aws-keys --initial-manage-principal users
databricks secrets put-secret aws-keys aws-access-key --string-value "YOUR_AWS_ACCESS_KEY_ID"
databricks secrets put-secret aws-keys aws-secret-key --string-value "YOUR_AWS_SECRET_ACCESS_KEY"

```

---

## Step 3: Running the Data Pipeline (ETL)

Execute the notebooks sequentially inside your cloned Git Folder in Databricks:

1. **`00_ingestion_to_landing.py`**: Run to initiate the raw parquet HTTP stream into your AWS S3 landing bucket. Note that `%pip install boto3 requests` must be executed at the top of this notebook session to instantiate libraries.
2. **`01_landing_to_bronze.py`**: Run to scan raw files individually, apply isolation parameters, and build initial Delta formats.
3. **`02_bronze_to_silver.py`**: Run to execute full schema expansion and un-filtered data consolidation.
4. **`02_b_create_dimensions.py`**: Run to build and overwrite the metadata lookup dimension tables as standard Parquet files.
5. **`03_silver_to_gold.py`**: Run to trigger dimensional Left Joins, implement business filtering rules, and save the curated analytical Fact Table.
6. **`analysis/spark_analysis.py`**: Run optionally to validate the calculated monthly average responses directly on PySpark and SparkSQL engines.

---

## Step 4: Streamlit UI Cloud Deployment

1. Make sure all your application updates (`src/app/main.py`, `src/app/db_connector.py`, `requirements.txt`) are committed and pushed to your GitHub repository.
2. Log into the official [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click the **Create App** button on the top-right corner.
4. Map the following setup fields:
* **Repository**: `your-user/ifood-case`
* **Branch**: `main`
* **Main file path**: `src/app/main.py`


5. Click **Advanced settings...** at the bottom of the deployment window.
6. In the **Secrets** section, paste your S3 credentials in the exact TOML format:

```toml
AWS_ACCESS_KEY_ID = "YOUR_AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "YOUR_AWS_SECRET_ACCESS_KEY"
AWS_DEFAULT_REGION = "us-east-1"

```

7. Click **Save** and select **Deploy!**. DuckDB will instantly stream and aggregate data directly on-demand from the Gold Parquet files.