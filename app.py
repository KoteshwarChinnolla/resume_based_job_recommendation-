from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
import uvicorn
from chatbot.job_search import JobSearch
from typing import List, Optional
# from chatbot.job_q import build_graph
from langchain_core.prompts import ChatPromptTemplate
import markdown
from markdownify import markdownify as md
from convertion import JobDataTransformer

converter = JobDataTransformer()

# graph=build_graph()


JobSearch = JobSearch()

app = FastAPI()

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client=MongoClient('mongodb+srv://Mithunlogin:12345@cluster0.nfdmggi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['Growup']

class Skill(BaseModel):
    name: str

class prompt_to_job(BaseModel):
    prompt: str
    thread_id: str = "67f4b82e377e28f0a580a913b4c0d3f"
    name: str = "user"

class Job(BaseModel):
    company: str
    job_description: str
    role: str
    from_experience: float
    to_experience: float
    apply_link: str
    skills: list[str]
    city: str
    state: str
    country: str
    from_salary: float
    to_salary: float
    date: str
    job_type: str

class login(BaseModel):
    email: str
    password: str

class signup(BaseModel):
    name: str
    email: str
    phone: str
    password: str

class edit_job(BaseModel):
    job_id: str
    updates: dict

class d_job(BaseModel):
    job_id: str

class details(BaseModel):
    company: Optional[str] = None
    job_description: Optional[str] = None
    role: str = None
    from_experience: Optional[int] = None
    to_experience: Optional[int] = None
    apply_link: Optional[str] = None
    skills: Optional[List[str]] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    from_salary: Optional[int] = None
    to_salary: Optional[int] = None
    date: Optional[str] = None
    job_type: Optional[str] = None
 


# Sign Up route
@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI backend!"}


@app.post("/signup")
async def signup(user: signup):
    user_dict = user.dict()
    for_login={}
    for_login['email']=user_dict['email']
    for_login['password']=user_dict['password']
    db.login_info.insert_one(for_login)
    db.users.insert_one(user_dict)  # Store user data in MongoDB
    return {"message": "User created successfully"}

# Login route
@app.post("/login")
async def login(user: login):
    existing_user = db.users.find_one({"email": user.email, "password": user.password})
    if existing_user:
        return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/add-job")
async def add_job(job: Job):
    job_dict = job.dict()
    print(job_dict)
    db.jobs.insert_one(job_dict)
    return {"message": "Job added successfully"}

@app.post("/delete-job")
async def delete_job(job_id: d_job):
    result = db.jobs.delete_one({"_id": ObjectId(job_id.job_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted successfully"}

@app.post("/edit_job")
async def edit_job(edit_details:edit_job):
    job_id = edit_details.job_id
    updated_data = edit_details.updates
    result = db.jobs.update_one({"_id": ObjectId(job_id)}, {"$set": updated_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job updated successfully"}



@app.post("/search_jobs")
async def search_jobs(details:details):
    sended_data={}
    for key, value in details.model_dump().items():
        if(type(value) == list):
            if "string" not in value:
                sended_data[key] = value
        elif(type(value) == str):
            if value != "string" :
                sended_data[key] = value
    print(sended_data)
    result1,result2=JobSearch.search(user_input=sended_data)
    return result1,result2

@app.get("/get-jobs")
async def get_jobs():
    jobs = db.jobs.find().to_list()
    list_of_jobs = []
    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs found")
    list_of_jobs = converter.transform_job_data(jobs)
    return list_of_jobs
# @app.post("/prompt_to_job")
# def prompt_to_job(prompt: prompt_to_job):
#     text = prompt.prompt
#     name = prompt.name
#     thread_id = prompt.thread_id
#     response=graph.response(text,name=name,thread_id=thread_id)
#     html_text = markdown.markdown(response)
#     response = md(html_text,heading_style="ATX")
#     return response

if _name_ == "_main_":
    uvicorn.run(app, host="127.0.0.1", port=8000)