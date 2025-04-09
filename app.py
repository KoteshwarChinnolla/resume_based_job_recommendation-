from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
import uvicorn

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

class Job(BaseModel):
    company: str
    job_description: str
    role: str
    experience: int
    apply_link: str
    skills: list[str]
    location: str
    salary: int
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

@app.post("/check-jobs")
async def check_jobs(skill: Skill):

    jobs = db.jobs.find({"skills": skill.name}).to_list(length=100)
    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs found for this skill")
 
    matched_jobs = [
        {
            "company": job['company'],
            "job_description": job['job_description'],
            "role": job['role'],
            "experience": job['experience'],
            "apply_link": job['apply_link'],
            "skills": job['skills']
        }
        for job in jobs if skill.name in job['skills']
    ]

    return matched_jobs

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)