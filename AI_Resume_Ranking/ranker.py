import re
from langchain.prompts import PromptTemplate

rank_template = PromptTemplate(
    template="""
You are an expert recruiter analyzing a resume against a job description. 
Provide a score from 0-100 and a concise evaluation.

Job Description:
{role}

Resume:
{resume}

Format your response exactly as:
Score: <number between 0-100>
Evaluation: <3-4 sentence summary of fit>

Focus on:
- Relevant skills match
- Experience alignment
- Qualification gaps
- Overall suitability
""",
    input_variables=["resume", "role"]
)

def parse_score_response(response):
    result = {
        "Score": 0,
        "Evaluation": "No evaluation provided",
        "Overall Fit": "No evaluation provided"
    }
    
    # Extract score
    score_match = re.search(r"Score:\s*(\d+)", response)
    if score_match:
        result["Score"] = int(score_match.group(1))
    
    # Extract evaluation
    eval_match = re.search(r"Evaluation:(.*?)(?=\n[A-Za-z ]+:|$)", response, re.DOTALL)
    if eval_match:
        result["Evaluation"] = eval_match.group(1).strip()
        result["Overall Fit"] = result["Evaluation"]
    
    return result["Score"], result["Evaluation"]

def rank_all_resumes(llm, resumes, names, role):
    results = []
    for name, text in zip(names, resumes):
        prompt = rank_template.format(resume=text, role=role)
        response = llm.invoke(prompt)
        score, evaluation = parse_score_response(response)
        results.append({
            "Name": name,
            "Score": score,
            "Overall Fit": evaluation,
            "Resume": text
        })
    return results