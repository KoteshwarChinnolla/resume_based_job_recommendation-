from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from tkinter import Tk, filedialog
from pdfminer.high_level import extract_text
import os
from dotenv import load_dotenv
import json
from roles import Roles

load_dotenv()
os.environ["GROQ_API_KEY"]= os.getenv("GROQ_API_KEY")


# Define your desired data structure.
class resume(BaseModel):
    name: str =Field(description="name of the student from given resume text")
    email: str = Field(description="email from given resume text")
    phone: str=Field(description="phone number from given text")
    all_skills: list[str] = Field(description="skills of the user from given resume text including skills from projects, internships, training etc..")
    major_skills: list[str] = Field(description="major highly mentioned skills from given resume text")
    experience: int =Field(description="experience from given resume text")
    address: str = Field(description="address from given resume text")
    schooling: str = Field(description="schooling from given resume text")
    tenth_marks: str = Field(description="tenth marks from given resume text")
    twelfth: str = Field(description="twelfth marks from given resume text")
    graduation: str = Field(description="graduation from given resume text")
    percentage: str = Field(description="percentage from given resume text")
    projects: list[str]=Field(description="projects from given resume text")
    internships: list[str]=Field(description="internships from given resume text")
    certifications: list[str]=Field(description="certifications from given resume text")
    hobbies: list[str]=Field(description="hobbies from given resume text")
    about: list[str]=Field(description="about from given resume text")
    languages: list[str]=Field(description="languages from given resume text")
    city: str = Field(description="location from given resume text")
    state: str = Field(description="state from given resume text")
    country: str = Field(description="country from given resume text")

class role(BaseModel):
    role_name: list[str] =Field(description="List of all the suitable roles")


# Hide the default tkinter window
root = Tk()
root.withdraw()

# Open file picker dialog
class ResumeDecoder:
    def __init__(self):
        
        self.file_path = filedialog.askopenfilename(title="Select a PDF", filetypes=[("PDF files", "*.pdf")])
        self.text = extract_text(self.file_path)
        self.model = ChatGroq(
            model="Qwen-2.5-32B",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

        self.roles = json.dumps(Roles.schema(), indent=2)
        self.roles = json.loads(self.roles)

        # Set up a parser + inject instructions into the prompt template.
        self.parser1 = JsonOutputParser(pydantic_object=resume)
        self.parser2 = JsonOutputParser(pydantic_object=role)

        self.prompt1 = PromptTemplate(
            template="you are given with a resume details classify the given text into this format \n{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": self.parser1.get_format_instructions()},
        )

        self.prompt2 = PromptTemplate(
            template="you are given with the resume details. list out the roles from the \n {roles} \n if role values match with the skills in resume details. output in this format  \n{format_instructions}\n resume:{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": self.parser2.get_format_instructions(),"roles":self.roles},
        )

        self.chain1 = self.prompt1 | self.model |  self.parser1
        self.chain2 = self.prompt2 | self.model |  self.parser2

    def model_chain1(self):
        return self.chain1

    def model_chain2(self):
        return self.chain2

    def response(self):
        print(self.text)
        k=self.chain1.invoke({"query": self.text})
        return k

    def response2(self):
        resume_details=self.response()
        k=self.chain2.invoke({"query": resume_details})
        return resume_details,k

resume_decoder = ResumeDecoder()
r,k = resume_decoder.response2()

for i in r.keys():
    print(i,r[i])
    print("_"*20)

print(k)