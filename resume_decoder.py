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
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class State(TypedDict):
    pdf_text: str
    resume: dict
    roles: list[str]


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
    schooling: str = Field(description="schooling from given resume text")
    tenth_marks: str = Field(description="tenth marks from given resume text")
    twelfth: str = Field(description="twelfth marks from given resume text")
    twelfth_marks: str = Field(description="twelfth marks from given resume text")
    graduation: str = Field(description="graduation from given resume text")
    percentage: str = Field(description="percentage from given resume text")
    field_of_study: str = Field(description="field of study from given resume text")
    projects: list[str]=Field(description="projects from given resume text")
    project_description: list[str]=Field(description="project description from given resume text")
    internships: list[str]=Field(description="internships from given resume text")
    certifications: list[str]=Field(description="certifications from given resume text")
    hobbies: list[str]=Field(description="hobbies from given resume text")
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
    def __init__(self, pdf_text):
        
        self.resume_text = pdf_text
        # self.file_path = filedialog.askopenfilename(title="Select a PDF file", filetypes=[("PDF files", "*.pdf")])
        
        self.model = ChatGroq(model="llama-3.3-70b-versatile")
        # self.model = ChatGroq(model="whisper-large-v3")


        self.roles = json.dumps(Roles.schema(), indent=2)
        self.roles = json.loads(self.roles)

        self.parser1 = JsonOutputParser(pydantic_object=resume)
        self.parser2 = JsonOutputParser(pydantic_object=role)

        self.prompt1 = PromptTemplate(
            template="you are given with a resume details classify the given text into this format \n{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": self.parser1.get_format_instructions()},
        )

        self.prompt2 = PromptTemplate(
            template="you are given with the resume details. list out the roles from the \n {roles} \n if role values match with the skills in resume details.just output in this format  \n{format_instructions} as it is json just output json. \n resume:{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": self.parser2.get_format_instructions(),"roles":self.roles},
        )

        self.chain1 = self.prompt1 | self.model |  self.parser1
        self.chain2 = self.prompt2 | self.model |  self.parser2

        graph_builder = StateGraph(State)
        # graph_builder.add_node("pdf_to_text", self.pdf_to_text)
        graph_builder.add_node("resume_response", self.resume_response)
        graph_builder.add_node("resume_roles", self.resume_roles)

        graph_builder.add_edge(START, "resume_response")
        graph_builder.add_edge("resume_response", "resume_roles")
        graph_builder.add_edge("resume_roles", END)

        self.graph = graph_builder.compile()
        # self.graph = graph_builder.compile(checkpointer=self.memory)
    def graph_workflow(self):
        return self.graph

    # def pdf_to_text(self, State:State):
    #     # Extract text from the PDF file
    #     text = extract_text(State["pdf_path"])
    #     return {"pdf_text": text}

    def model_chain1(self):
        return self.chain1

    def model_chain2(self):
        return self.chain2

    def resume_response(self,State:State):
        # print(self.text)
        k=self.chain1.invoke({"query": State["pdf_text"]})
        return {"resume": k}

    def resume_roles(self,State:State):
        k=self.chain2.invoke({"query": State["resume"]})
        return {"roles": k}

    def response(self):
        response=self.graph.stream({"pdf_text": self.resume_text},stream_mode="values")
        last_chat = []
        for event in response:
            if isinstance(event, dict):
                last_chat.append(event)
            else:
                print(event)
        return last_chat[-1]["resume"],last_chat[-1]["roles"]


# resume_decoder = ResumeDecoder("C:/Users/Chinnnolla Koteshwar/Downloads/koteshwar_chinnolla.pdf")
# k,r = resume_decoder.response()

# # for i in r.keys():
# #     print(i,r[i])
# #     print("_"*20)

# print(k)
# print("_"*20)
# print(r)