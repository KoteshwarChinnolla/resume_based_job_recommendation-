from langchain_community.tools import DuckDuckGoSearchRun
from job_search import JobSearch

JobSearch = JobSearch()
search = DuckDuckGoSearchRun()



class tools:
    def job_search(self,details:dict)->dict:
        """ search for jobs based on the details provided
        Args:
        details: input dictionary containing job search details in the dictionary format.
        output: result1 represent matching jobs (any one parameter can be matched) and result2 represent perfect match jobs (all the given parameters matched)
        """
        # print("job search")
        # print(details)
        # jobs={}
        result1,result2=JobSearch.search(user_input=details)

        # if result1:
        #     print("Matching Jobs Found:")
        #     for i in result1:
        #         print("\n---")
        #         print(f"Company: {i['company']}")
        #         print(f"Role: {', '.join(i['role'])}")
        #         print(f"Job Description: {i['job_description']}")
        #         print(f"Experience: {i['experience_range']}")
        #         print(f"Salary: {i['salary_range']}")
        #         print(f"state: {i['state']}")
        #         print(f"city: {i['city']}")
        #         print(f"country: {i['country']}")
        #         print(f"Job Type: {i['job_type']}")
        #         print(f"Tech/Non-Tech: {i['tech_nontech']}")
        #         print(f"Apply Link: {i['apply_link']}")
        #         print(f"Posted Date: {i['date']}")
        #         print(f"Matched Skills: {', '.join(i['matched_skills'])}")
        # else:
        #     print("Sorry, no matching jobs found.")

        # if result2:
        #     print("*"*40)
        #     print("Perfect Match Jobs Found:")
        #     for i in result2:
        #         print("\n---")
        #         print(f"Company: {i['company']}")
        #         print(f"Role: {', '.join(i['role'])}")
        #         print(f"Job Description: {i['job_description']}")
        #         print(f"Experience: {i['experience_range']}")
        #         print(f"Salary: {i['salary_range']}")
        #         print(f"state: {i['state']}")
        #         print(f"city: {i['city']}")
        #         print(f"country: {i['country']}")
        #         print(f"Job Type: {i['job_type']}")
        #         print(f"Tech/Non-Tech: {i['tech_nontech']}")
        #         print(f"Apply Link: {i['apply_link']}")
        #         print(f"Posted Date: {i['date']}")
        #         print(f"Matched Skills: {', '.join(i['matched_skills'])}")
        # else:
        #     print("Sorry, no perfect match jobs found.")

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