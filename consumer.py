from kafka import KafkaConsumer
import json

# اتصال به Kafka و خوندن پیام‌ها
consumer = KafkaConsumer(
    'test-topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',  # از اولین پیام شروع کن
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

print("در حال گوش دادن به پیام‌ها...")
for message in consumer:
    print(f"پیام دریافت شد: {message.value}")
    break  # فقط یه پیام بگیر و تموم کن