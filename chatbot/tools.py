from langchain_community.tools import DuckDuckGoSearchRun
from chatbot.job_search import JobSearch
JobSearch = JobSearch()
search = DuckDuckGoSearchRun()
from chatbot.vector_searchabout import VectorSearch_about
from chatbot.vector_searchsearvices import VectorSearch_services
import json
about = VectorSearch_about()
services = VectorSearch_services()
class tools:
    def job_search(self,details:dict)->dict:
        """ search for jobs based on the details provided
        Args:
        details: input dictionary containing job search details in the dictionary format.
        output: result1 represent matching jobs (any one parameter can be matched) and result2 represent perfect match jobs (all the given parameters matched)
        """
        print("jobs")
        print(json.dumps(details, indent=2))
        real_details = {}
        print("**************** ****************")
        for key, value in details.items():
            print(f"{key}: {value}")
            if value == "" or value == [] or value == {} or value == None:
                continue
            else:
                real_details[key] = value
        print("**************** ****************")
        print("real details")
        print(json.dumps(real_details, indent=2))
        try : 
            result1,result2=JobSearch.search(user_input=real_details)
            # print(result1,result2)
        except Exception as e:
            print(f"Error jobs: {e}")
            result1 = []
            result2 = []
        print(result1,result2)

        return {"matching_jobs":result1,"perfect_match_jobs":result2}

    def internship_search(self,details:dict)->dict:
        """ search for internships based on the details provided
        Args:
        details: dictionary of internship details
        """
        # print(details)
        internships={}
        # internships=InternshipSearch(details=details)
        return internships
    
    def websearch(self,search_info:str)-> str:
        """ search the web for a query
        Args:
        search_info: information to search for
        """
        # print(search_info)
        websearch=search.invoke(search_info)
        return websearch
    
    def about_us(self, query:str) -> str:
        """Search the vector database for information related to the organization's 'About Us' section.

        Args:
            query: A question or input specifically about the organization (e.g., mission, vision, background).

        Returns:
            A string containing the relevant text extracted from the vector search results.
        """
        print("about us")
        # print(query)
        try:
            results = about.search_documents(query)
            context = about.generate_answer(query, results)
        except Exception as e:
            print(f"Error: {e}")
            context = "Sorry, I couldn't retrieve the information at this time."
        # print(context)
        return context

    def services(self, query:str) -> str:
        """
        Search the vector database for service-related information based on the query.

        Args:
            query: The question or input about services of the organization.

        Returns:
            A string containing the retrieved and joined text content related to services.
        """
        print("services")
        # print(query)
        try:
            results = services.search_documents(query)
            context = about.generate_answer(query, results)
        except Exception as e:
            print(f"Error: {e}")
            context = "Sorry, I couldn't retrieve the information at this time."
        # print(context)
        # print(context)
        return context