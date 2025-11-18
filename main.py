from fastapi import FastAPI
from pydantic import BaseModel
from haversine import haversine
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

photos_db = []

class Photo(BaseModel):
    name: str
    lat: float
    lon: float
    created: datetime

@app.post("/photos")
def create_photo(photo: Photo):
    photo_data = photo.model_dump()
    new_id = len(photos_db) + 1
    filename = f"{new_id}.png"
    
    photo_data["id"] = new_id
    photo_data["filename"] = filename
    
    photos_db.append(photo_data)
    
    return photo_data

@app.get("/photos/area")
def get_photos_in_area(min_lat: float, min_lon: float, max_lat: float, max_lon: float):
    results = []
    
    for photo in photos_db:
        if ((min_lat <= photo["lat"] <= max_lat)
                and (min_lon <= photo["lon"] <= max_lon)):
            results.append(photo)
            
    return results

@app.get("/photos/nearby")
def get_photos_nearby(lat: float, lon: float, radius: float=20.0):
    results = []
    user_location = (lat, lon)
    
    for photo in photos_db:
        photo_location = (photo["lat"], photo["lon"])
        
        distance = haversine(user_location, photo_location)
        
        if distance <= radius:
            photo_with_dist = photo.copy()
            photo_with_dist["distance"] = round(distance, 2)
            
            results.append(photo_with_dist)
    
    results.sort(key=lambda x: x["distance"])            
    
    return results