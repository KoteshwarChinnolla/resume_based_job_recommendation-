import os
from dotenv import load_dotenv
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from typing import Annotated, Literal, Dict, Any, List, Optional
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from chatbot.tools import tools
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
import json
from chatbot.job_search import JobSearch
from roles import Roles


load_dotenv()
# Set a default API key if not provided in environment
if os.getenv("GROQ_API_KEY") is None:
    os.environ["GROQ_API_KEY"] = "default_key_for_development"
else:
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

roles = json.dumps(Roles.schema(), indent=2)
roles = json.loads(roles)

class MessageState(TypedDict):
    messages:Annotated[list[AnyMessage],add_messages]

class Job(BaseModel):
    company: str
    job_description: str
    role: Literal[
        "MarketingTechnologist", "SEOSpecialist", "WebAnalyticsDeveloper", "DigitalMarketingManager", "SocialMediaManager",
        "GrowthHacker", "Content_Manager", "Content_Strategist", "InformationArchitect", "UX_Designer", "UI_Designer",
        "AccessibilitySpecialist", "InteractionDesigner", "FrontEndDesigner", "FrontEndDeveloper", "MobileDeveloper",
        "FullStackDeveloper", "SoftwareDeveloper", "WordPressDeveloper", "FrameworksSpecialist", "ReactDeveloper",
        "PythonDeveloper", "ThreeDDesigner", "ARVRDeveloper", "GameDeveloper", "AugmentedRealityDesigner",
        "VirtualRealityDesigner", "BusinessSystemsAnalyst", "SystemsEngineer", "SystemsAdministrator", "AIDeveloper",
        "AlgorithmEngineer", "MachineLearningEngineer", "DatabaseAdministrator", "DataArchitect", "DataModeler",
        "DataAnalyst", "DataScientist", "CloudArchitect", "TechnicalLead", "DevOpsManager", "AgileProjectManager",
        "ProductManager", "TechnicalAccountManager", "SecuritySpecialist", "QASpecialist", "ComputerGraphicsAnimator",
        "MobileAppDeveloper", "MobileAppDesigner"
    ]
    experience: int
    apply_link: str
    skills: list[str] 
    city: str
    state: str
    country:str
    expected_salary: int
    date: str
    job_type: str
    tech_nontech : Literal["tech", "non-tech"]

class build_graph:
    def _init_(self):

        t=tools()
        self.model=ChatGroq(model="qwen-2.5-32b")
        self.job_search=t.job_search
        self.internship_search=t.internship_search
        self.websearch=t.websearch
        self.about=t.about_us
        self.services=t.services
        self.memory=MemorySaver()

        self.tools_list=[self.job_search,self.internship_search,self.websearch,self.about,self.services]

        self.llm_with_tool=self.model.bind_tools(self.tools_list)

        self.jobs = json.dumps(Job.schema(), indent=2)
        self.jobs = json.loads(self.jobs)
        # print(self.jobs)

        self.builder=StateGraph(MessageState)

        self.builder.add_node("tool_calling_llm",self.tool_calling_llm)
        self.builder.add_node("tools", ToolNode(self.tools_list))

        self.builder.add_edge(START,"tool_calling_llm")
        self.builder.add_conditional_edges("tool_calling_llm",tools_condition,)
        self.builder.add_edge("tools","tool_calling_llm")

        # self.graph=self.builder.compile(checkpointer=self.memory)
        self.graph=self.builder.compile(checkpointer=self.memory)

    def graph_workflow():
        return self.graph

    def tool_calling_llm(self,state=MessageState):

        sys_msg = '''
        you are a chatbot for GrowUp organization. your task is to respond with the opertunities, paths, guidance, and resources available to the given user_input.
        you can use the tools to search for jobs, internships and services. you can also use about tool if response require companies information and can use web search tool for any current web information.
        to search for jobs and internships the json inputs must be in a specific format.

        1. Format to search for jobs / internships: {jobs}
        job search / internship search tool produces 2 outputs 1st represents matching jobs (jobs with any one or more parameter matched) and 2nd represents perfect match jobs (jobs with all the given parameters matched).
        
        2. input the about us tool with the related query, if the response require companies information like (Mission,Benefits,Vision,Commitment,Achievements)

        3. input the about us tool with the related query, the response require companies services like.

        4. ask websearch tool for any current information

        process required toll responses summarize for a perfect output. make relevant tool calls for faster response. provide to the point response dont make any tool calling errors.
        
        '''

        template = ChatPromptTemplate([
            ("system", sys_msg),
            ("human", "user_input:{user_input}"),
        ])

        chain = template | self.llm_with_tool
        answer = chain.invoke({"user_input":state["messages"][-1].content,"query":state["messages"][-1].content,"jobs":self.jobs})
        return {"messages" : answer}

    def process_job_result(self, job_data):
        """Convert job data to standardized format"""
        return {
            "company": job_data.get("company", ""),
            "role": job_data.get("role", ""),
            "experience_range": {
                "from": job_data.get("from_experience", 0),
                "to": job_data.get("to_experience", 0)
            },
            "salary_range": {
                "from": job_data.get("from_salary", 0),
                "to": job_data.get("to_salary", 0)
            },
            "location": {
                "city": job_data.get("city", ""),
                "state": job_data.get("state", ""),
                "country": job_data.get("country", "")
            },
            "apply_link": job_data.get("apply_link", "string"),
            "skills": job_data.get("skills", []),
            "date_posted": job_data.get("date", "string"),
            "job_type": job_data.get("job_type", "Full-time"),
            "category": job_data.get("tech_nontech", "string"),
            "description": job_data.get("job_description", "not mentioned"),
            "match_score": 1  # Default match score
        }

    def response(self,message,name,thread_id):
        config={"configurable":{"thread_id":thread_id}}
        messages=[HumanMessage(content=message,name=name)]
        response=self.graph.stream({"messages":messages},config=config,stream_mode="values")

        # Collect all messages
        all_messages = []
        for event in response:
            all_messages.append(event["messages"][-1])
        
        # Separate different types of messages
        ai_messages = [i for i in all_messages if str(type(i))=="<class 'langchain_core.messages.ai.AIMessage'>"]
        tool_messages = [i for i in all_messages if str(type(i))=="<class 'langchain_core.messages.tool.ToolMessage'>"]
        
        # Get the final AI response for conversational context
        ai_response = ai_messages[-1].content if ai_messages else "No response generated."
        
        # Process tool responses by type
        tool_responses = {}
        
        # Process tool calls and extract information about which tools were called
        if len(ai_messages) > 1:
            try:
                tools_called = ai_messages[-2].additional_kwargs.get("tool_calls", [])
                for tool_call in tools_called:
                    tool_name = tool_call["function"]["name"]
                    tool_args = tool_call["function"]["arguments"]
                    if tool_name not in tool_responses:
                        tool_responses[tool_name] = {"calls": [], "responses": []}
                    tool_responses[tool_name]["calls"].append(tool_args)
            except (KeyError, AttributeError, IndexError) as e:
                pass
        
        # Process tool response messages
        for tool_msg in tool_messages:
            tool_name = tool_msg.name if hasattr(tool_msg, 'name') else "Unknown Tool"
            if tool_name not in tool_responses:
                tool_responses[tool_name] = {"calls": [], "responses": []}
            tool_responses[tool_name]["responses"].append(tool_msg.content)
        
        # Create response JSON
        response_data = {
            "ai_response": ai_response,
            "tools": {}
        }
        
        # Add tool responses to the JSON
        for tool_name, data in tool_responses.items():
            if tool_name == "job_search" and data["responses"]:
                job_search_results = {"perfect_match_jobs": [], "matching_jobs": []}
                
                for resp in data["responses"]:
                    try:
                        if isinstance(resp, str):
                            resp_data = json.loads(resp)
                        else:
                            resp_data = resp
                        
                        # Add perfect match jobs
                        if "perfect_match_jobs" in resp_data and resp_data["perfect_match_jobs"]:
                            for job in resp_data["perfect_match_jobs"]:
                                job_search_results["perfect_match_jobs"].append(self.process_job_result(job))
                        
                        # Add matching jobs
                        if "matching_jobs" in resp_data and resp_data["matching_jobs"]:
                            for job in resp_data["matching_jobs"]:
                                job_search_results["matching_jobs"].append(self.process_job_result(job))
                    except (json.JSONDecodeError, AttributeError, TypeError) as e:
                        # Handle error but continue processing
                        pass
                
                # Add total counts and search criteria
                total_jobs = len(job_search_results["perfect_match_jobs"]) + len(job_search_results["matching_jobs"])
                job_search_results["total_results"] = total_jobs
                
                # Add calls info to extract search criteria
                search_criteria = {}
                if data["calls"]:
                    try:
                        for call in data["calls"]:
                            if isinstance(call, str):
                                call_data = json.loads(call)
                                for key, value in call_data.items():
                                    if value and key not in ["skills"]:
                                        search_criteria[key] = value
                    except:
                        pass
                
                job_search_results["search_criteria"] = search_criteria
                
                # Format the response according to the exact format required with only perfect matches
                response_data["tools"]["job_search"] = {
                    "total_results": len(job_search_results["perfect_match_jobs"]),
                    "jobs": job_search_results["perfect_match_jobs"],
                    "search_criteria": search_criteria
                }
            
            elif tool_name == "about_us" and data["responses"]:
                about_content = "\n".join(data["responses"])
                response_data["tools"]["about_us"] = about_content
            
            elif tool_name == "services" and data["responses"]:
                services_content = "\n".join(data["responses"])
                response_data["tools"]["services"] = services_content
            
            elif tool_name == "websearch" and data["responses"]:
                search_content = "\n".join(data["responses"])
                response_data["tools"]["websearch"] = search_content
            
            elif tool_name == "internship_search" and data["responses"]:
                internship_content = "\n".join(data["responses"])
                response_data["tools"]["internship_search"] = internship_content
        
        # If only job search results are requested and available, return only those
        if "job_search" in response_data["tools"] and message.lower().find("job") != -1:
            return json.loads(json.dumps(response_data["tools"]["job_search"], indent=2))
        
        # Otherwise return the full response
        return json.loads(json.dumps(response_data, indent=2))