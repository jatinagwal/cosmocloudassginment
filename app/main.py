# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient
from bson.objectid import ObjectId
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# MongoDB Connection
try:
    client = MongoClient("mongodb+srv://colab442:6aZKMVhvimhB7heY@cluster0.uevmpcw.mongodb.net/")
    db = client["school"]
    collection = db["students"]
    logging.info("Connected to MongoDB successfully.")
except Exception as e:
    logging.error("Error connecting to MongoDB: %s", str(e))
    raise HTTPException(status_code=500, detail="Error connecting to the database.")

app = FastAPI()

# Model for Student
class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    id: str = None
    name: str
    age: int
    address: Address

# API Endpoints
@app.post("/students/", status_code=201, response_model=Student)
def create_student(student: Student):
    try:
        inserted_student = collection.insert_one(student.dict(exclude={'id'}))
        created_student = collection.find_one({"_id": inserted_student.inserted_id})
        return Student(id=str(created_student['_id']), **created_student)
    except Exception as e:
        logging.error("Error creating student: %s", str(e))
        raise HTTPException(status_code=500, detail="Error creating the student.")

@app.get("/students/", response_model=List[Student])
def list_students(country: Optional[str] = None, age: Optional[int] = None):
    try:
        filter_query = {}
        if country:
            filter_query["address.country"] = country
        if age:
            filter_query["age"] = {"$gte": age}
        students = list(collection.find(filter_query))
        return [Student(id=str(student['_id']), **student) for student in students]
    except Exception as e:
        logging.error("Error listing students: %s", str(e))
        raise HTTPException(status_code=500, detail="Error retrieving the students.")

@app.get("/students/{id}", response_model=Student)
def get_student(id: str):
    try:
        student = collection.find_one({"_id": ObjectId(id)})
        if student:
            return Student(id=str(student['_id']), **student)
        else:
            raise HTTPException(status_code=404, detail="Student not found")
    except Exception as e:
        logging.error("Error getting student: %s", str(e))
        raise HTTPException(status_code=500, detail="Error retrieving the student.")

@app.patch("/students/{id}", status_code=204)
def update_student(id: str, student: Student):
    try:
        updated_student = collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": student.dict(exclude={'id'})},
            return_document=True
        )
        if updated_student:
            return
        else:
            raise HTTPException(status_code=404, detail="Student not found")
    except Exception as e:
        logging.error("Error updating student: %s", str(e))
        raise HTTPException(status_code=500, detail="Error updating the student.")

@app.delete("/students/{id}", status_code=200)
def delete_student(id: str):
    try:
        deleted_student = collection.find_one_and_delete({"_id": ObjectId(id)})
        if deleted_student:
            return {"message": "Student deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Student not found")
    except Exception as e:
        logging.error("Error deleting student: %s", str(e))
        raise HTTPException(status_code=500, detail="Error deleting the student.")