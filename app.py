import os
import mysql.connector
from mysql.connector import Error
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"],  
)
DBHOST = os.getenv('DBHOST')
DBUSER = os.getenv('DBUSER')
DBPASS = os.getenv('DBPASS')  
DB = "njd5rd" 

def connect_db():
    try:
        db = mysql.connector.connect(
            host=DBHOST,
            user=DBUSER,
            password=DBPASS,
            database=DB
        )
        cur = db.cursor(dictionary=True)  
        return db, cur
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None, None

@app.get("/")  
def read_root():
   return {"message": "Welcome to my API!"}
@app.get('/genres')
def get_genres():
    db = mysql.connector.connect(user=DBUSER, host=DBHOST, password=DBPASS, database=DB)
    cur=db.cursor()
    query = "SELECT * FROM genres ORDER BY genreid;"
    try:    
        cur.execute(query)
        headers=[x[0] for x in cur.description]
        results = cur.fetchall()
        json_data=[]
        for result in results:
            json_data.append(dict(zip(headers,result)))
        cur.close()
        db.close()
        return(json_data)
    except Error as e:
        cur.close()
        db.close()
        return {"Error": "MySQL Error: " + str(e)}
@app.get('/songs')
def get_songs():
    db = mysql.connector.connect(user=DBUSER, host=DBHOST, password=DBPASS, database=DB)
    cur = db.cursor()
    
    query = """
    SELECT 
        songs.title AS title, 
        songs.album AS album, 
        songs.artist AS artist, 
        songs.year AS year, 
        CONCAT('https://my-bucket.s3.amazonaws.com/', songs.file) AS file,
        CONCAT('https://my-bucket.s3.amazonaws.com/', songs.image) AS image,
        genres.genre AS genre
    FROM songs
    JOIN genres ON songs.genre = genres.genreid
    ORDER BY songs.title;
    """
    
    try:    
        cur.execute(query) 
        headers = [x[0] for x in cur.description] 
        results = cur.fetchall()  
        
        json_data = []
        for result in results:
            json_data.append(dict(zip(headers, result)))
        
        cur.close()
        db.close()
        
        return json_data
    
    except Error as e:
        cur.close()
        db.close()
        return {"Error": "MySQL Error: " + str(e)}

