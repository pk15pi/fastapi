from fastapi import Depends, FastAPI, Path
from routers.user import get_current_user
from routers import subject, question, options  # Correct import paths
from database import Base, engine
from config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# make all endpoints secure. These all needs to be JWT authenticated
# from fastapi import FastAPI, Depends
# from auth import get_current_user
# app = FastAPI(dependencies=[Depends(get_current_user)])
app = FastAPI()

##########################################################################################
# Authentication can be implemented on selected endpoint also
# quiz_router = APIRouter(prefix="/quiz", dependencies=[Depends(get_current_user)])

# @quiz_router.get("/questions")
# def get_questions():
#     return {"msg": "Only for authenticated users"}

# app.include_router(quiz_router)


######################### Keycloak integration #################
KEYCLOAK_URL = "http://localhost:8080"
KEYCLOAK_REALM = "fastapi"
KEYCLOAK_CLIENT_ID = "fastapi"
KEYCLOAK_ISSUER = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}"
KEYCLOAK_JWKS_URL = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/certs"
KEYCLOAK_OFFLINE_TOKEN = "your_hardcoded_offline_token_here"


###########################################################################################

##################################### not reccommende for production
# Create database tables
'''
Keep this line in seperate file and call with python filename.py
If kept here it will create/update tables every time the program runs.
if kept in seperate file, table will update/create only when the script is called
'''
Base.metadata.create_all(bind=engine)

# This will create tables when the app starts
# @app.on_event("startup")
# def on_startup():
#     Base.metadata.create_all(bind=engine)

################################## recommended for production #####################
'''
1: pip install alembic
2: In the root of the project run commnad
    alembic init alembic

    this will create:
    .
    ├── alembic/
    │   ├── versions/
    │   └── env.py
    ├── alembic.ini

3: Configure alembic.ini
    Open alembic.ini and update the sqlalchemy.url with your DB connection:

    sqlalchemy.url = sqlite:///./quiz.db
    PostgreSQL: postgresql://user:password@localhost/dbname
    MySQL/MariaDB: mysql+pymysql://user:pass@localhost/dbname
    MSSQL: mssql+pyodbc://user:pass@localhost/dbname?driver=ODBC+Driver+17+for+SQL+Server
    Oracle: oracle+cx_oracle://user:pass@localhost:1521/?service_name=orcl

4: Edit env.py to Include Your Models
    At the top of alembic/env.py, add:
        import sys
        import os
        from config import settings
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

        from database import Base
        from models import *  # make sure this includes all models
        target_metadata = Base.metadata

        # instead of using sqlalchemy.url from alembic.ini
        config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


5: Create an Migration
    alembic revision --autogenerate -m "whatever message"

    Alembic will scan your models and generate a new file in alembic/versions/ containing the migration.

6: Apply the Migration (Create Tables)
    alembic upgrade head

7: Common commands:
    alembic downgrade -1	    Revert last migration
    alembic current	            Show current DB migration version
    alembic history	            View all migration history

'''


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
    },
    4: {
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
        
