from collections import defaultdict
import json
# Original data

# Transform function
class JobDataTransformer:
  def transform_job_data(self,data):
      companies = defaultdict(lambda: {
          "name": None,
          "industry": None,
          "logo": None,
          "openings": []
      })

      final_data = {"IT":{"companies":[]}, "NonIT":{"companies":[]}}

      for job in data:
          company_name = job.get("company")
          company_type = job.get("tech_nontech")
          if not company_name:
              continue

          companies[company_name]["name"] = company_name
          companies[company_name]["logo"] = f"/logos/{company_name.lower()}.png"
          companies[company_name]["industry"] = "IT services" if company_type == "tech" else "Non-IT"

          opening = {
              "role": job.get("role") or None,
              "experience": f"{job.get('from_experience')} - {job.get("to_experience")} years",
              "location": job.get("city") or None,
              "salary": f"{job.get('from_salary')} - {job.get("to_salary")} LPA",
              "type": job.get("job_type") or None
          }

          companies[company_name]["openings"].append(opening)

      for company in companies.values():
          industry = company["industry"]
          if industry == "IT services":
              final_data["IT"]["companies"].append(company)
          else:
              final_data["NonIT"]["companies"].append(company)

      return final_data

# Run and print the result