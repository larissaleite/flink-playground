from datetime import datetime
import os
from pyflink.datastream.stream_execution_environment import StreamExecutionEnvironment
from pyflink.datastream.time_characteristic import TimeCharacteristic
from pyflink.table import (
    StreamTableEnvironment,
    DataTypes,
    EnvironmentSettings,
    CsvTableSink,
)
from pyflink.table.sinks import WriteMode
from pyflink.table.window import Tumble

env_settings = (
    EnvironmentSettings.new_instance().in_streaming_mode().use_blink_planner().build()
)

execution_environment = StreamExecutionEnvironment.get_execution_environment()
execution_environment.set_parallelism(1)
execution_environment.set_stream_time_characteristic(TimeCharacteristic.EventTime)

table_env = StreamTableEnvironment.create(
    execution_environment, environment_settings=env_settings
)
statement_set = table_env.create_statement_set()

KAFKA_BROKER_URL = "kafka:29092"
KAFKA_TOPIC = "user.events.v1"


def source_from_kafka():
    ddl = f"""
    CREATE TABLE user_events (
        event_id VARCHAR,
        event_timestamp VARCHAR,
        platform VARCHAR,
        user_id VARCHAR,
        country VARCHAR,
        event_ts AS TO_TIMESTAMP(event_timestamp),
        WATERMARK FOR event_ts AS event_ts - INTERVAL '30' SECOND
    ) WITH (
        'connector' = 'kafka',
        'topic' = '{KAFKA_TOPIC}',
        'properties.bootstrap.servers' = '{KAFKA_BROKER_URL}',
        'properties.group.id' = 'group-1',
        'format' = 'json',
        'scan.startup.mode' = 'earliest-offset'
    ) """

    table_env.execute_sql(ddl)


def sink_into_csv():
    ddl = """
    CREATE table sink_into_csv (
       country STRING,
       count_sessions BIGINT,
       last_window_timestamp TIMESTAMP(3)
    ) WITH (
        'connector' = 'filesystem',
        'path' = 'output_file.csv' ,
        'format' = 'csv',
        'sink.partition-commit.policy.kind'='success-file',
        'sink.partition-commit.delay' = '3 min'
    ) """

    table_env.execute_sql(ddl)


def run_job():
    source_from_kafka()
    sink_into_csv()

    table_env.scan("user_events").window(
        Tumble.over("1.minute").on("event_ts").alias("w")
    ).group_by("country, w").select(
        "country AS country, COUNT(1) AS count_sessions, w.end AS last_window_timestamp"
    ).insert_into(
        "sink_into_csv"
    )

    table_env.execute("Kafka user events to CSV")


if __name__ == "__main__":
    run_job()
