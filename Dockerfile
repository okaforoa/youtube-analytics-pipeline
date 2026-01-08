FROM apache/airflow:2.10.4-python3.12

# Copy requirements file
COPY airflow/requirements.txt /requirements.txt

# Install requirements as airflow user
USER airflow
RUN pip install --no-cache-dir -r /requirements.txt

USER airflow
