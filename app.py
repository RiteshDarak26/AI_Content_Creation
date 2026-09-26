import html
import re
from collections import Counter

import streamlit as st
from google import genai
from google.genai import types
from textblob import TextBlob


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Signal — AI Content Studio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap'
    );

    :root {
        --bg: #F7F8FC;
        --surface: #FFFFFF;
        --surface-soft: #F1F3F8;
        --primary: #5B4CF6;
        --primary-dark: #4939DF;
        --primary-soft: #EEECFF;
        --green: #18A673;
        --orange: #E58A2B;
        --text: #171925;
        --muted: #73778A;
        --border: #E5E7EF;
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

    #MainMenu,
    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }


    /* ================= SIDEBAR ================= */

    [data-testid="stSidebar"] {
        background: #15162A;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding: 1.5rem 1.1rem;
    }

    [data-testid="stSidebar"] * {
        color: #FFFFFF;
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
            #7568FF,
            #4D3DE5
        );
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        box-shadow:
            0 8px 22px rgba(91, 76, 246, 0.35);
    }

    .logo-title {
        font-size: 21px;
        font-weight: 700;
    }

    .logo-subtitle {
        font-size: 10px;
        color: #9497AE !important;
        letter-spacing: 0.8px;
    }

    .sidebar-section {
        font-size: 10px;
        color: #777B98 !important;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 600;
        margin: 18px 0 9px 7px;
    }

    .sidebar-tool {
        color: #A5A8BB !important;
        font-size: 12px;
        line-height: 2.2;
        padding-left: 8px;
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
        color: #979AB0 !important;
        font-size: 11px;
        line-height: 1.5;
    }


    /* ================= HERO ================= */

    .signal-hero {
        padding: 1.7rem 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1.5rem;
    }

    .signal-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.55rem;
        color: var(--primary);
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1.3px;
        margin-bottom: 0.65rem;
    }

    .signal-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--primary);
        box-shadow:
            0 0 0 4px var(--primary-soft);
    }

    .signal-title {
        font-family: "Playfair Display", serif;
        font-size: 3rem;
        font-weight: 600;
        line-height: 1.05;
        margin: 0 0 0.55rem 0;
        color: #171925 !important;
        letter-spacing: -1px;
    }

    .signal-sub {
        color: #73778A !important;
        font-size: 1rem;
        max-width: 700px;
        line-height: 1.6;
    }


    /* ================= STATUS ================= */

    .status-row {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 20px;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background: #EAF9F2;
        color: #13855D !important;
        border: 1px solid #D2F0E2;
        border-radius: 20px;
        padding: 7px 12px;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.4px;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        background: #18A673;
        border-radius: 50%;
    }


    /* ================= FEATURE CARDS ================= */

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
        box-shadow:
            0 3px 12px rgba(30, 34, 60, 0.03);
        transition: 0.15s ease;
    }

    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow:
            0 8px 20px rgba(30, 34, 60, 0.07);
    }

    .feature-icon {
        width: 35px;
        height: 35px;
        border-radius: 9px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 11px;
        font-size: 17px;
    }

    .icon-purple {
        background: #EEECFF;
    }

    .icon-blue {
        background: #E8F3FF;
    }

    .icon-green {
        background: #E8F8F1;
    }

    .icon-orange {
        background: #FFF2E5;
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


    /* ================= WORKSPACE ================= */

    .workspace {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 25px;
        box-shadow:
            0 8px 30px rgba(30, 34, 60, 0.07);
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


    /* ================= TABS ================= */

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
        background: #FFFFFF !important;
        color: var(--primary) !important;
        box-shadow:
            0 2px 7px rgba(30, 34, 60, 0.08);
    }


    /* ================= INPUTS ================= */

    .stTextInput label,
    .stTextArea label,
    .stSelectbox label {
        color: var(--text) !important;
        font-size: 12px !important;
        font-weight: 600 !important;
    }

    .stTextInput input,
    .stTextArea textarea {
        background: #FAFBFE !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        font-size: 13px !important;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #9A9EAF !important;
    }

    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--primary) !important;
        box-shadow:
            0 0 0 2px rgba(91, 76, 246, 0.10) !important;
    }

    .stSelectbox div[data-baseweb="select"] > div {
        background: #FAFBFE !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
    }


    /* ================= BUTTON FIX ================= */

    [data-testid="stButton"] button,
    .stButton button {
        background: #5B4CF6 !important;
        color: #FFFFFF !important;
        border: 1px solid #5B4CF6 !important;
        border-radius: 9px !important;
        min-height: 42px !important;
        padding: 0 22px !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        opacity: 1 !important;
        visibility: visible !important;
        box-shadow:
            0 5px 15px rgba(91, 76, 246, 0.20) !important;
    }

    [data-testid="stButton"] button *,
    .stButton button * {
        color: #FFFFFF !important;
        opacity: 1 !important;
        visibility: visible !important;
    }

    [data-testid="stButton"] button:hover,
    .stButton button:hover {
        background: #4939DF !important;
        color: #FFFFFF !important;
        border-color: #4939DF !important;
        transform: translateY(-1px);
        box-shadow:
            0 7px 18px rgba(91, 76, 246, 0.27) !important;
    }

    [data-testid="stButton"] button:focus,
    [data-testid="stButton"] button:active,
    .stButton button:focus,
    .stButton button:active {
        background: #4939DF !important;
        color: #FFFFFF !important;
        border-color: #4939DF !important;
    }


    /* ================= OUTPUT ================= */

    .output-card {
        background: #FAFBFE;
        border: 1px solid var(--border);
        border-left: 3px solid var(--primary);
        border-radius: 13px;
        padding: 20px;
        margin-top: 20px;
        line-height: 1.7;
        color: #343746;
        font-size: 13px;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
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


    /* ================= METRICS ================= */

    [data-testid="stMetric"] {
        background: #FAFBFE;
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


    /* ================= KEYWORDS ================= */

    .keyword-box {
        background: #F1FBF7;
        border: 1px solid #D8F1E6;
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
        color: #26765D;
        font-size: 12px;
        line-height: 1.5;
    }


    /* ================= FOOTER ================= */

    .app-footer {
        text-align: center;
        color: #999DAF;
        font-size: 10px;
        padding: 25px 0 5px 0;
    }


    /* ================= RESPONSIVE ================= */

    @media (max-width: 900px) {
        .feature-grid {
            grid-template-columns: repeat(2, 1fr);
        }

        .signal-title {
            font-size: 2.4rem;
        }
    }

    @media (max-width: 600px) {
        .feature-grid {
            grid-template-columns: 1fr;
        }

        .workspace {
            padding: 15px;
        }

        .signal-title {
            font-size: 2rem;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# GEMINI FUNCTION
# ============================================================

def generate_response(
    prompt,
    temperature=0.7,
    top_p=1.0,
    max_tokens=1024,
):

    api_key = st.secrets.get(
        "GEMINI_API_KEY",
        "",
    )

    if not api_key:
        return (
            "Gemini API key is not configured. "
            "Please add GEMINI_API_KEY to Streamlit Secrets."
        )

    try:

        client = genai.Client(
            api_key=api_key
        )

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

        return "Gemini returned an empty response."

    except Exception as error:

        return f"Gemini API error: {error}"


# ============================================================
# PROMPT BUILDER
# ============================================================

def build_prompt(
    role,
    context,
    task,
    constraints,
    output_format,
):

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


# ============================================================
# CONTENT GENERATOR
# ============================================================

def generate_content(
    topic,
    content_type,
):

    role = (
        "You are a professional creative content writer "
        "specialized in storytelling, poetry and social media."
    )

    context = (
        f"The requested content is about {topic}."
    )

    if content_type == "Poem":

        task = f"""
Write an original poem about {topic}.

Create 8 to 12 meaningful lines.
Use imagery and an engaging tone.
"""

    elif content_type == "Story":

        task = f"""
Write a short original story about {topic}.

The story should have:
- Beginning
- Middle
- Ending
- Main character
- Small conflict
- Resolution

Keep it between 500 and 700 words.
"""

    else:

        task = f"""
Create an engaging social media post about {topic}.

Keep it under 280 characters.
Add 3 to 5 relevant hashtags.
"""

    constraints = """
Use clear language.
Keep the content original.
Avoid offensive or inappropriate material.
"""

    output_format = """
Return only the requested content.
Do not provide explanations before or after it.
"""

    prompt = build_prompt(
        role,
        context,
        task,
        constraints,
        output_format,
    )

    return generate_response(
        prompt,
        temperature=0.8,
        top_p=0.95,
        max_tokens=1500,
    )


# ============================================================
# PODCAST PLANNER
# ============================================================

def generate_podcast_plan(topic):

    role = (
        "You are an experienced podcast producer "
        "and content strategist."
    )

    context = (
        f"The podcast episode is about {topic}."
    )

    task = f"""
Create a complete podcast episode plan about {topic}.

Include:

1. Catchy episode title.
2. Episode description.
3. Ideal guest profile.
4. Why this guest is suitable.
5. Eight open-ended interview questions.
6. A short reason for each question.
"""

    constraints = """
Keep the tone professional and conversational.
Questions should encourage detailed answers.
Avoid yes/no questions.
"""

    output_format = """
TITLE:
...

DESCRIPTION:
...

GUEST PROFILE:
...

WHY THIS GUEST:
...

INTERVIEW QUESTIONS:

1. Question
Reason:

2. Question
Reason:

3. Question
Reason:

4. Question
Reason:

5. Question
Reason:

6. Question
Reason:

7. Question
Reason:

8. Question
Reason:
"""

    prompt = build_prompt(
        role,
        context,
        task,
        constraints,
        output_format,
    )

    return generate_response(
        prompt,
        temperature=0.7,
        top_p=0.9,
        max_tokens=1800,
    )


# ============================================================
# TEXT ANALYSIS
# ============================================================

def analyze_text(text):

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
        "very",
        "will",
        "some",
        "more",
        "such",
        "only",
        "because",
    }

    filtered = [
        word
        for word in words
        if word not in stopwords
    ]

    keyword_counts = Counter(
        filtered
    ).most_common(5)

    keywords = [
        word
        for word, count in keyword_counts
    ]

    return {
        "sentiment": sentiment,
        "polarity": round(
            polarity,
            3,
        ),
        "keywords": keywords,
    }


# ============================================================
# PARAMETER EXPERIMENT
# ============================================================

def parameter_experiment(topic):

    prompt = f"""
Write a short 3-4 sentence brand pitch
for a brand related to {topic}.

Make it engaging and suitable for marketing.
"""

    configurations = [
        {
            "name": "Low Temperature",
            "parameter": "Temperature = 0.2",
            "temperature": 0.2,
            "top_p": 1.0,
        },
        {
            "name": "High Temperature",
            "parameter": "Temperature = 1.0",
            "temperature": 1.0,
            "top_p": 1.0,
        },
        {
            "name": "Low Top-P",
            "parameter": "Top-P = 0.3",
            "temperature": 0.7,
            "top_p": 0.3,
        },
        {
            "name": "High Top-P",
            "parameter": "Top-P = 1.0",
            "temperature": 0.7,
            "top_p": 1.0,
        },
    ]

    results = []

    for config in configurations:

        output = generate_response(
            prompt,
            temperature=config["temperature"],
            top_p=config["top_p"],
            max_tokens=400,
        )

        results.append(
            {
                "name": config["name"],
                "parameter": config["parameter"],
                "output": output,
            }
        )

    return results


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-logo">

            <div class="logo-icon">
                ✦
            </div>

            <div>
                <div class="logo-title">
                    Signal
                </div>

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
            color: #FFFFFF;
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
        <div class="sidebar-tool">
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


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="signal-hero">

        <div class="signal-eyebrow">
            <span class="signal-dot"></span>
            ASSIGNMENT 8 · PROMPT ENGINEERING
        </div>

        <div class="signal-title">
            Signal
        </div>

        <div class="signal-sub">
            A small studio for scripting content,
            planning an episode, and reading the room —
            built for Walchand Institute of Technology,
            Solapur.
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# STATUS
# ============================================================

st.markdown(
    """
    <div class="status-row">
        <div class="status-badge">
            <span class="status-dot"></span>
            AI STUDIO READY
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FEATURE CARDS
# ============================================================

st.markdown(
    """
    <div class="feature-grid">

        <div class="feature-card">
            <div class="feature-icon icon-purple">
                ✎
            </div>
            <div class="feature-title">
                Content Writer
            </div>
            <div class="feature-text">
                Generate poems, stories and
                social media posts.
            </div>
        </div>

        <div class="feature-card">
            <div class="feature-icon icon-blue">
                ◉
            </div>
            <div class="feature-title">
                Podcast Planner
            </div>
            <div class="feature-text">
                Build episode briefs and
                interview questions.
            </div>
        </div>

        <div class="feature-card">
            <div class="feature-icon icon-green">
                ◌
            </div>
            <div class="feature-title">
                Text Analyzer
            </div>
            <div class="feature-text">
                Analyze sentiment and
                extract keywords.
            </div>
        </div>

        <div class="feature-card">
            <div class="feature-icon icon-orange">
                ⚙
            </div>
            <div class="feature-title">
                Parameter Lab
            </div>
            <div class="feature-text">
                Experiment with Temperature
                and Top-P.
            </div>
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# WORKSPACE
# ============================================================

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


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "✎  Write",
        "◉  Podcast",
        "◌  Analyze",
        "⚙  Parameter Lab",
    ]
)


# ============================================================
# WRITE TAB
# ============================================================

with tab1:

    st.markdown("### Create content")

    st.caption(
        "Choose a format and generate content using Gemini."
    )

    col1, col2 = st.columns(
        [2.2, 1],
        gap="medium",
    )

    with col1:

        topic1 = st.text_input(
            "Topic",
            placeholder="e.g. Climate Change",
            key="content_topic",
        )

    with col2:

        content_type = st.selectbox(
            "Format",
            [
                "Poem",
                "Story",
                "Social Media Post",
            ],
            key="content_format",
        )

    if st.button(
        "✦ Generate Content",
        key="generate_content_button",
        use_container_width=True,
    ):

        if not topic1.strip():

            st.warning(
                "Please enter a topic first."
            )

        else:

            with st.spinner(
                "Creating your content..."
            ):

                result = generate_content(
                    topic1.strip(),
                    content_type,
                )

            st.markdown(
                f"""
                <div class="output-card">

                    <div class="output-header">
                        <span class="output-line"></span>
                        {content_type.upper()}
                    </div>

                    {html.escape(result)}

                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# PODCAST TAB
# ============================================================

with tab2:

    st.markdown(
        "### Plan a podcast episode"
    )

    st.caption(
        "Generate a title, description, guest profile and interview questions."
    )

    podcast_topic = st.text_input(
        "Episode topic",
        placeholder=(
            "e.g. The Future of Artificial Intelligence"
        ),
        key="podcast_topic",
    )

    if st.button(
        "◉ Plan Episode",
        key="podcast_button",
        use_container_width=True,
    ):

        if not podcast_topic.strip():

            st.warning(
                "Please enter an episode topic."
            )

        else:

            with st.spinner(
                "Producing your episode plan..."
            ):

                result = generate_podcast_plan(
                    podcast_topic.strip()
                )

            st.markdown(
                f"""
                <div class="output-card">

                    <div class="output-header">
                        <span class="output-line"></span>
                        EPISODE PLAN
                    </div>

                    {html.escape(result)}

                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# ANALYZE TAB
# ============================================================

with tab3:

    st.markdown(
        "### Read the room"
    )

    st.caption(
        "Analyze sentiment and identify important keywords."
    )

    analysis_text = st.text_area(
        "Text",
        height=190,
        placeholder=(
            "Paste a paragraph, review, comment, "
            "or any text you want to analyze..."
        ),
        label_visibility="collapsed",
        key="analysis_input",
    )

    if st.button(
        "◌ Analyze Text",
        key="analysis_button",
        use_container_width=True,
    ):

        if not analysis_text.strip():

            st.warning(
                "Please paste some text first."
            )

        else:

            result = analyze_text(
                analysis_text
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
                    result["polarity"],
                )

            with col3:

                keyword_text = (
                    ", ".join(
                        result["keywords"]
                    )
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
                            {html.escape(keyword_text)}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ============================================================
# PARAMETER LAB TAB
# ============================================================

with tab4:

    st.markdown(
        "### Experiment with LLM parameters"
    )

    st.caption(
        "Compare how Temperature and Top-P influence generated content."
    )

    parameter_topic = st.text_input(
        "Brand topic",
        placeholder="e.g. Sustainable Fashion",
        key="parameter_topic",
    )

    if st.button(
        "⚙ Run Parameter Experiment",
        key="parameter_button",
        use_container_width=True,
    ):

        if not parameter_topic.strip():

            st.warning(
                "Please enter a topic first."
            )

        else:

            with st.spinner(
                "Generating parameter variants..."
            ):

                results = parameter_experiment(
                    parameter_topic.strip()
                )

            columns = st.columns(2)

            for index, result in enumerate(results):

                with columns[index % 2]:

                    st.markdown(
                        f"""
                        <div class="output-card">

                            <div class="output-header">
                                <span class="output-line"></span>
                                {result["name"].upper()}
                            </div>

                            <div style="
                                color:#73778A;
                                font-size:11px;
                                margin-bottom:7px;
                            ">
                                Configuration
                            </div>

                            <div style="
                                color:#5B4CF6;
                                font-size:13px;
                                font-weight:700;
                                margin-bottom:14px;
                            ">
                                {result["parameter"]}
                            </div>

                            {html.escape(result["output"])}

                        </div>
                        """,
                        unsafe_allow_html=True,
                    )


# ============================================================
# CLOSE WORKSPACE
# ============================================================

st.markdown(
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="app-footer">
        Signal AI Studio · Assignment 8 · Prompt Engineering
    </div>
    """,
    unsafe_allow_html=True,
)
