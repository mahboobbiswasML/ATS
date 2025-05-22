def generate_summary(llm, resume_text):
    prompt = f"""
    Summarize this resume in 4-5 bullet points highlighting:
    - Key experience
    - Technical skills
    - Notable achievements
    - Education background
    - Overall strengths
    
    Resume:
    {resume_text}
    """
    response = llm.invoke(prompt)
    return response

def generate_insights(llm, resumes, job_description):
    prompt = f"""
    Analyze these resumes in the context of the following job description:
    {job_description}
    
    Provide key insights about:
    1. How well the candidates match the requirements
    2. Notable strengths and weaknesses
    3. Any patterns or interesting observations
    4. Recommendations for further evaluation
    
    For multiple resumes, compare them and highlight:
    - The strongest candidates overall
    - Best fit for specific requirements
    - Any missing skills across candidates
    
    Resumes to analyze:
    {"---".join(resumes)}
    """
    return llm.invoke(prompt)