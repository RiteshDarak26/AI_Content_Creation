import streamlit as st
import re
from collections import Counter
import google.generativeai as genai
from textblob import TextBlob

# ----------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------
st.set_page_config(page_title="AI Content Creation & Analysis System", page_icon="🎙️", layout="wide")

# ----------------------------------------------------------------------
# API CLIENT
# ----------------------------------------------------------------------
def generate_response(prompt, temperature=0.7, top_p=1.0, max_tokens=500):
    """Single wrapper around the LLM API call used by every module."""
    api_key = st.session_state.get("api_key", "")
    if not api_key:
        return "⚠️ Please enter your Gemini API key in the sidebar first."
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_tokens,
        ),
    )
    return response.text.strip()


# ----------------------------------------------------------------------
# 1. PROMPT DESIGN
# ----------------------------------------------------------------------
def build_structured_prompt(role, context, task, constraints, output_format):
    return f"""
Role: {role}
Context: {context}
Task: {task}
Constraints: {constraints}
Output Format: {output_format}
"""


# ----------------------------------------------------------------------
# 2. CONTENT GENERATION
# ----------------------------------------------------------------------
def generate_content(topic, content_type="Poem"):
    role = "You are a creative content writer skilled in storytelling and poetry."
    context = f"The user wants engaging content about the topic: {topic}."
    if content_type == "Poem":
        task = f"Write a short, evocative poem (4-6 stanzas) about {topic}."
    elif content_type == "Story":
        task = f"Write a short story (200-300 words) about {topic}."
    else:
        task = f"Write an engaging social media post (under 280 characters) about {topic}, including relevant hashtags."
    constraints = "Keep language simple, avoid offensive content, be original."
    output_format = "Return only the content, no extra commentary."
    prompt = build_structured_prompt(role, context, task, constraints, output_format)
    return generate_response(prompt, temperature=0.8)


# ----------------------------------------------------------------------
# 3. PODCAST PLANNING
# ----------------------------------------------------------------------
def generate_podcast_plan(topic):
    role = "You are an experienced podcast producer and content strategist."
    context = f"Planning a new podcast episode on the topic: {topic}."
    task = ("Generate: 1) A catchy podcast title, 2) A 2-3 sentence description, "
            "3) An ideal guest type/profile for this episode, "
            "4) Five thoughtful interview questions for the guest.")
    constraints = "Keep the tone professional yet conversational; questions should be open-ended."
    output_format = ("Return the result in this exact structure:\n"
                      "Title: <title>\nDescription: <description>\nGuest Type: <guest type>\n"
                      "Questions:\n1. ...\n2. ...\n3. ...\n4. ...\n5. ...")
    prompt = build_structured_prompt(role, context, task, constraints, output_format)
    return generate_response(prompt, temperature=0.7)


# ----------------------------------------------------------------------
# 4. TEXT ANALYSIS
# ----------------------------------------------------------------------
def analyze_text(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        sentiment = "Positive"
    elif polarity < -0.1:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    stopwords = {"this", "that", "with", "from", "have", "which", "their",
                 "would", "about", "there", "these", "those", "been", "were"}
    filtered = [w for w in words if w not in stopwords]
    keywords = [w for w, _ in Counter(filtered).most_common(5)]

    return {"sentiment": sentiment, "polarity_score": round(polarity, 3), "keywords": keywords}


# ----------------------------------------------------------------------
# 5. PARAMETER EXPERIMENTATION
# ----------------------------------------------------------------------
def compare_parameters(topic):
    prompt = f"Write a two-line tagline for a brand related to {topic}."
    configs = [
        ("Low Temp (0.2)", {"temperature": 0.2, "top_p": 1.0}),
        ("High Temp (1.0)", {"temperature": 1.0, "top_p": 1.0}),
        ("Low Top-P (0.3)", {"temperature": 0.7, "top_p": 0.3}),
        ("High Top-P (1.0)", {"temperature": 0.7, "top_p": 1.0}),
    ]
    results = {}
    for label, params in configs:
        results[label] = generate_response(prompt, **params)
    return results


# ----------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    st.session_state["api_key"] = st.text_input(
        "Gemini API Key", type="password",
        help="Get a free one at aistudio.google.com/apikey. "
             "For a public deploy, add it as a Streamlit secret instead (see README)."
    )
    st.caption("Your key is only used for this session and is never stored.")

st.title("🎙️ AI-Powered Content Creation & Analysis System")
st.caption("Prompt Engineering — Assignment 8 · Walchand Institute of Technology, Solapur")

tab1, tab2, tab3, tab4 = st.tabs(
    ["✍️ Content Generation", "🎧 Podcast Planning", "📊 Text Analysis", "🧪 Parameter Experimentation"]
)

# ---------------- TAB 1: CONTENT GENERATION ----------------
with tab1:
    st.subheader("Generate a poem, story, or social media post")
    col1, col2 = st.columns([2, 1])
    with col1:
        topic1 = st.text_input("Enter a topic", key="topic1", placeholder="e.g. Climate Change")
    with col2:
        content_type = st.selectbox("Content type", ["Poem", "Story", "Social Media Post"])
    if st.button("Generate Content", type="primary"):
        if topic1:
            with st.spinner("Generating..."):
                st.write(generate_content(topic1, content_type))
        else:
            st.warning("Please enter a topic.")

# ---------------- TAB 2: PODCAST PLANNING ----------------
with tab2:
    st.subheader("Plan a podcast episode")
    topic2 = st.text_input("Enter a topic", key="topic2", placeholder="e.g. Climate Change")
    if st.button("Generate Podcast Plan", type="primary"):
        if topic2:
            with st.spinner("Planning episode..."):
                st.markdown(generate_podcast_plan(topic2))
        else:
            st.warning("Please enter a topic.")

# ---------------- TAB 3: TEXT ANALYSIS ----------------
with tab3:
    st.subheader("Sentiment analysis & keyword extraction")
    text_input = st.text_area("Paste text to analyze", height=150,
                               placeholder="Paste a paragraph, review, or comment here...")
    if st.button("Analyze Text", type="primary"):
        if text_input.strip():
            result = analyze_text(text_input)
            c1, c2, c3 = st.columns(3)
            c1.metric("Sentiment", result["sentiment"])
            c2.metric("Polarity Score", result["polarity_score"])
            c3.write("**Top Keywords**")
            c3.write(", ".join(result["keywords"]) if result["keywords"] else "—")
        else:
            st.warning("Please enter some text.")

# ---------------- TAB 4: PARAMETER EXPERIMENTATION ----------------
with tab4:
    st.subheader("Compare temperature & Top-P settings")
    topic4 = st.text_input("Enter a topic", key="topic4", placeholder="e.g. Climate Change")
    if st.button("Run Comparison", type="primary"):
        if topic4:
            with st.spinner("Generating with different parameters..."):
                results = compare_parameters(topic4)
            for label, output in results.items():
                st.markdown(f"**{label}**")
                st.info(output)
        else:
            st.warning("Please enter a topic.")
