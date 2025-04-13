FROM apache/airflow:2.7.1-python3.9

USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install Python packages
COPY requirements.txt /opt/airflow/requirements.txt
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt

# Set the PYTHONPATH
ENV PYTHONPATH=/opt/airflow 