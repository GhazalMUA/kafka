from kafka import KafkaProducer
import json

# اتصال به Kafka
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# فرستادن یه پیام ساده
producer.send('test-topic', {'message': 'سلام دنیا!'})
producer.flush()  # مطمئن بشه پیام فرستاده شده

print("پیام ارسال شد!")