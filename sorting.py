import heapq
from resume_decoder import ResumeDecoder
from pymongo import MongoClient

resume_decoder = ResumeDecoder()
class jobSort:
    def __init__(self):
        r,k = resume_decoder.response2()

        r["roles"]=k["role_name"]
        client = MongoClient("mongodb+srv://Mithunlogin:12345@cluster0.nfdmggi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db = client["Growup"]
        collection = db["jobs"]
        self.company_roles = list(collection.find())

        self.resume_data = r
    def normalize(items):
        if isinstance(items, list):
            return set(i.strip().lower() for i in items)
        return items.strip().lower()

    def rank_companies(resume, company_roles):
        print(resume)
        resume_roles = normalize(resume["roles"])
        resume_skills = normalize(resume["major_skills"])
        resume_exp = resume["experience"]
        resume_loc = normalize(resume["city"])
        heap = []

        for entry in company_roles:
            print(entry)
            job_roles = normalize(entry["role"])
            job_skills = normalize(entry["skills"])
            try:
                job_exp_from = int(entry["from_experience"])
                job_exp_to = int(entry["to_experience"])
            except ValueError:
                job_exp_from = 0
                job_exp_to = 0
            try:
                job_loc = normalize(entry["city"])
            except KeyError:
                job_loc = "hyderabad"  # Default location if not provided

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
                heapq.heappush(heap, (-score, entry["company"], entry["role"], {
                    "matched_skills": list(matched_skills),
                    "matched_roles": list(matched_roles),
                    "location_match": location_match,
                    "experience_match": experience_match,
                    "total_score": score
                }))

        ranked = []
        while heap:
            score, company, role, details = heapq.heappop(heap)
            ranked.append({
                "company": company,
                "role": role,
                **details
            })
        return ranked

    ranked_list = rank_companies(resume_data, company_roles)

    print("🎯 Priority-wise Suitable Companies and Roles:\n")
    for idx, item in enumerate(ranked_list, 1):
        print(f"{idx}. {item['company']} - {item['role']}")
        print(f"   Skills matched: {item['matched_skills']}")
        print(f"   Roles matched: {item['matched_roles']}")
        print(f"   Location match: {item['location_match']}")
        print(f"   Experience match: {item['experience_match']}")
        print(f"   Total Score: {item['total_score']}\n")