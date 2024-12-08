#import os

#from chalice import Chalice

#app = Chalice(app_name='ingestor')
#app.debug = True


# Set the value of APP_BUCKET_NAME in the .chalice/config.json file.
#S3_BUCKET = os.environ.get('njd5rd-dp1-spotify', '')


#@app.on_s3_event(bucket=S3_BUCKET, events=['s3:ObjectCreated:*'])
#def s3_handler(event):
    #app.log.debug("Received event for bucket: %s, key: %s",
                 #event.bucket, event.key)

import os
import json
import mysql.connector
import boto3
from chalice import Chalice

app = Chalice(app_name='ingestor')
app.debug = True

# Configuration from environment variables
S3_BUCKET = 'njd5rd-dp1-spotify'
DBHOST = os.getenv('DBHOST')
DBUSER = os.getenv('DBUSER')
DBPASS = os.getenv('DBPASS')
DB = os.getenv('DB')
BASE_URL = f"http://{S3_BUCKET}.s3-website-us-east-1.amazonaws.com/"

# Supported file extensions
SUPPORTED_EXTENSIONS = ('.json',)

def is_json(key):
    """Check if the file has a .json extension."""
    return key.endswith(SUPPORTED_EXTENSIONS)

@app.on_s3_event(bucket=S3_BUCKET, events=['s3:ObjectCreated:*'])
def s3_handler(event):
    # Create S3 and database connections within the function
    s3 = boto3.client('s3')
    
    # Log the event
    app.log.debug(f"Received event for bucket: {event.bucket}, key: {event.key}")
    
    if is_json(event.key):
        try:
            # Retrieve and parse the JSON file
            response = s3.get_object(Bucket=event.bucket, Key=event.key)
            text = response["Body"].read().decode()
            data = json.loads(text)
            
            # Extract metadata from the JSON
            TITLE = data.get('title', 'Unknown Title')
            ALBUM = data.get('album', 'Unknown Album')
            ARTIST = data.get('artist', 'Unknown Artist')
            YEAR = data.get('year', 'Unknown Year')
            GENRE = data.get('genre', 'Unknown Genre')
            
            # Create MP3 and image URLs
            keyhead = event.key
            identifier = keyhead.split('.')[0]
            MP3 = f"{BASE_URL}{identifier}.mp3"
            IMG = f"{BASE_URL}{identifier}.jpg"
            
            # Create database connection
            with mysql.connector.connect(
                user=DBUSER, 
                host=DBHOST, 
                password=DBPASS, 
                database=DB
            ) as db:
                with db.cursor() as cur:
                    # Insert the song into the database
                    add_song = (
                        "INSERT INTO songs "
                        "(title, album, artist, year, file, image, genre) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    )
                    song_vals = (TITLE, ALBUM, ARTIST, YEAR, MP3, IMG, GENRE)
                    cur.execute(add_song, song_vals)
                    db.commit()
                    
            app.log.info(f"Successfully inserted song: {TITLE}")
            
        except mysql.connector.Error as err:
            app.log.error(f"Failed to insert song: {err}")
        except Exception as e:
            app.log.error(f"Unexpected error: {e}")
