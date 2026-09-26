```python
import html
import re
from collections import Counter

import streamlit as st
from google import genai
from google.genai import types
from textblob import TextBlob


# ==============================================================
# PAGE CONFIGURATION
# ==============================================================

st.set_page_config(
    page_title="Signal AI Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==============================================================
# CUSTOM CSS
# ==============================================================

CUSTOM_CSS = """
<style>

/* --------------------------------------------------------------
   GLOBAL
-------------------------------------------------------------- */

@import url(
    'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap'
);

:root {
    --bg: #f7f8fc;
    --surface: #ffffff;
    --surface-soft: #f1f3f8;
    --primary: #5b4cf6;
    --primary-dark: #4939df;
    --primary-soft: #eeecff;
    --green: #18a673;
    --orange: #e58a2b;
    --text: #171925;
    --muted: #73778a;
    --border: #e6e8ef;
    --shadow: 0 8px 30px rgba(30, 34, 60, 0.07);
}

html,
body,
[class*="css"] {
    font-family: "DM Sans", sans-serif;
}

.stApp {
    background: var(--bg);
    color: var(--text);
}

/* Hide Streamlit default elements */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    background: transparent !important;
}


/* --------------------------------------------------------------
   SIDEBAR
-------------------------------------------------------------- */

[data-testid="stSidebar"] {
    background: #15162a;
    border-right: none;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 1.5rem 1.1rem;
}

[data-testid="stSidebar"] * {
    color: #ffffff;
}

.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 35px;
}

.logo-icon {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: linear-gradient(
        135deg,
        #7568ff,
        #4d3de5
    );
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    box-shadow: 0 8px 22px rgba(91, 76, 246, 0.35);
}

.logo-title {
    font-size: 21px;
    font-weight: 700;
    letter-spacing: -0.4px;
}

.logo-subtitle {
    font-size: 11px;
    color: #9497ae !important;
    margin-top: 1px;
}

.sidebar-section {
    font-size: 11px;
    color: #777b98 !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-weight: 600;
    margin: 18px 0 9px 7px;
}

.sidebar-info {
    margin-top: 30px;
    padding: 15px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.07);
}

.sidebar-info-title {
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 5px;
}

.sidebar-info-text {
    color: #979ab0 !important;
    font-size: 11px;
    line-height: 1.5;
}


/* --------------------------------------------------------------
   MAIN HEADER
-------------------------------------------------------------- */

.main-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 26px;
}

.header-eyebrow {
    color: var(--primary);
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.3px;
    margin-bottom: 7px;
}

.header-title {
    font-family: "Playfair Display", serif;
    font-size: 39px;
    line-height: 1.1;
    font-weight: 600;
    letter-spacing: -1px;
    color: var(--text);
}

.header-description {
    color: var(--muted);
    font-size: 14px;
    margin-top: 8px;
    max-width: 650px;
    line-height: 1.6;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: #eaf9f2;
    color: #13855d;
    border: 1px solid #d2f0e2;
    border-radius: 20px;
    padding: 8px 13px;
    font-size: 11px;
    font-weight: 600;
}

.status-dot {
    width: 7px;
    height: 7px;
    background: #18a673;
    border-radius: 50%;
}


/* --------------------------------------------------------------
   FEATURE CARDS
-------------------------------------------------------------- */

.feature-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 13px;
    margin-bottom: 25px;
}

.feature-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 15px;
    padding: 17px;
    box-shadow: 0 3px 12px rgba(30, 34, 60, 0.03);
}

.feature-icon {
    width: 34px;
    height: 34px;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 11px;
    font-size: 17px;
}

.icon-purple {
    background: #eeecff;
}

.icon-blue {
    background: #e8f3ff;
}

.icon-green {
    background: #e8f8f1;
}

.icon-orange {
    background: #fff2e5;
}

.feature-title {
    font-size: 13px;
    font-weight: 700;
    color: var(--text);
}

.feature-text {
    color: var(--muted);
    font-size: 11px;
    line-height: 1.45;
    margin-top: 4px;
}


/* --------------------------------------------------------------
   WORKSPACE
-------------------------------------------------------------- */

.workspace {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 25px;
    box-shadow: var(--shadow);
}

.workspace-title {
    font-family: "Playfair Display", serif;
    font-size: 23px;
    font-weight: 600;
    color: var(--text);
}

.workspace-description {
    color: var(--muted);
    font-size: 12px;
    margin-top: 3px;
    margin-bottom: 20px;
}


/* --------------------------------------------------------------
   STREAMLIT TABS
-------------------------------------------------------------- */

.stTabs [data-baseweb="tab-list"] {
    gap: 5px;
    background: var(--surface-soft);
    padding: 5px;
    border-radius: 11px;
    border: 1px solid var(--border);
}

.stTabs [data-baseweb="tab"] {
    height: 42px;
    padding: 0 18px;
    border-radius: 8px;
    color: var(--muted);
    font-size: 12px;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background: var(--surface) !important;
    color: var(--primary) !important;
    box-shadow: 0 2px 7px rgba(30, 34, 60, 0.08);
}

.stTabs [data-baseweb="tab-highlight"] {
    background: transparent;
}


/* --------------------------------------------------------------
   FORM INPUTS
-------------------------------------------------------------- */

.stTextInput label,
.stTextArea label,
.stSelectbox label {
    color: var(--text) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
}

.stTextInput input,
.stTextArea textarea {
    background: #fafbfe !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    font-size: 13px !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px rgba(91, 76, 246, 0.10) !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background: #fafbfe !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}


/* --------------------------------------------------------------
   BUTTONS
-------------------------------------------------------------- */

.stButton > button {
    background: var(--primary);
    color: white;
    border: none;
    border-radius: 9px;
    min-height: 42px;
    padding: 0 22px;
    font-size: 12px;
    font-weight: 700;
    box-shadow: 0 5px 15px rgba(91, 76, 246, 0.20);
    transition: all 0.15s ease;
}

.stButton > button:hover {
    background: var(--primary-dark);
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 7px 18px rgba(91, 76, 246, 0.27);
}


/* --------------------------------------------------------------
   OUTPUT CARD
-------------------------------------------------------------- */

.output-card {
    background: #fafbfe;
    border: 1px solid var(--border);
    border-radius: 13px;
    padding: 20px;
    margin-top: 20px;
    line-height: 1.7;
    color: #343746;
    font-size: 13px;
    white-space: pre-wrap;
}

.output-header {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--primary);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    margin-bottom: 12px;
}

.output-line {
    width: 20px;
    height: 2px;
    background: var(--primary);
    border-radius: 2px;
}


/* --------------------------------------------------------------
   METRICS
-------------------------------------------------------------- */

[data-testid="stMetric"] {
    background: #fafbfe;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 13px;
}

[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-size: 11px !important;
}

[data-testid="stMetricValue"] {
    color: var(--primary) !important;
    font-family: "Playfair Display", serif;
}


/* --------------------------------------------------------------
   KEYWORD BOX
-------------------------------------------------------------- */

.keyword-box {
    background: #f1fbf7;
    border: 1px solid #d8f1e6;
    border-radius: 12px;
    padding: 15px;
    min-height: 73px;
}

.keyword-title {
    color: var(--green);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    margin-bottom: 8px;
}

.keyword-text {
    color: #26765d;
    font-size: 12px;
    line-height: 1.5;
}


/* --------------------------------------------------------------
   PARAMETER CARDS
-------------------------------------------------------------- */

.parameter-title {
    font-size: 11px;
    color: var(--muted);
    margin-bottom: 4px;
}

.parameter-value {
    color: var(--primary);
    font-size: 13px;
    font-weight: 700;
}


/* --------------------------------------------------------------
   FOOTER
-------------------------------------------------------------- */

.app-footer {
    text-align: center;
    color: #999daf;
    font-size: 10px;
    padding: 25px 0 5px 0;
}


/* --------------------------------------------------------------
   RESPONSIVE
-------------------------------------------------------------- */

@media (max-width: 900px) {
    .feature-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .header-title {
        font-size: 32px;
    }
}

</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==============================================================
# GEMINI API
# ==============================================================

def generate_response(
    prompt,
    temperature=0.7,
    top_p=1.0,
    max_tokens=1024,
):
    """
    Send a prompt to Gemini and return the generated response.
    """

    api_key = st.secrets.get("GEMINI_API_KEY", "")

    if not api_key:
        return (
            "⚠️ Gemini API key is not configured. "
            "Add GEMINI_API_KEY to Streamlit Secrets."
        )

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                top_p=top_p,
                max_output_tokens=max_tokens,
            ),
        )

        if response.text:
            return response.text.strip()

        return "⚠️ Gemini returned an empty response."

    except Exception as error:
        return f"⚠️ Gemini API error: {error}"


# ==============================================================
# PROMPT BUILDER
# ==============================================================

def build_structured_prompt(
    role,
    context,
    task,
    constraints,
    output_format,
):
    """
    Create a structured prompt for the LLM.
    """

    return f"""
Role:
{role}

Context:
{context}

Task:
{task}

Constraints:
{constraints}

Output Format:
{output_format}
""".strip()


# ==============================================================
# CONTENT GENERATION
# ==============================================================

def generate_content(topic, content_type):
    """
    Generate poem, story, or social media content.
    """

    role = (
        "You are a creative content writer skilled in "
        "storytelling, poetry, and digital content."
    )

    context = (
        f"The user wants engaging content about: {topic}."
    )

    if content_type == "Poem":

        task = (
            f"Write a rich and evocative poem with "
            f"8-12 stanzas about {topic}."
        )

    elif content_type == "Story":

        task = (
            f"Write a detailed short story of 600-900 words "
            f"about {topic}. Include a clear beginning, middle, "
            f"and ending."
        )

    else:

        task = (
            f"Write an engaging social media post under "
            f"280 characters about {topic}. Include suitable "
            f"hashtags."
        )

    constraints = (
        "Use simple language. Keep the content original. "
        "Avoid offensive or inappropriate content."
    )

    output_format = (
        "Return only the requested content. "
        "Do not include explanations."
    )

    prompt = build_structured_prompt(
        role,
        context,
        task,
        constraints,
        output_format,
    )

    return generate_response(
        prompt,
        temperature=0.8,
        max_tokens=1500,
    )


# ==============================================================
# PODCAST PLANNER
# ==============================================================

def generate_podcast_plan(topic):
    """
    Generate a complete podcast episode plan.
    """

    role = (
        "You are an experienced podcast producer and "
        "content strategist."
    )

    context = (
        f"Planning a new podcast episode about {topic}."
    )

    task = """
Generate:

1. A catchy podcast title.
2. A detailed 5-6 sentence episode description.
3. An ideal guest type/profile with a short rationale.
4. Eight thoughtful open-ended interview questions.
5. A one-sentence reason for asking each question.
"""

    constraints = (
        "Keep the tone professional, engaging, and conversational. "
        "Questions must be open-ended."
    )

    output_format = """
Title:
<episode title>

Description:
<episode description>

Guest Type:
<guest profile and rationale>

Questions:

1. <question>
Why: <reason>

2. <question>
Why: <reason>

3. <question>
Why: <reason>

4. <question>
Why: <reason>

5. <question>
Why: <reason>

6. <question>
Why: <reason>

7. <question>
Why: <reason>

8. <question>
Why: <reason>
"""

    prompt = build_structured_prompt(
        role,
        context,
        task,
        constraints,
        output_format,
    )

    return generate_response(
        prompt,
        temperature=0.7,
        max_tokens=1500,
    )


# ==============================================================
# TEXT ANALYSIS
# ==============================================================

def analyze_text(text):
    """
    Analyze sentiment and extract frequent keywords.
    """

    blob = TextBlob(text)

    polarity = blob.sentiment.polarity

    if polarity > 0.1:
        sentiment = "Positive"

    elif polarity < -0.1:
        sentiment = "Negative"

    else:
        sentiment = "Neutral"

    words = re.findall(
        r"\b[a-zA-Z]{4,}\b",
        text.lower(),
    )

    stopwords = {
        "this",
        "that",
        "with",
        "from",
        "have",
        "which",
        "their",
        "would",
        "about",
        "there",
        "these",
        "those",
        "been",
        "were",
        "they",
        "what",
        "when",
        "where",
        "your",
        "into",
        "than",
        "then",
        "also",
    }

    filtered_words = [
        word
        for word in words
        if word not in stopwords
    ]

    keywords = [
        word
        for word, _ in Counter(filtered_words).most_common(5)
    ]

    return {
        "sentiment": sentiment,
        "polarity_score": round(polarity, 3),
        "keywords": keywords,
    }


# ==============================================================
# PARAMETER EXPERIMENTATION
# ==============================================================

def compare_parameters(topic):
    """
    Generate the same prompt with different
    temperature and Top-P values.
    """

    prompt = (
        f"Write a short brand pitch of 3-4 sentences "
        f"for a brand related to {topic}."
    )

    configurations = [
        (
            "Low Temperature",
            "Temperature: 0.2",
            {
                "temperature": 0.2,
                "top_p": 1.0,
            },
        ),
        (
            "High Temperature",
            "Temperature: 1.0",
            {
                "temperature": 1.0,
                "top_p": 1.0,
            },
        ),
        (
            "Low Top-P",
            "Top-P: 0.3",
            {
                "temperature": 0.7,
                "top_p": 0.3,
            },
        ),
        (
            "High Top-P",
            "Top-P: 1.0",
            {
                "temperature": 0.7,
                "top_p": 1.0,
            },
        ),
    ]

    results = []

    for title, parameter, values in configurations:

        output = generate_response(
            prompt,
            max_tokens=400,
            **values,
        )

        results.append(
            {
                "title": title,
                "parameter": parameter,
                "output": output,
            }
        )

    return results


# ==============================================================
# SIDEBAR
# ==============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-logo">
            <div class="logo-icon">✦</div>

            <div>
                <div class="logo-title">Signal</div>
                <div class="logo-subtitle">
                    AI CONTENT STUDIO
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-section">Workspace</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="
            padding: 11px 12px;
            background: rgba(91,76,246,0.20);
            border-radius: 9px;
            color: #ffffff;
            font-size: 12px;
            font-weight: 600;
        ">
            ✦ AI Content Studio
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-section">Tools</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="
            color:#a5a8bb;
            font-size:12px;
            line-height:2.2;
            padding-left:8px;
        ">
            ✎ Content Writer<br>
            ◉ Podcast Planner<br>
            ◌ Text Analyzer<br>
            ⚙ Parameter Lab
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-info">
            <div class="sidebar-info-title">
                Assignment 8
            </div>

            <div class="sidebar-info-text">
                Prompt Engineering<br>
                Walchand Institute of Technology<br>
                Solapur
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================
# MAIN HEADER
# ==============================================================

st.markdown(
    """
    <div class="main-header">

        <div>
            <div class="header-eyebrow">
                AI CONTENT WORKSPACE
            </div>

            <div class="header-title">
                Create with Signal.
            </div>

            <div class="header-description">
                Write content, plan podcast episodes,
                analyze text, and experiment with LLM
                parameters in one simple workspace.
            </div>
        </div>

        <div>
            <div class="status-badge">
                <span class="status-dot"></span>
                AI STUDIO READY
            </div>
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ==============================================================
# FEATURE OVERVIEW
# ==============================================================

st.markdown(
    """
    <div class="feature-grid">

        <div class="feature-card">
            <div class="feature-icon icon-purple">✎</div>
            <div class="feature-title">
                Content Writer
            </div>
            <div class="feature-text">
                Generate poems, stories and social posts.
            </div>
        </div>

        <div class="feature-card">
            <div class="feature-icon icon-blue">◉</div>
            <div class="feature-title">
                Podcast Planner
            </div>
            <div class="feature-text">
                Build complete episode briefs and questions.
            </div>
        </div>

        <div class="feature-card">
            <div class="feature-icon icon-green">◌</div>
            <div class="feature-title">
                Text Analyzer
            </div>
            <div class="feature-text">
                Detect sentiment and extract keywords.
            </div>
        </div>

        <div class="feature-card">
            <div class="feature-icon icon-orange">⚙</div>
            <div class="feature-title">
                Parameter Lab
            </div>
            <div class="feature-text">
                Compare Temperature and Top-P outputs.
            </div>
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ==============================================================
# WORKSPACE
# ==============================================================

st.markdown(
    """
    <div class="workspace">
        <div class="workspace-title">
            AI Workspace
        </div>

        <div class="workspace-description">
            Select a tool below to get started.
        </div>
    """,
    unsafe_allow_html=True,
)


# ==============================================================
# TABS
# ==============================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "✎  Write",
        "◉  Podcast",
        "◌  Analyze",
        "⚙  Parameter Lab",
    ]
)


# ==============================================================
# TAB 1 — CONTENT GENERATOR
# ==============================================================

with tab1:

    st.markdown(
        "### Create content"
    )

    st.caption(
        "Choose a format and let Gemini create your content."
    )

    col1, col2 = st.columns(
        [2.2, 1],
        gap="medium",
    )

    with col1:

        topic1 = st.text_input(
            "Topic",
            placeholder="e.g. Climate Change",
            key="topic1",
        )

    with col2:

        content_type = st.selectbox(
            "Format",
            [
                "Poem",
                "Story",
                "Social Media Post",
            ],
            key="content_type",
        )

    if st.button(
        "✦ Generate Content",
        type="primary",
        key="generate_content",
        use_container_width=True,
    ):

        if topic1.strip():

            with st.spinner("Creating your content..."):

                output = generate_content(
                    topic1.strip(),
                    content_type,
                )

            safe_output = html.escape(output)

            st.markdown(
                f"""
                <div class="output-card">

                    <div class="output-header">
                        <span class="output-line"></span>
                        {content_type.upper()}
                    </div>

                    {safe_output}

                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.warning(
                "Please enter a topic first."
            )


# ==============================================================
# TAB 2 — PODCAST PLANNER
# ==============================================================

with tab2:

    st.markdown(
        "### Plan a podcast episode"
    )

    st.caption(
        "Generate an episode concept, guest profile and interview questions."
    )

    topic2 = st.text_input(
        "Episode topic",
        placeholder="e.g. The Future of Artificial Intelligence",
        key="topic2",
    )

    if st.button(
        "◉ Plan Episode",
        type="primary",
        key="plan_episode",
        use_container_width=True,
    ):

        if topic2.strip():

            with st.spinner(
                "Producing your episode brief..."
            ):

                output = generate_podcast_plan(
                    topic2.strip()
                )

            safe_output = html.escape(output)

            st.markdown(
                f"""
                <div class="output-card">

                    <div class="output-header">
                        <span class="output-line"></span>
                        EPISODE BRIEF
                    </div>

                    {safe_output}

                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.warning(
                "Please enter an episode topic."
            )


# ==============================================================
# TAB 3 — TEXT ANALYSIS
# ==============================================================

with tab3:

    st.markdown(
        "### Read the room"
    )

    st.caption(
        "Analyze sentiment and identify the most frequent keywords."
    )

    text_input = st.text_area(
        "Text",
        height=180,
        placeholder=(
            "Paste a paragraph, review, comment, "
            "or any text you want to analyze..."
        ),
        label_visibility="collapsed",
        key="analysis_text",
    )

    if st.button(
        "◌ Analyze Text",
        type="primary",
        key="analyze_text",
        use_container_width=True,
    ):

        if text_input.strip():

            result = analyze_text(
                text_input
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Sentiment",
                    result["sentiment"],
                )

            with col2:

                st.metric(
                    "Polarity Score",
                    result["polarity_score"],
                )

            with col3:

                keywords = (
                    ", ".join(result["keywords"])
                    if result["keywords"]
                    else "No keywords found"
                )

                st.markdown(
                    f"""
                    <div class="keyword-box">

                        <div class="keyword-title">
                            TOP KEYWORDS
                        </div>

                        <div class="keyword-text">
                            {html.escape(keywords)}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        else:

            st.warning(
                "Please paste some text first."
            )


# ==============================================================
# TAB 4 — PARAMETER LAB
# ==============================================================

with tab4:

    st.markdown(
        "### Experiment with LLM parameters"
    )

    st.caption(
        "Compare how Temperature and Top-P affect generated content."
    )

    topic4 = st.text_input(
        "Brand topic",
        placeholder="e.g. Sustainable Fashion",
        key="topic4",
    )

    if st.button(
        "⚙ Run Parameter Experiment",
        type="primary",
        key="run_parameters",
        use_container_width=True,
    ):

        if topic4.strip():

            with st.spinner(
                "Generating four parameter variants..."
            ):

                results = compare_parameters(
                    topic4.strip()
                )

            columns = st.columns(2)

            for index, result in enumerate(results):

                with columns[index % 2]:

                    safe_output = html.escape(
                        result["output"]
                    )

                    st.markdown(
                        f"""
                        <div class="output-card">

                            <div class="output-header">
                                <span class="output-line"></span>
                                {result["title"].upper()}
                            </div>

                            <div class="parameter-title">
                                Configuration
                            </div>

                            <div class="parameter-value">
                                {result["parameter"]}
                            </div>

                            <br>

                            {safe_output}

                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        else:

            st.warning(
                "Please enter a topic first."
            )


# ==============================================================
# CLOSE WORKSPACE
# ==============================================================

st.markdown(
    """
    </div>
    """,
    unsafe_allow_html=True,
)


# ==============================================================
# FOOTER
# ==============================================================

st.markdown(
    """
    <div class="app-footer">
        Signal AI Studio · Assignment 8 · Prompt Engineering
    </div>
    """,
    unsafe_allow_html=True,
)
```
