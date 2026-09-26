import streamlit as st
import re
from collections import Counter
import google.generativeai as genai
from textblob import TextBlob

# ----------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------
st.set_page_config(page_title="Signal — AI Content Studio", page_icon="🎙️", layout="wide")

# ----------------------------------------------------------------------
# THEME — a small broadcast-studio identity: deep ink background,
# warm amber "on-air" accent, editorial serif for headings.
# ----------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600&display=swap');

:root {
  --bg: #FAF8F3;
  --surface: #FFFFFF;
  --surface-2: #F4F1E9;
  --accent: #B8722C;
  --accent-soft: rgba(184,114,44,0.10);
  --accent-ink: #FFFFFF;
  --teal: #2F8F82;
  --text: #201C16;
  --text-muted: #7A7266;
  --border: #E6E1D6;
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: var(--bg); color: var(--text); }
#MainMenu, footer { visibility: hidden; }

/* ---- Hero ---- */
.signal-hero {
  padding: 1.6rem 0 1.6rem 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1.6rem;
}
.signal-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  color: var(--accent);
  font-size: 0.82rem;
  font-weight: 500;
  margin-bottom: 0.7rem;
}
.signal-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 0 4px var(--accent-soft);
}
.signal-title {
  font-family: 'Fraunces', serif;
  font-size: 2.75rem;
  font-weight: 600;
  line-height: 1.05;
  margin: 0 0 0.55rem 0;
  color: var(--text);
}
.signal-sub {
  color: var(--text-muted);
  font-size: 1.02rem;
  max-width: 620px;
  line-height: 1.5;
}

/* ---- Tabs styled as a panel selector ---- */
.stTabs [data-baseweb="tab-list"] {
  gap: 4px;
  background: var(--surface);
  padding: 6px;
  border-radius: 10px;
  border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
  height: 44px;
  border-radius: 7px;
  color: var(--text-muted);
  font-weight: 500;
}
.stTabs [aria-selected="true"] {
  background: var(--accent-soft) !important;
  color: var(--accent) !important;
}
.stTabs [data-baseweb="tab-highlight"] { background: transparent; }

/* ---- Section labels inside tabs ---- */
.signal-label {
  font-family: 'Fraunces', serif;
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text);
  margin: 0.2rem 0 0.9rem 0;
}

/* ---- Buttons ---- */
.stButton>button {
  background: var(--accent);
  color: var(--accent-ink);
  border: none;
  border-radius: 8px;
  font-weight: 600;
  padding: 0.55rem 1.4rem;
  transition: background 0.15s ease;
}
.stButton>button:hover { background: #A0631F; color: var(--accent-ink); }
.stButton>button:active { background: #8C561B; }

/* ---- Output cards ---- */
.signal-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  border-radius: 10px;
  padding: 1.3rem 1.5rem;
  margin-top: 0.9rem;
  line-height: 1.6;
  white-space: pre-wrap;
  box-shadow: 0 1px 3px rgba(32,28,22,0.05);
}
.signal-card-teal { border-left-color: var(--teal); }
.signal-card-label {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  color: var(--accent);
  margin-bottom: 0.5rem;
  display: block;
}
.signal-card-teal .signal-card-label { color: var(--teal); }

/* ---- Inputs ---- */
.stTextInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
  background: var(--surface-2) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 1px var(--accent) !important;
}

/* ---- Metrics (text analysis) ---- */
[data-testid="stMetricValue"] {
  color: var(--accent);
  font-family: 'Fraunces', serif;
}
[data-testid="stMetricLabel"] { color: var(--text-muted); }

hr { border-color: var(--border); }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ----------------------------------------------------------------------
# API CLIENT
# ----------------------------------------------------------------------
def generate_response(prompt, temperature=0.7, top_p=1.0, max_tokens=500):
    """Single wrapper around the LLM API call used by every module."""
    # Reads the key from Streamlit Secrets only — set once in
    # Settings -> Secrets as GEMINI_API_KEY = "..."; no input box needed.
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return ("⚠️ No Gemini API key configured. Add GEMINI_API_KEY in this app's "
                "Streamlit Cloud Settings → Secrets.")
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
# HERO
# ----------------------------------------------------------------------
st.markdown("""
<div class="signal-hero">
  <div class="signal-eyebrow"><span class="signal-dot"></span> ASSIGNMENT 8 · PROMPT ENGINEERING</div>
  <div class="signal-title">Signal</div>
  <div class="signal-sub">A small studio for scripting content, planning an episode, and reading
  the room — built for Walchand Institute of Technology, Solapur.</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(
    ["Write", "Plan an episode", "Read the room", "Parameter lab"]
)

# ---------------- TAB 1: CONTENT GENERATION ----------------
with tab1:
    st.markdown('<div class="signal-label">Generate a poem, story, or social post</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        topic1 = st.text_input("Topic", key="topic1", placeholder="e.g. Climate Change")
    with col2:
        content_type = st.selectbox("Format", ["Poem", "Story", "Social Media Post"])
    if st.button("Generate", type="primary", key="btn1"):
        if topic1:
            with st.spinner("Writing..."):
                output = generate_content(topic1, content_type)
            st.markdown(
                f'<div class="signal-card"><span class="signal-card-label">{content_type.upper()}</span>{output}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.warning("Enter a topic first.")

# ---------------- TAB 2: PODCAST PLANNING ----------------
with tab2:
    st.markdown('<div class="signal-label">Plan a podcast episode</div>', unsafe_allow_html=True)
    topic2 = st.text_input("Topic", key="topic2", placeholder="e.g. Climate Change")
    if st.button("Plan episode", type="primary", key="btn2"):
        if topic2:
            with st.spinner("Producing..."):
                output = generate_podcast_plan(topic2)
            st.markdown(
                f'<div class="signal-card signal-card-teal"><span class="signal-card-label">EPISODE BRIEF</span>{output}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.warning("Enter a topic first.")

# ---------------- TAB 3: TEXT ANALYSIS ----------------
with tab3:
    st.markdown('<div class="signal-label">Sentiment & keyword extraction</div>', unsafe_allow_html=True)
    text_input = st.text_area("Text to analyze", height=150,
                               placeholder="Paste a paragraph, review, or comment here...",
                               label_visibility="collapsed")
    if st.button("Analyze", type="primary", key="btn3"):
        if text_input.strip():
            result = analyze_text(text_input)
            c1, c2, c3 = st.columns(3)
            c1.metric("Sentiment", result["sentiment"])
            c2.metric("Polarity", result["polarity_score"])
            c3.markdown(
                f'<span class="signal-card-label" style="color:var(--teal);">KEYWORDS</span>'
                f'{", ".join(result["keywords"]) if result["keywords"] else "—"}',
                unsafe_allow_html=True,
            )
        else:
            st.warning("Paste some text first.")

# ---------------- TAB 4: PARAMETER EXPERIMENTATION ----------------
with tab4:
    st.markdown('<div class="signal-label">Compare temperature & Top-P</div>', unsafe_allow_html=True)
    topic4 = st.text_input("Topic", key="topic4", placeholder="e.g. Climate Change")
    if st.button("Run comparison", type="primary", key="btn4"):
        if topic4:
            with st.spinner("Generating four variants..."):
                results = compare_parameters(topic4)
            cols = st.columns(2)
            for i, (label, output) in enumerate(results.items()):
                with cols[i % 2]:
                    st.markdown(
                        f'<div class="signal-card"><span class="signal-card-label">{label.upper()}</span>{output}</div>',
                        unsafe_allow_html=True,
                    )
        else:
            st.warning("Enter a topic first.")
