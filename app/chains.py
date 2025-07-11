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
            no preamble, just the email content.
            ### JOB DESCRIPTION:
            {job_description}
            
            ### RELEVANT PORTFOLIO LINKS:
            {link_list}
            
            ### STRICT INSTRUCTIONS:
            Write a cold email for the job above following these rules:
            
            1. Start directly with the email content (no introductory text)
            2. Format must be:
            Subject: [Your Subject Here]
            
            [Email Body Here]
            
            [Your Signature]
            
            3. Must include:
            - Hyperlinked portfolio projects: [project name](URL)
            - Specific skills matching job requirements
            - Professional but enthusiastic tone
            
            4. DO NOT include:
            - Any text before "Subject:"
            - Markers like "--- BEGIN EMAIL ---"
            - Explanatory text about the email
            """
        )


        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link_list": links})
        return res.content
    
        
if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))