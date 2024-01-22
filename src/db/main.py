from os import walk

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

import database.crud as crud
import database.models as models
import database.schemas as schemas
from database.database import async_session, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Dependency
def get_db():
    db = async_session()
    try:
        yield db
    finally:
        db.close()


@app.post('/operation')
def add_operation(operation: schemas.OperationBase):
    print(operation)
    return 'operation added'

@app.get('/operation')
def get_operation():

    return 'ok'

@app.get('/icons')
def get_icons():

    path = 'front-end/src/components/CategoryItem/icons'

    f = []
    for (_, _, filenames) in walk(path):
        for filename in filenames:
            if not filename.startswith('.'):
                f.append(filename)
    return f


@app.get('/icon/{icon_name}')
def get_icon(icon_name: str):
    icons_dir = 'front-end/src/components/CategoryItem/icons/'
    return FileResponse(icons_dir + icon_name)


@app.get('/balance/{user_id}')
def get_balance(user_id: int):
    if user_id == 12345:
        return 20000
    else:
        return 0


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post('/expenses/', response_model=schemas.Expenditure)
def create_expense(expense: schemas.ExpenditureCreate, db: Session = Depends(get_db)):
    db_category = crud.get_category_by_title(db, expense.category)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return crud.create_expense(db, expense)


@app.post('/categories/', response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    return crud.create_category(db, category)


@app.get("/categories/{group}")
def read_categories(group: str):
    # categories = crud.get_categories(db, skip=skip, limit=limit)
    if group == 'income':
        return [
            {'name': 'Tinkoff', 'sum': 10000, 'icon': 'money.png'}
        ]
    elif group == 'expense':
        return [
            {'name': 'Products', 'sum': 5000, 'icon': 'products.png'},
            {'name': 'Cafe', 'sum': 2000, 'icon': 'icons8-food-bar-100.png'},
            {'name': 'Transport', 'sum': 3000, 'icon': 'transport.png'}
        ]
    else:
        return 'Invalid group.'


@app.get('/balance/')
def get_balance(user_id: int, db: Session = Depends(get_db)):
    balance = crud.get_balance_by_user_id(db, user_id)
    return balance if balance else {'message': 'User not found.'}


@app.post('/balance/', response_model=schemas.Bank)
def set_balance(balance: schemas.BalanceCreate, db: Session = Depends(get_db)):
    return crud.set_balance(db, balance)
