from pymongo import MongoClient

# MongoDB connection string
CONNECTION_STRING = "mongodb+srv://adminuser:edX4mktR69lZ4K8M@tradingcluster.xux7hfc.mongodb.net/"
mongo_client = MongoClient(CONNECTION_STRING)
students = mongo_client['TradingSystems']['student_data']

# CREATE: Insert a new student
student = {
    "name": "John Doe",
    "age": 21,
    "courses": ["Math", "Science", "History"]
}

student_id = students.insert_one(student).inserted_id
print(f"Inserted student with id: {student_id}")

student = {
    "name": "Sugam Gupta",
    "age": 35,
    "courses": ["Python", "Machine Learning", "AI"]
}
students.insert_one(student)


# READ: Find the student by name
found_student = students.find_one({"name": "John Doe"})
print("Found student:", found_student)




# UPDATE: Update the student's age
update_result = students.update_one(
    {"name": "John Doe"},
    {"$set": {"age": 25}}
)
print(f"Updated {update_result.modified_count} document(s)")




# READ: Verify the update
updated_student = students.find_one({"name": "John Doe"})
print("Updated student:", updated_student)




# DELETE: Remove the student
delete_result = students.delete_one({"name": "John Doe"})
print(f"Deleted {delete_result.deleted_count} document(s)")


