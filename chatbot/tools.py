from langchain_community.tools import DuckDuckGoSearchRun
from chatbot.job_search import JobSearch

JobSearch = JobSearch()
search = DuckDuckGoSearchRun()
from chatbot.vector_searchabout import VectorSearch
from chatbot.vector_searchservices import VectorSearch
searcher = VectorSearch()
class tools:
    def job_search(self,details:dict)->dict:
        """ search for jobs based on the details provided
        Args:
        details: input dictionary containing job search details in the dictionary format.
        output: result1 represent matching jobs (any one parameter can be matched) and result2 represent perfect match jobs (all the given parameters matched)
        """
        print("job search")
        # print(details)
        # jobs={}
        result1,result2=JobSearch.search(user_input=details)

        return {"matching_jobs":result1,"perfect_match_jobs":result2}

    def internship_search(self,details:dict)->dict:
        """ search for internships based on the details provided
        Args:
        details: dictionary of internship details
        """
        print(details)
        internships={}
        # internships=InternshipSearch(details=details)
        return internships
    
    def websearch(self,search_info:str)-> str:
        """ search the web for a query
        Args:
        search_info: information to search for
        """
        websearch=search.invoke(search_info)
        return websearch
    
    def about_us(self, query) -> str:
        """Search the vector database for information related to the organization's 'About Us' section.

        Args:
            query: A user-provided question or input specifically about the organization (e.g., mission, vision, background).

        Returns:
            A string containing the relevant text extracted from the vector search results.
        """
        results = searcher.search_documents(query)
        context = "\n\n".join([res["text"] for res in results])
        return context

    def services(self, query) -> str:
        """
        Search the vector database for service-related information based on the query.

        Args:
            query: The user's question or input about services.

        Returns:
            A string containing the retrieved and joined text content related to services.
        """
        results = searcher.search_documents(query)
        context = "\n\n".join([res["text"] for res in results])
        return context