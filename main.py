from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine, SessionLocal, get_db
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

#Initialize a new FastAPI application
app = FastAPI()


#Create database tables
models.Base.metadata.create_all(bind=engine)

db_dependency = Annotated[Session, Depends(get_db)]

class TodoBase(BaseModel):
    id: int
    task_body: str
    due_day: int
    due_month: str
    due_year: int


@app.post("/todos", status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoBase, db: db_dependency):
    db_todo = models.Todo(**todo.model_dump())
    db.add(db_todo)
    db.commit()
    return {"detail": "Todo added successfully"}


@app.get("/todos", status_code=status.HTTP_200_OK)
async def get_todos(db: db_dependency):
    return db.query(models.Todo).all()


@app.put("/todos/{todo_id}", response_model=TodoBase, status_code=status.HTTP_200_OK)
async def update_todo(todo_id: int, todo_request: TodoBase, db: db_dependency):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id)
    if db_todo.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    update_data = todo_request.model_dump(exclude_unset=True)

    #update the database record with the new data
    db_todo.update(update_data, synchronize_session=False)
    db.commit()

    return db_todo.first()

@app.delete("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def delete_todo(todo_id: int, db: db_dependency):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id)
    if db_todo.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    #delete the database record
    db_todo.delete(synchronize_session=False)
    db.commit()

    return {"detail": "Todo deleted successfully"}


# from .models import models, schemas
# from .controllers import orders
# from .dependencies.database import engine, get_db
#
# models.Base.metadata.create_all(bind=engine)
#
# app = FastAPI()
#
# origins = ["*"]
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
#
# @app.post("/orders/", response_model=schemas.Order, tags=["Orders"])
# def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
#     return orders.create(db=db, order=order)
#
#
# @app.get("/orders/", response_model=list[schemas.Order], tags=["Orders"])
# def read_orders(db: Session = Depends(get_db)):
#     return orders.read_all(db)
#
#
# @app.get("/orders/{order_id}", response_model=schemas.Order, tags=["Orders"])
# def read_one_order(order_id: int, db: Session = Depends(get_db)):
#     order = orders.read_one(db, order_id=order_id)
#     if order is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return order
#
#
# @app.put("/orders/{order_id}", response_model=schemas.Order, tags=["Orders"])
# def update_one_order(order_id: int, order: schemas.OrderUpdate, db: Session = Depends(get_db)):
#     order_db = orders.read_one(db, order_id=order_id)
#     if order_db is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return orders.update(db=db, order=order, order_id=order_id)
#
#
# @app.delete("/orders/{order_id}", tags=["Orders"])
# def delete_one_order(order_id: int, db: Session = Depends(get_db)):
#     order = orders.read_one(db, order_id=order_id)
#     if order is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return orders.delete(db=db, order_id=order_id)
