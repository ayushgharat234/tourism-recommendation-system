FROM apache/airflow:2.7.1-python3.9

USER root

# Install system dependencies (optional for plugins or builds)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Copy and install Python dependencies
COPY requirements.txt /opt/airflow/requirements.txt
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt

# Add custom Airflow plugins/modules
COPY ./src /opt/airflow/src
COPY ./dags /opt/airflow/dags
COPY ./sql /opt/airflow/sql

# Set PYTHONPATH for custom modules
ENV PYTHONPATH=/opt/airflow:/opt/airflow/src
