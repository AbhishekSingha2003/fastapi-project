# Import necessary modules and define FastAPI instance
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define SQLAlchemy base
Base = declarative_base()

# Define CGPA model
class CGPA(Base):
    __tablename__ = 'cgpa'
    id = Column(Integer, primary_key=True)
    roll_no = Column(String, unique=True)
    cgpa = Column(Float)

# Define syllabus model
class Syllabus(Base):
    __tablename__ = 'syllabus'
    id = Column(Integer, primary_key=True)
    branch = Column(String)
    semester = Column(String)
    syllabus_file = Column(String)

# Create database engine and session
engine = create_engine('sqlite:///database.db', echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI instance
app = FastAPI()

# Define a data model for the request
class DialogflowRequest(BaseModel):
    queryResult: dict

# Define a function to check CGPA in the SQL database
def check_cgpa(roll_no):
    session = SessionLocal()
    cgpa = session.query(CGPA).filter(CGPA.roll_no == roll_no).first()
    if cgpa:
        return cgpa.cgpa
    else:
        return None

# Define a function to get syllabus branch and semester wise
def get_syllabus(branch, semester):
    session = SessionLocal()
    syllabus = session.query(Syllabus).filter(Syllabus.branch == branch, Syllabus.semester == semester).first()
    if syllabus:
        return syllabus.syllabus_file
    else:
        return None

# Define route to handle webhook requests
@app.post("/webhook")
async def webhook(request: DialogflowRequest):
    # Extract information from the request
    query_result = request.queryResult
    intent = query_result.get("intent", {}).get("displayName")
    parameters = query_result.get("parameters", {})

    # Determine what action to take based on the intent
    if intent == "Check CGPA":
        roll_no = parameters.get("roll_no")
        # Call function to check CGPA
        cgpa = check_cgpa(roll_no)
        if cgpa is not None:
            return {"fulfillmentText": f"Your CGPA is: {cgpa}"}
        else:
            raise HTTPException(status_code=404, detail="CGPA not found")

    elif intent == "Get Syllabus":
        branch = parameters.get("branch")
        semester = parameters.get("semester")
        # Call function to get syllabus
        syllabus_file = get_syllabus(branch, semester)
        if syllabus_file:
            return {"fulfillmentText": f"Here is the syllabus for {branch}, {semester}: {syllabus_file}"}
        else:
            raise HTTPException(status_code=404, detail="Syllabus not found")

    else:
        raise HTTPException(status_code=400, detail="Unknown intent")
