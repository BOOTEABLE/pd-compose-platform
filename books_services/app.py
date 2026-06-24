from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
import psycopg2
import os

# Definimos la estructura de datos que esperamos recibir al crear un libro
class Book(BaseModel):
    title: str
    author: str

# Función para conectarse a la base de datos PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'db'),
        database=os.environ.get('DB_NAME', 'biblioteca'),
        user=os.environ.get('DB_USER', 'myuser'),
        password=os.environ.get('DB_PASSWORD', 'mypassword')
    )

# Función para inicializar la tabla en la base de datos
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id SERIAL PRIMARY KEY,
            title VARCHAR(150) NOT NULL,
            author VARCHAR(100) NOT NULL
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Configuramos el ciclo de vida para ejecutar init_db() al arrancar el servicio
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

# Inicializamos la aplicación FastAPI
app = FastAPI(title="Books Service", lifespan=lifespan)

# 1. Ruta para OBTENER TODOS los libros (GET general)
@app.get('/books')
def get_books():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM books;')
    books = cur.fetchall()
    cur.close()
    conn.close()
    
    # Formateamos la respuesta como una lista de diccionarios
    return [{'id': row[0], 'title': row[1], 'author': row[2]} for row in books]


# 2. Ruta para OBTENER UN SOLO libro por su ID (GET específico)
@app.get('/books/{book_id}')
def get_book(book_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Usamos WHERE para buscar solo el ID que pasaste en la URL
    cur.execute('SELECT * FROM books WHERE id = %s;', (book_id,))
    book = cur.fetchone()
    cur.close()
    conn.close()
    
    # Si el libro no existe, lanzamos el error 404
    if book is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    # Si existe, devolvemos solo ese libro
    return {'id': book[0], 'title': book[1], 'author': book[2]}

# 2. Ruta para AGREGAR un nuevo libro (POST)
@app.post('/books', status_code=201)
def add_book(book: Book):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO books (title, author) VALUES (%s, %s)', 
        (book.title, book.author)
    )
    conn.commit()
    cur.close()
    conn.close()
    
    return {'message': 'Libro agregado exitosamente'}

# 3. Ruta para ACTUALIZAR un libro existente (PUT)
@app.put('/books/{book_id}')
def update_book(book_id: int, book: Book):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Primero verificamos si el libro existe
    cur.execute('SELECT id FROM books WHERE id = %s;', (book_id,))
    if cur.fetchone() is None:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    # Si existe, lo actualizamos
    cur.execute(
        'UPDATE books SET title = %s, author = %s WHERE id = %s', 
        (book.title, book.author, book_id)
    )
    conn.commit()
    cur.close()
    conn.close()
    
    return {'message': 'Libro actualizado exitosamente'}

# 4. Ruta para ELIMINAR un libro (DELETE)
@app.delete('/books/{book_id}')
def delete_book(book_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Primero verificamos si el libro existe
    cur.execute('SELECT id FROM books WHERE id = %s;', (book_id,))
    if cur.fetchone() is None:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    # Si existe, lo eliminamos
    cur.execute('DELETE FROM books WHERE id = %s', (book_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    return {'message': 'Libro eliminado exitosamente'}