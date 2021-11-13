from time import time
from influxdb import InfluxDBClient, client
from datetime import datetime
from datetime import datetime
from typing import Dict, Optional
from fastapi import FastAPI, Response, status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

dataBase = "ApiTest"
measurement_ = "Sensor"
server_IP = "10.0.0.10"
server_PORT = 8086

app = FastAPI()

class Post(BaseModel): #Post schema
    measurement: str
    tags: Dict[str,str]
    fields: Dict[str,str]
    timestamp: Optional[datetime]  = None

try:
    client = InfluxDBClient(server_IP, server_PORT)
    ping = client.ping()
    if ping == None:
        raise Exception
    client.switch_database(dataBase)
    print("Connected")
except Exception:
    while(1):
        print("Database Connection Failed")
        time.sleep(2.5)
    

@app.get("/") #   "/" url root path
def root():
    return {"Version": "Api V.1.0.2", "For more info": "type /docs"}

@app.get(f"/{measurement_}")
def get_posts():
    postQuery = list(client.query(f"SELECT * FROM {measurement_}").get_points(measurement=measurement_))
    return {"data": postQuery}


#This method extracts the data from the body of the post being published.
@app.post("/posts", status_code=HTTP_201_CREATED)
def create_posts(post:Post):
    post_dict = post.dict();
    jsonBod = []
    jsonBod.append(post_dict)
    client.write_points(jsonBod)
    return {"data": jsonBod, "data": "Successfully Created!"}  

@app.get("/posts/{id}")
def get_posts(id: str, resp: Response):
    postQuery = client.query(f"SELECT * FROM {measurement_}")
    idPoints = list(postQuery.get_points(tags={"id": f"{id}"}))
    if not idPoints:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id #{id} was not found!")
    return {"post_detail": idPoints}                                    



@app.delete("/posts/{id}/{type}", status_code=HTTP_204_NO_CONTENT)
def del_posts(id: str, type: str):
    postQuery = client.query(f"SELECT * FROM {measurement_}")
    idPoints = list(postQuery.get_points(tags={"id": f"{id}","type": f"{type}"}))
    if not idPoints:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id #{id} and type {type} was not found!")
    client.delete_series(tags={"id": f"{id}","type": f"{type}"})
    return Response(status_code=status.HTTP_204_NO_CONTENT)







