import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text

# — Streamlit page config (must be first)
st.set_page_config(
    layout="wide",
    page_title="Cold Email Generator",
    page_icon="⚡🤖",
)

# — Meta-style CSS Styling —
st.markdown("""
<style>
/* Prevent horizontal scrolling in code/expander */
.streamlit-expanderHeader, .streamlit-expanderContent { max-width: 100% !important; }
pre { white-space: pre-wrap !important; word-wrap: break-word !important; }

/* Title styling with glowing color */
.title {
    text-align: center;
    font-size: 3rem;
    font-weight: 700;
    margin: 1.5rem 0;
    color: #00f2ff;
    text-shadow: 2px 2px 6px rgba(0, 242, 255, 0.5);
}

/* Meta-style button with gradient and hover animation */
div.stButton > button:first-child {
    background: linear-gradient(45deg, #00f2ff, #4facfe) !important;
    color: #0f2027 !important;
    font-size: 1.2rem !important;
    font-weight: bold;
    padding: 0.6rem 1.2rem !important;
    border: none !important;
    border-radius: 0.4rem !important;
    transition: transform 0.2s ease-in-out;
}
div.stButton > button:first-child:hover {
    transform: scale(1.05);
    background: linear-gradient(45deg, #4facfe, #00f2ff) !important;
}
</style>
""", unsafe_allow_html=True)

# — Main Streamlit App Logic —
def create_streamlit_app(llm, portfolio, clean_text):
    # Stylish title
    st.markdown('<h1 class="title">⚡🤖 Cold Email Generator</h1>', unsafe_allow_html=True)

    # Input
    url_input = st.text_input(
        "Enter a Job Posting URL:",
        value="https://www.google.com/about/careers/applications/jobs/results/111007517923779270-software-engineer-university-graduate-2026"
    )
    submit_button = st.button("Generate ⚡")

    # On submit
    if submit_button:
        with st.spinner("🔄 Generating your cold email, please wait…"):
            # Load job posting content
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)

            # Load portfolio and extract jobs
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)

            for idx, job in enumerate(jobs, start=1):
                skills = job.get('skills', [])
                links = portfolio.query_links(skills)
                email = llm.write_mail(job, links)

                # Output email with wrapped text
                with st.expander(f"📧 Generated Email #{idx}", expanded=True):
                    st.text_area("", email, height=300, key=f"email_{idx}")

        st.success("✅ Cold email(s) generated!")

# — Entry point —
if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    create_streamlit_app(chain, portfolio, clean_text)
