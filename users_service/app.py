from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
import psycopg2
import os

class User(BaseModel):
    name: str
    email: str

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'db'),
        database=os.environ.get('DB_NAME', 'biblioteca'),
        user=os.environ.get('DB_USER', 'myuser'),
        password=os.environ.get('DB_PASSWORD', 'mypassword')
    )

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(150) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Users Service", lifespan=lifespan)

@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")

@app.get('/users')
def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users;')
    users = cur.fetchall()
    cur.close()
    conn.close()
    return [{'id': u[0], 'name': u[1], 'email': u[2]} for u in users]

@app.post('/users', status_code=201)
def add_user(user: User):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO users (name, email) VALUES (%s, %s)', (user.name, user.email))
    conn.commit()
    cur.close()
    conn.close()
    return {'message': 'Usuario agregado'}

@app.put('/users/{user_id}')
def update_user(user_id: int, user: User):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE users SET name = %s, email = %s WHERE id = %s', (user.name, user.email, user_id))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    conn.commit()
    cur.close()
    conn.close()
    return {'message': 'Usuario actualizado'}

@app.delete('/users/{user_id}')
def delete_user(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM users WHERE id = %s', (user_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    conn.commit()
    cur.close()
    conn.close()
    return {'message': 'Usuario eliminado'}