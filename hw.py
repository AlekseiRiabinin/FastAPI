from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()


class Order(BaseModel):
    order_id: int
    customer_name: str
    items: List[str]
    total_amount: float


orders_db = {}


# Создание заказа (POST /orders/):
# Принимает данные заказа и возвращает созданный заказ с order_id.
@app.post("/orders/", response_model=Order, status_code=201)
async def create_order(order: Order):
    orders_db[order.order_id] = order
    return order


# Получение заказа по ID (GET /orders/{order_id}):
# Возвращает информацию о заказе по заданному order_id.
@app.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: int):
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# Обновление заказа (PATCH /orders/{order_id}):
# Позволяет обновлять данные заказа по order_id.
@app.patch("/orders/{order_id}", response_model=Order)
async def update_order(order_id: int, order: Order):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    orders_db[order_id] = order
    return order


# Удаление заказа (DELETE /orders/{order_id}):
# Удаляет заказ по order_id и возвращает сообщение об успешном удалении.
@app.delete("/orders/{order_id}")
async def delete_order(order_id: int):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    del orders_db[order_id]
    return {"detail": "Order deleted"}
