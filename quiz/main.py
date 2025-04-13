from fastapi import FastAPI
from routers import subject, question, options  # Correct import paths
from database import Base, engine

app = FastAPI()

# Create database tables (this should be fine)
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(subject.router)
app.include_router(question.router)
app.include_router(options.router)

# Default route
@app.get("/")
def root():
    return {"message": "Quiz API is running!"}

# how to pass parameters and parameter based queries
students = {
    1: {
        "name" : "Kailash",
        "title" : "Yadav",
        "age" : 20
    },
    2: {
        "name" : "Mrityunjay",
        "Title" : "Verma",
        "age" : 18
    },
    3: {
        "name" : "Rajan",
        "Title" : "Sirohi",
        "age" : 15
    }
}

@app.get("/res")
def res():
    return students

# get data at provided index
@app.get("/get-by-id/{student_id}/")
def getById(student_id: int):
    return students[student_id]

# Add Path patameter to provide help text to user on swagger,
# add validations
@app.get("/get-by-id-and-validate/{student_id}/")
def getById(student_id: int = Path(
    description="Provide ID of the student",
    gt=0, lt=3)
    ):
    return students[student_id]


@app.get("/get-by-name/{student_name}/")
def getByName(student_name:str):
    res = []
    print(student_name, "###")
    for rec in students:
        # for loop enumerates indexes
        print(rec)
        if students[rec]['name'] == student_name:
            res.append(students[rec])
    if res:
        return res
    else:
        return {"Data" : "No data found"}
        
