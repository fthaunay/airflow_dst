from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.sensors.filesystem import FileSensor
from airflow.operators.docker_operator import DockerOperator
from docker.types import Mount
from build_init_order import build_init_order

with DAG(
    dag_id='load_order',
    tags=['order', 'docker', 'postgres', 'datascientest'],
    default_args={
        'owner': 'airflow',
        'start_date': days_ago(0, minute=1),
    },
    schedule_interval='0 17 * * *'
    catchup=False
) as dag:

    init_order = build_init_order(dag)

    orders_sensor = FileSensor(
    task_id='orders_sensor',
    filepath='data/to_ingest/bronze/orders.json',
    poke_interval=20,
    timeout=120,
    mode='poke'
)

    python_transform = DockerOperator(
    task_id='python_transform',
    image='python_transform:latest',
    auto_remove=True,
    command='python3 main.py',
    mounts=[
        Mount(source='/home/ubuntu/airflow/data/to_ingest', target='/app/data/to_ingest', type='bind')
    ]
)

    python_load = DockerOperator(
    task_id='python_load',
    image='python_load:latest',
    auto_remove=True,
    environment={
        'HOST': 'postgres',
        'DATABASE': 'airflow',
        'USER': 'airflow',
        'PASSWORD': 'airflow'
    },
    command='python3 main.py',
    network_mode='airflow_default',
    mounts=[
        Mount(source='/home/ubuntu/airflow/data/to_ingest', target='/app/data/to_ingest', type='bind')
    ]
)

    init_order >> orders_sensor >> python_transform >> python_load