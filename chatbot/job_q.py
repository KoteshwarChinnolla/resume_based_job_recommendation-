
import os
from dotenv import load_dotenv
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from typing import Annotated, Literal
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
os.environ["GROQ_API_KEY"]= os.getenv("GROQ_API_KEY")

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
    def __init__(self):

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

    def response(self,message,name,thread_id):
        config={"configurable":{"thread_id":thread_id}}
        messages=[HumanMessage(content=message,name=name)]
        # response=self.graph.invoke({"messages":messages})
        response=self.graph.stream({"messages":messages},config=config,stream_mode="values")

        last_chat=[]

        for event in response:
            last_chat.append(event["messages"][-1])
        AI_message=[i for i in last_chat if str(type(i))=="<class 'langchain_core.messages.ai.AIMessage'>"]
        Tool_message=[i for i in last_chat if str(type(i))=="<class 'langchain_core.messages.tool.ToolMessage'>"]
        tool_content=""
        for i in Tool_message:
            tool_content=i.content+"\n"
        process=""

        if len(AI_message)>1:
            tools_called=AI_message[-2].additional_kwargs["tool_calls"]
            for i in tools_called:
                process+="\n\n"+str(i["function"]["arguments"] + " \n\n " + str(i["function"]["name"]))

        AI_content=AI_message[-1].content

        # final_content=process+"\n\n"+tool_content+"\n\n"+AI_content
        
        return AI_content

# graph=build_graph()
# response=graph.response(input(),name="user",thread_id="1234")
# print(response)