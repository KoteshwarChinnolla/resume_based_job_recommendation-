import heapq
from resume_decoder import ResumeDecoder
from pymongo import MongoClient
import itertools


class jobSort:
    def __init__(self,pdf_text):
        resume_decoder = ResumeDecoder(pdf_text)
        r,k = resume_decoder.response()

        r["roles"]=k["role_name"]
        client = MongoClient("mongodb+srv://Mithunlogin:12345@cluster0.nfdmggi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db = client["Growup"]
        collection = db["jobs"]
        self.company_roles = list(collection.find())

        self.resume_data = r
    def normalize(self,items):
        if isinstance(items, list):
            return set(i.strip().lower() for i in items)
        return items.strip().lower()

    def rank_companies(self):
        resume=self.resume_data
        company_roles=self.company_roles
        print(resume)
        resume_roles = self.normalize(resume["roles"])
        resume_skills = self.normalize(resume["major_skills"])
        resume_exp = resume["experience"]
        resume_loc = self.normalize(resume["city"])
        heap = []
        counter = itertools.count()

        for entry in company_roles:
            print(entry)
            job_roles = self.normalize(entry["role"])
            job_skills = self.normalize(entry["skills"])
            job_exp_from = int(entry["from_experience"])
            job_exp_to = int(entry["to_experience"])
            job_loc = self.normalize(entry["city"])

            matched_skills = resume_skills & job_skills
            matched_roles = resume_roles & set(job_roles)
            score = len(matched_skills)+ len(matched_roles)
            location_match = resume_loc == job_loc
            experience_match = resume_exp >= job_exp_from

            if location_match:
                score += 1
            if experience_match:
                score += 1

            if score > 0:
                print(f"Score: {score}, Company: {entry['company']}, Role: {entry['role']}")
                heapq.heappush(heap, (-score, entry["company"], entry["role"], next(counter), {
                    "matched_skills": list(matched_skills),
                    "location_match": location_match,
                    "experience_match": experience_match,
                    "total_score": score
                }))

        ranked = []
        i=6
        while (i>0) and heap:
            details_ = heapq.heappop(heap)
            # (-3, 'Nxtwave', 'Datascientist', 6, {'matched_skills': ['machine learning'], 'matched_roles': [], 'location_match': True, 'experience_match': True, 'total_score': 3}) 
            details = details_[4]
            company = details_[1]
            role = details_[2]
            ranked.append({
                "company": company,
                "role": role,
                **details
            })
            i-=1
        return ranked

    # ranked_list = rank_companies(resume_data, company_roles)


# job_sort=jobSort()
# ranked_list=job_sort.rank_companies()

# print("🎯 Priority-wise Suitable Companies and Roles:\n")
# for idx, item in enumerate(ranked_list, 1):
#     print(f"{idx}. {item['company']} - {item['role']}")
#     print(f"   Skills matched: {item['matched_skills']}")
#     print(f"   Roles matched: {item['matched_roles']}")
#     print(f"   Location match: {item['location_match']}")
#     print(f"   Experience match: {item['experience_match']}")
#     print(f"   Total Score: {item['total_score']}\n")