# Resume Based job recommendation

**Project aims to recommend jobs based on the details provided in the resume.**
> the major features of the project include
> 1. classifying and mapping the details to the appropriate variables ( such as names, college, skills ...)
> 2. Fetches details from the database to compare it to the resume 
> 3. match percentage will be calculated according to the intersection in skills, experience, roles, ...
> 4. sort the jobs according to the match percentage.

## Run on your local system

> 1. clone the repository `git clone https://github.com/KoteshwarChinnolla/resume_based_job_recommendation-`
> 2. the `cd resume_based_job_recommendation-`
> 3. Create `.env` file
>    > 1. Add mongodb url ( create a cluster and get the url)
>    > 2. Add Groq API key

### Two ways of execution 

### 1. Docker 
**pre requisite** Docker engene on your system. 

> 1. start the docker Engene
> 2. Run `docker compose up --build` command

### 2. General
**pre requisite** python on your system 

> 1. open the project in command prompt.
> 2. Create a venv `python -m venv venv` or if you have anaconda `conds create -p venv python==3.12`
> 3. activate the venv enter this on command prompt `venv/Scripts/activate` ( check the path of the activate file inside venv) or if you have created the venv using conda then `conda activate ./venv`
> 4. Run `python app.py`

move to `http://localhost:8000/docs` on browser to access functionalitys

before going live on index.html which is in templates. you need to add data into mongodb to do that i have provided some sample data in the **sample.json** copy entire data and post it onto add_jobs section in `http://localhost:8000/docs` paste the data directly after clicking on add_jobs -> try now option.

then upload the resume in index.html to get the recommendations 

thank you 
ch Koteshwar
