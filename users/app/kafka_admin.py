import asyncio
from kafka import KafkaAdminClient, KafkaConsumer
from app import config

KAFKA_TOPIC = config.KAFKA_USER_DB_RESPONSE
KAFKA_BOOTSTRAP_SERVERS = config.BOOTSTRAP_SERVER

async def get_message_count():
    admin_client = KafkaAdminClient(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    
    try:
        topic_partitions = admin_client.describe_topics([KAFKA_TOPIC])[0].partitions
        total_messages = 0

        for partition in topic_partitions:
            partition_id = partition.partition
            earliest_offset = admin_client.list_consumer_group_offsets(
                'your_consumer_group_id', {KAFKA_TOPIC: partition_id}, offset='earliest'
            )
            latest_offset = admin_client.list_consumer_group_offsets(
                'your_consumer_group_id', {KAFKA_TOPIC: partition_id}, offset='latest'
            )

            earliest_offset_value = earliest_offset[(KAFKA_TOPIC, partition_id)].offset
            latest_offset_value = latest_offset[(KAFKA_TOPIC, partition_id)].offset

            total_messages += latest_offset_value - earliest_offset_value

        
        return total_messages
    finally:
        admin_client.close()
