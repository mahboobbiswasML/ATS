import streamlit as st
from resume_parser import extract_text
from rag_pipeline import build_vector_store, create_chatbot
from ranker import rank_all_resumes
from summarizer import generate_summary, generate_insights
from langchain.llms import Ollama
import pandas as pd
from ollama import Client
import time

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")
st.title("📄 AI Resume Analysis & Chat")

# Initialize session state variables
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'resume_texts' not in st.session_state:
    st.session_state.resume_texts = None
if 'resume_names' not in st.session_state:
    st.session_state.resume_names = None
if 'role_description' not in st.session_state:
    st.session_state.role_description = None
if 'vector_db' not in st.session_state:
    st.session_state.vector_db = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'ollama_error' not in st.session_state:
    st.session_state.ollama_error = False

def check_ollama_connection():
    try:
        client = Client(host='http://localhost:11434')
        client.list()  # Simple API call to check connection
        return True
    except:
        return False

# Sidebar for inputs
st.sidebar.header("Upload Resumes")
uploaded_files = st.sidebar.file_uploader("Upload PDF or DOCX resumes", type=["pdf", "docx"], accept_multiple_files=True)
role_description = st.sidebar.text_area("Paste Job Description", height=150)
analyze_button = st.sidebar.button("🔍 Analyze Candidates")

if uploaded_files:
    # Store extracted data in session state
    st.session_state.resume_texts = [extract_text(file) for file in uploaded_files]
    st.session_state.resume_names = [file.name for file in uploaded_files]
    st.session_state.role_description = role_description
    
    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["Ranking", "Insights", "Chat"])
    
    if analyze_button and role_description:
        # Clear previous error state
        st.session_state.ollama_error = False
        
        # Check Ollama connection
        if not check_ollama_connection():
            st.session_state.ollama_error = True
            st.error("Ollama server is not running. Please start Ollama and try again.")
        else:
            try:
                with st.spinner("Analyzing candidates..."):
                    llm = Ollama(model="llama2")
                    results = rank_all_resumes(llm, st.session_state.resume_texts, st.session_state.resume_names, role_description)
                    st.session_state.analysis_results = results
                    st.session_state.vector_db = build_vector_store(st.session_state.resume_texts)
                    st.session_state.ollama_error = False  # Success case
            except Exception as e:
                st.session_state.ollama_error = True
                st.error(f"Error during analysis: {str(e)}")
    
    # Display existing analysis results if available
    if st.session_state.analysis_results and not st.session_state.ollama_error:
        # Ranking Tab
        with tab1:
            st.subheader("📊 Candidate Ranking")
            df = pd.DataFrame(st.session_state.analysis_results)
            
            # Sort by Score descending and reset index
            df = df.sort_values("Score", ascending=False).reset_index(drop=True)
            
            # Add Eligibility column
            df['Eligibility'] = df['Score'].apply(lambda x: 'Yes' if x >= 50 else 'No')
            
            # Select and reorder columns
            display_df = df[['Name', 'Score', 'Eligibility', 'Overall Fit']]
            
            # Rename columns for better display
            display_df = display_df.rename(columns={
                'Overall Fit': 'Evaluation Summary'
            })
            
            st.dataframe(display_df,
                        use_container_width=True,
                        column_config={
                            "Score": st.column_config.ProgressColumn(
                                "Score",
                                help="Candidate's match score (0-100)",
                                format="%d",
                                min_value=0,
                                max_value=100,
                            ),
                            "Eligibility": st.column_config.TextColumn(
                                "Eligibility",
                                help="Meets minimum qualifications (Score ≥ 50)"
                            )
                        })
            
            if len(st.session_state.resume_names) > 1:
                st.subheader("🏆 Top Candidates")
                top_candidates = df.sort_values("Score", ascending=False).head(min(3, len(st.session_state.analysis_results)))
                for idx, candidate in top_candidates.iterrows():
                    with st.expander(f"{idx+1}. {candidate['Name']} (Score: {candidate['Score']})"):
                        st.write(generate_summary(llm, candidate["Resume"]))
        
        # Insights Tab
        with tab2:
            st.subheader("🔍 Key Insights")
            llm = Ollama(model="llama2")
            
            st.info("### Overall Insights")
            st.write(generate_insights(llm, st.session_state.resume_texts, st.session_state.role_description))
            
            st.info("### Individual Candidate Insights")
            for res in st.session_state.analysis_results:
                with st.expander(f"{res['Name']} (Score: {res['Score']})"):
                    st.write(generate_insights(llm, [res["Resume"]], st.session_state.role_description))
    
    # Chat Tab (always available)
    with tab3:
        st.subheader("💬 Chat with llama2")
        if st.session_state.vector_db and not st.session_state.ollama_error:
            try:
                chatbot = create_chatbot(st.session_state.vector_db)
                
                # Display chat messages from history
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                
                # Accept user input
                if prompt := st.chat_input("Ask about the resumes..."):
                    # Add user message to chat history
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    # Display user message
                    with st.chat_message("user"):
                        st.markdown(prompt)
                    
                    # Display assistant response
                    with st.chat_message("assistant"):
                        response = chatbot.run(prompt)
                        st.markdown(response)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Chat error: {str(e)}")
        else:
            st.info("Please analyze candidates first to enable chat")
else:
    st.info("Please upload resumes to begin analysis")