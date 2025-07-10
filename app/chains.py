import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-8b-8192"
    )
    
    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}

            ### INSTRUCTION:
            You are an expert job posting extractor. The above content is scraped from a job listing website.

            Your task is to extract all relevant job postings from the text and return them in **strict JSON format**.

            Each JSON object must contain the following keys:
            - "role"
            - "experience"
            - "skills"
            - "description"

            Do NOT include any introduction, explanation, or preamble.  
            Respond with **JSON only** — not Markdown, not prose, just the JSON.  
            Do NOT use triple backticks or text like "Here is the JSON:"  
            If information is missing, use an empty string.

            ### OUTPUT FORMAT:
            [
            {{
                "role": "...",
                "experience": "...",
                "skills": "...",
                "description": "..."
            }},
            ...
            ]
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res,list) else [res]
    
    def write_mail(self,job,links):
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}
            
            ### INSTRUCTION:
            You are Keerthi, a passionate software engineer who builds smart, tailored solutions across AI, full-stack, and automation.
            Your goal is to write a cold email expressing interest in the job above, showcasing your ability to deliver impact using
            relevant projects from your resume.

            Add the most relevant (only one) link from the following links: {link_list}

            Keep it direct, professional, and focused on how you can help them.  
            No preamble.

            ### EMAIL (NO PREAMBLE):
            """
        )


        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link_list": links})
        return res.content
    
        
if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))