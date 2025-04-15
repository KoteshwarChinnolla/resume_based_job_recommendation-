from pymongo import MongoClient

class JobSearch:
    def __init__(self):
        client = MongoClient("mongodb+srv://Mithunlogin:12345@cluster0.nfdmggi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db = client['Growup']
        self.collections = db['jobs']
        self.results1 = []
        self.results2 = []

    def normalize(self,items):
        if isinstance(items, int):
            return items
        if isinstance(items, float):
            return items
        if isinstance(items, list):
            return set(i.strip().lower() for i in items)
        return items.strip().lower()

    def search(self, user_input):

        for key, value in user_input.items():
            user_input[key]=self.normalize(value)

        for job in self.collections.find():
            # print(job)
            matched = False
            not_matched = False
            common_skills = set()

            for key,value in job.items():
                if key=="_id":
                    continue
                job[key]=self.normalize(value)

            if "skills" in user_input:
                job_skills = set(job.get("skills"))
                common_skills = set(user_input["skills"]) & job_skills

                if common_skills:
                    matched = True
                else:
                    not_matched = True
            if "experience" in user_input:
                try:
                    if job.get("from_experience") <= user_input["experience"] <= job.get("to_experience"):
                        matched = True
                    else:
                        not_matched = True
                except TypeError:
                    print(f"Error: Experience values are not comparable for job {job.get('company')}")
                    self.collections.delete_one({"_id": job["_id"]})
                    continue

            if "expected_salary" in user_input:
                if job.get("from_salary") <= user_input["expected_salary"] <= job.get("to_salary"):
                    matched = True
                else:
                    not_matched = True

            if "state" in user_input:
                if user_input["state"] == job.get("state"):
                    matched = True
                else:
                    not_matched = True
            if "city" in user_input:
                if user_input["city"] == job.get("city"):
                    matched = True
                else:
                    not_matched = True

            if "country" in user_input:
                if user_input["country"] == job.get("country"):
                    matched = True
                else:
                    not_matched = True

            if "company" in user_input:

                if user_input["company"] == job.get("company"):
                    matched = True
                else:
                    not_matched = True

            if "role" in user_input:
                job_roles = job.get("role")
                user_role = user_input["role"]
                if job_roles in user_role:
                    matched = True
                else:
                    not_matched = True

            if "job_type" in user_input:
                if user_input["job_type"] == job.get("job_type"):
                    matched = True
                else:
                    not_matched = True

            if "tech_nontech" in user_input:
                if user_input["tech_nontech"] == job.get("tech_nontech"):
                    matched = True
                else:
                    not_matched = True

            if matched:
                job_result = {
                    "company": job.get("company"),
                    "role": job.get("role"),
                    "job_description": job.get("job_description"),
                    "experience_range": f"{job.get('from_experience')} - {job.get('to_experience')} years",
                    "salary_range": f"{job.get('from_salary')} - {job.get('to_salary')}",
                    "city": f"{job.get('city')}",
                    "state": f"{job.get('state')}", 
                    "country":f"{job.get('country')}",
                    "job_type": job.get("job_type"),
                    "tech_nontech": job.get("tech_nontech"),
                    "apply_link": job.get("apply_link"),
                    "date": job.get("date"),
                    "matched_skills": list(common_skills)
                }
                self.results1.append(job_result)
            if not_matched is False:
                job_perfect_match = {
                    "company": job.get("company"),
                    "role": job.get("role"),
                    "job_description": job.get("job_description"),
                    "experience_range": f"{job.get('from_experience')} - {job.get('to_experience')} years",
                    "salary_range": f"{job.get('from_salary')} - {job.get('to_salary')}",  
                    "city": f"{job.get('city')}",
                    "state": f"{job.get('state')}", 
                    "country":f"{job.get('country')}",
                    "job_type": job.get("job_type"),
                    "tech_nontech": job.get("tech_nontech"),
                    "apply_link": job.get("apply_link"),
                    "date": job.get("date"),
                    "matched_skills": list(common_skills)
                }
                self.results2.append(job_perfect_match)

        return self.results1[:3], self.results2[:3]

# user_input = {'company': 'Capgemini', 'city': 'Bangalore '}
# job_search = JobSearch()
# results1, results2 = job_search.search(user_input)

# if results1:
#     print("Matching Jobs Found:")
#     for i in results1:
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

# if results2:
#     print("*"*40)
#     print("Perfect Match Jobs Found:")
#     for i in results2:
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