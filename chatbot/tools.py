from langchain_community.tools import DuckDuckGoSearchRun
from chatbot.job_search import JobSearch

JobSearch = JobSearch()
search = DuckDuckGoSearchRun()



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