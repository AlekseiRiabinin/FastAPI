from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pika
import json
from clickhouse_driver import Client


app = FastAPI()

# setting RabbitMQ
rabbitmq_host = 'localhost'
rabbitmq_queue = 'data_queue'

credentials = pika.PlainCredentials('user', 'password')

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials)
)
channel = connection.channel()
channel.queue_declare(queue=rabbitmq_queue)

# setting ClickHouse
clickhouse_client = Client(host='localhost')


# data model
class DataModel(BaseModel):
    key: str
    value: str


# endpoint for sending data
@app.post("/send")
def send_data(data: DataModel):
    try:
        message = data.model_dump_json()
        channel.basic_publish(
            exchange='',
            routing_key=rabbitmq_queue,
            body=message
        )
        return {"status": "Message sent to RabbitMQ"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# function for processing messages
def callback(ch, method, properties, body):
    data = json.loads(body)
    clickhouse_client.execute(
        "INSERT INTO my_table (key, value) VALUES",
        [(data['key'], data['value'])]
    )


channel.basic_consume(
    queue=rabbitmq_queue,
    on_message_callback=callback,
    auto_ack=True
)


# endpoint for getting data
@app.get("/data")
def get_data():
    try:
        result = clickhouse_client.execute("SELECT * FROM my_table")
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
