# Import necessary libraries
import os
import mysql.connector
from mysql.connector import Error
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you can restrict to specific domains if needed)
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)
# Database connection details
DBHOST = os.getenv('DBHOST')
DBUSER = os.getenv('DBUSER')
DBPASS = os.getenv('DBPASS')  # Password stored as environment variable
DB = "njd5rd"  # Replace with your actual database name

# Function to connect to the database
def connect_db():
    try:
        db = mysql.connector.connect(
            host=DBHOST,
            user=DBUSER,
            password=DBPASS,
            database=DB
        )
        cur = db.cursor(dictionary=True)  # Ensures results are returned as dictionaries
        return db, cur
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None, None

@app.get("/")  # Root endpoint
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
    # Connect to the database
    db = mysql.connector.connect(user=DBUSER, host=DBHOST, password=DBPASS, database=DB)
    cur = db.cursor()
    
    # Define the JOIN query
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
        cur.execute(query)  # Execute the query
        headers = [x[0] for x in cur.description]  # Extract column headers
        results = cur.fetchall()  # Fetch all rows
        
        # Convert rows to JSON format
        json_data = []
        for result in results:
            json_data.append(dict(zip(headers, result)))
        
        # Close the cursor and connection
        cur.close()
        db.close()
        
        # Return the data
        return json_data
    
    except Error as e:
        cur.close()
        db.close()
        return {"Error": "MySQL Error: " + str(e)}

