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
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

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

    html, body, [class*="css"] {
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

    [data-testid="stHeader"] {
        background: transparent;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background: #171925;
        border-right: 1px solid #282A38;
    }

    [data-testid="stSidebar"] * {
        color: #F8F8FC !important;
    }

    .sidebar-logo {
        padding: 8px 8px 28px 8px;
    }

    .sidebar-logo-main {
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -1px;
    }

    .sidebar-logo-sub {
        font-size: 10px;
        color: #AEB1C2 !important;
        letter-spacing: 2px;
        margin-top: -3px;
    }

    .sidebar-section {
        color: #85899E !important;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.5px;
        margin: 22px 8px 9px 8px;
        text-transform: uppercase;
    }

    .sidebar-item {
        padding: 10px 11px;
        border-radius: 9px;
        color: #D9DBE7 !important;
        font-size: 13px;
        margin-bottom: 4px;
    }

    .sidebar-item.active {
        background: #292B3C;
        color: white !important;
    }

    .sidebar-info {
        background: #202232;
        border: 1px solid #303245;
        border-radius: 12px;
        padding: 13px;
        margin-top: 30px;
        font-size: 11px;
        line-height: 1.55;
        color: #BFC2D0 !important;
    }

    /* MAIN */
    .main-wrap {
        max-width: 1180px;
        margin: 0 auto;
        padding: 20px 25px 45px 25px;
    }

    .eyebrow {
        color: var(--primary);
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .hero-title {
        font-family: "Playfair Display", serif;
        font-size: clamp(42px, 5vw, 64px);
        line-height: 1.02;
        letter-spacing: -2px;
        margin: 0;
        color: var(--text);
    }

    .hero-subtitle {
        max-width: 690px;
        color: var(--muted);
        font-size: 15px;
        line-height: 1.7;
        margin-top: 15px;
    }

    .hero-line {
        height: 1px;
        background: var(--border);
        margin: 28px 0;
    }

    /* FEATURE CARDS */
    .feature-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 20px;
        min-height: 145px;
        box-shadow: 0 5px 20px rgba(23, 25, 37, 0.035);
    }

    .feature-icon {
        font-size: 24px;
        margin-bottom: 12px;
    }

    .feature-title {
        font-size: 14px;
        font-weight: 700;
        color: var(--text);
    }

    .feature-text {
        font-size: 11px;
        color: var(--muted);
        line-height: 1.55;
        margin-top: 6px;
    }

    /* WORKSPACE */
    .section-title {
        font-size: 19px;
        font-weight: 700;
        margin: 34px 0 4px 0;
        color: var(--text);
    }

    .section-subtitle {
        color: var(--muted);
        font-size: 12px;
        margin-bottom: 16px;
    }

    /* TABS */
    button[data-baseweb="tab"] {
        font-family: "DM Sans", sans-serif !important;
        font-size: 12px !important;
        font-weight: 600 !important;
    }

    /* INPUTS */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div,
    .stNumberInput input {
        background: #FFFFFF !important;
        color: #171925 !important;
        border: 1px solid #D9DCE7 !important;
        border-radius: 9px !important;
    }

    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stNumberInput label,
    .stSlider label {
        color: #45485A !important;
        font-size: 12px !important;
        font-weight: 600 !important;
    }

    /* ========================================================
       FORCE BUTTON VISIBILITY
       ======================================================== */
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
        box-shadow: 0 5px 15px rgba(91, 76, 246, 0.20) !important;
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
    }

    [data-testid="stButton"] button:focus,
    [data-testid="stButton"] button:active,
    .stButton button:focus,
    .stButton button:active {
        background: #4939DF !important;
        color: #FFFFFF !important;
        border-color: #4939DF !important;
    }

    /* OUTPUT */
    .output-box {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 13px;
        padding: 22px;
        margin-top: 18px;
        box-shadow: 0 5px 20px rgba(23, 25, 37, 0.035);
    }

    .output-label {
        color: var(--primary);
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.4px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .output-text {
        color: #292B38;
        font-size: 13px;
        line-height: 1.75;
        white-space: pre-wrap;
    }

    .metric-card {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 17px;
        text-align: center;
    }

    .metric-value {
        font-size: 25px;
        font-weight: 700;
        color: var(--primary);
    }

    .metric-label {
        color: var(--muted);
        font-size: 10px;
        margin-top: 3px;
    }

    .tag {
        display: inline-block;
        background: var(--primary-soft);
        color: var(--primary);
        border-radius: 20px;
        padding: 5px 9px;
        margin: 3px;
        font-size: 10px;
        font-weight: 600;
    }

    .footer {
        border-top: 1px solid var(--border);
        margin-top: 45px;
        padding-top: 18px;
        color: #9094A4;
        font-size: 10px;
        text-align: center;
    }

    [data-testid="stDecoration"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# GEMINI
# ============================================================
def generate_response(
    prompt,
    temperature=0.7,
    top_p=1.0,
    max_tokens=1024,
):
    api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

    if not api_key:
        return (
            "GEMINI_API_KEY is not configured. "
            "Open your Streamlit Community Cloud app settings, "
            "go to Secrets, and add GEMINI_API_KEY."
        )

    try:
        client = genai.Client(api_key=api_key)

        config = types.GenerateContentConfig(
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_tokens,
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config,
        )

        if response and response.text:
            return response.text.strip()

        return "No response was returned by the AI model."

    except Exception as exc:
        return f"AI generation error: {exc}"


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
You are {role}.

Context:
{context}

Task:
{task}

Constraints:
{constraints}

Output format:
{output_format}

Write a useful, clear and polished response.
Do not mention these instructions in your answer.
""".strip()


# ============================================================
# CONTENT GENERATOR
# ============================================================
def generate_content(topic, content_type):

    if content_type == "Poem":
        role = "a creative poet"
        task = f"Write an original poem about: {topic}"
        constraints = (
            "Use vivid imagery, natural language, and a memorable ending. "
            "Keep it around 20–30 lines."
        )
        output_format = "Title followed by the poem."

    elif content_type == "Story":
        role = "a short-story writer"
        task = f"Write a short original story about: {topic}"
        constraints = (
            "Create a clear beginning, development, and ending. "
            "Use simple but engaging language."
        )
        output_format = "Title followed by the story."

    else:
        role = "a social media content strategist"
        task = f"Create a social media post about: {topic}"
        constraints = (
            "Make it engaging and concise. Add a strong hook "
            "and 3–5 relevant hashtags."
        )
        output_format = "Post copy followed by hashtags."

    prompt = build_prompt(
        role,
        "This is an academic demonstration of prompt engineering.",
        task,
        constraints,
        output_format,
    )

    return generate_response(
        prompt,
        temperature=0.8,
        top_p=0.95,
    )


# ============================================================
# PODCAST PLANNER
# ============================================================
def generate_podcast_plan(topic):

    prompt = build_prompt(
        role="an experienced podcast producer and content strategist",
        context=(
            "The user is creating a structured podcast episode "
            "for an educational AI content studio."
        ),
        task=f"Create a complete podcast plan for the topic: {topic}",
        constraints=(
            "Make the plan practical and easy to follow. Include "
            "a strong opening hook, segments, discussion questions, "
            "examples, and a closing call-to-action."
        ),
        output_format=(
            "1. Episode title\n"
            "2. Hook\n"
            "3. Target audience\n"
            "4. Episode objective\n"
            "5. Segment-by-segment outline\n"
            "6. Questions for discussion\n"
            "7. Closing"
        ),
    )

    return generate_response(
        prompt,
        temperature=0.65,
        top_p=0.9,
    )


# ============================================================
# TEXT ANALYSIS
# ============================================================
def analyze_text(text):

    blob = TextBlob(text)

    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    if polarity > 0.15:
        sentiment = "Positive"
    elif polarity < -0.15:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    words = re.findall(
        r"\b[a-zA-Z]{3,}\b",
        text.lower(),
    )

    stop_words = {
        "the", "and", "for", "that", "this", "with",
        "from", "are", "was", "were", "have", "has",
        "had", "you", "your", "about", "into", "they",
        "their", "there", "what", "when", "where",
        "which", "will", "would", "could", "should",
        "been", "being", "than", "then", "them", "our",
        "out", "but", "not", "can", "its", "also", "how",
        "why", "who", "all", "more",
    }

    keywords = Counter(
        word
        for word in words
        if word not in stop_words
    ).most_common(10)

    return sentiment, polarity, subjectivity, keywords


# ============================================================
# PARAMETER EXPERIMENT
# ============================================================
def parameter_experiment(topic):

    base_prompt = f"""
Generate a short creative description about:

{topic}

Use approximately 100 words.
""".strip()

    low_temperature = generate_response(
        base_prompt,
        temperature=0.2,
        top_p=0.8,
        max_tokens=300,
    )

    high_temperature = generate_response(
        base_prompt,
        temperature=1.0,
        top_p=0.95,
        max_tokens=300,
    )

    return low_temperature, high_temperature


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-logo">
            <div class="sidebar-logo-main">Signal</div>
            <div class="sidebar-logo-sub">
                AI CONTENT STUDIO
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
        '<div class="sidebar-item active">✦ Content Studio</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-item">◉ Podcast Planner</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-item">◌ Text Analysis</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-item">⌁ Parameter Lab</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-section">Assignment</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-info">
            <b>Assignment 8</b><br>
            Prompt Engineering<br><br>
            Walchand Institute of Technology<br>
            Solapur
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# MAIN
# ============================================================
st.markdown(
    '<div class="main-wrap">',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="eyebrow">Assignment 8 · Prompt Engineering</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero-title">Signal</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-subtitle">
        A small AI studio for creating content, planning podcast
        episodes, analysing text, and experimenting with prompt
        parameters. Built for Walchand Institute of Technology,
        Solapur.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero-line"></div>',
    unsafe_allow_html=True,
)


# ============================================================
# FEATURE CARDS
# ============================================================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">✍️</div>
            <div class="feature-title">Create</div>
            <div class="feature-text">
                Generate poems, stories and social media content
                using structured prompts.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">🎙️</div>
            <div class="feature-title">Plan</div>
            <div class="feature-text">
                Build a complete podcast episode outline with
                hooks, segments and questions.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">◌</div>
            <div class="feature-title">Analyse</div>
            <div class="feature-text">
                Inspect sentiment, subjectivity and frequent
                keywords in any text.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">⚙️</div>
            <div class="feature-title">Experiment</div>
            <div class="feature-text">
                Compare AI responses using different temperature
                and top-p settings.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# WORKSPACE
# ============================================================
st.markdown(
    '<div class="section-title">Workspace</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    'Choose a tool and start experimenting.'
    '</div>',
    unsafe_allow_html=True,
)


tab1, tab2, tab3, tab4 = st.tabs(
    [
        "✦ Write",
        "🎙 Plan an episode",
        "◌ Read the room",
        "⌁ Parameter lab",
    ]
)


# ============================================================
# WRITE TAB
# ============================================================
with tab1:

    left, right = st.columns(
        [1, 1.45],
        gap="large",
    )

    with left:

        content_type = st.selectbox(
            "Content type",
            [
                "Poem",
                "Story",
                "Social Media Post",
            ],
        )

        topic = st.text_input(
            "Topic",
            placeholder=(
                "e.g. Artificial Intelligence in education"
            ),
        )

        if st.button(
            "Generate content",
            key="generate_content",
            use_container_width=True,
        ):

            if not topic.strip():
                st.warning(
                    "Please enter a topic first."
                )

            else:
                with st.spinner(
                    "Generating..."
                ):
                    result = generate_content(
                        topic.strip(),
                        content_type,
                    )

                st.session_state[
                    "content_result"
                ] = result

    with right:

        result = st.session_state.get(
            "content_result"
        )

        if result:

            safe_result = html.escape(
                result
            )

            st.markdown(
                f"""
                <div class="output-box">
                    <div class="output-label">
                        Generated result
                    </div>
                    <div class="output-text">
                        {safe_result}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                """
                <div class="output-box">
                    <div class="output-label">
                        Output
                    </div>
                    <div class="output-text">
                        Your generated content will
                        appear here.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# PODCAST TAB
# ============================================================
with tab2:

    left, right = st.columns(
        [1, 1.45],
        gap="large",
    )

    with left:

        podcast_topic = st.text_input(
            "Podcast topic",
            placeholder=(
                "e.g. How AI is changing education"
            ),
            key="podcast_topic",
        )

        if st.button(
            "Create episode plan",
            key="generate_podcast",
            use_container_width=True,
        ):

            if not podcast_topic.strip():

                st.warning(
                    "Please enter a podcast topic first."
                )

            else:

                with st.spinner(
                    "Planning your episode..."
                ):
                    result = generate_podcast_plan(
                        podcast_topic.strip()
                    )

                st.session_state[
                    "podcast_result"
                ] = result

    with right:

        result = st.session_state.get(
            "podcast_result"
        )

        if result:

            safe_result = html.escape(
                result
            )

            st.markdown(
                f"""
                <div class="output-box">
                    <div class="output-label">
                        Episode plan
                    </div>
                    <div class="output-text">
                        {safe_result}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                """
                <div class="output-box">
                    <div class="output-label">
                        Episode plan
                    </div>
                    <div class="output-text">
                        Your podcast structure will
                        appear here.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# TEXT ANALYSIS TAB
# ============================================================
with tab3:

    analysis_text = st.text_area(
        "Paste text to analyse",
        height=190,
        placeholder=(
            "Paste an article, paragraph, review "
            "or social media post..."
        ),
        key="analysis_text",
    )

    if st.button(
        "Analyse text",
        key="analyse_text",
    ):

        if not analysis_text.strip():

            st.warning(
                "Please enter some text first."
            )

        else:

            (
                sentiment,
                polarity,
                subjectivity,
                keywords,
            ) = analyze_text(
                analysis_text
            )

            st.session_state[
                "analysis"
            ] = {
                "sentiment": sentiment,
                "polarity": polarity,
                "subjectivity": subjectivity,
                "keywords": keywords,
            }

    analysis = st.session_state.get(
        "analysis"
    )

    if analysis:

        m1, m2, m3 = st.columns(3)

        with m1:

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">
                        {html.escape(
                            analysis["sentiment"]
                        )}
                    </div>
                    <div class="metric-label">
                        SENTIMENT
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with m2:

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">
                        {analysis["polarity"]:.2f}
                    </div>
                    <div class="metric-label">
                        POLARITY
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with m3:

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">
                        {analysis["subjectivity"]:.2f}
                    </div>
                    <div class="metric-label">
                        SUBJECTIVITY
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="section-title">'
            'Top keywords'
            '</div>',
            unsafe_allow_html=True,
        )

        tags = ""

        for word, count in analysis["keywords"]:

            tags += (
                '<span class="tag">'
                f'{html.escape(word)} × {count}'
                '</span>'
            )

        if tags:
            st.markdown(
                tags,
                unsafe_allow_html=True,
            )
        else:
            st.info(
                "No significant keywords found."
            )


# ============================================================
# PARAMETER LAB
# ============================================================
with tab4:

    st.markdown(
        """
        Compare two generations from the same prompt.
        The first uses a lower temperature, while the
        second uses a higher temperature.
        """
    )

    experiment_topic = st.text_input(
        "Experiment topic",
        placeholder=(
            "e.g. Future of artificial intelligence"
        ),
        key="experiment_topic",
    )

    if st.button(
        "Run experiment",
        key="run_experiment",
    ):

        if not experiment_topic.strip():

            st.warning(
                "Please enter an experiment topic first."
            )

        else:

            with st.spinner(
                "Running parameter experiment..."
            ):

                low, high = parameter_experiment(
                    experiment_topic.strip()
                )

            st.session_state[
                "experiment"
            ] = {
                "low": low,
                "high": high,
            }

    experiment = st.session_state.get(
        "experiment"
    )

    if experiment:

        low_col, high_col = st.columns(
            2,
            gap="large",
        )

        with low_col:

            st.markdown(
                """
                <div class="output-box">
                    <div class="output-label">
                        Low temperature · 0.2
                    </div>
                """,
                unsafe_allow_html=True,
            )

            st.write(
                experiment["low"]
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

        with high_col:

            st.markdown(
                """
                <div class="output-box">
                    <div class="output-label">
                        High temperature · 1.0
                    </div>
                """,
                unsafe_allow_html=True,
            )

            st.write(
                experiment["high"]
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )


# ============================================================
# FOOTER
# ============================================================
st.markdown(
    """
    <div class="footer">
        Signal — AI Content Studio · Assignment 8 · Prompt Engineering
        <br>
        Walchand Institute of Technology, Solapur
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "</div>",
    unsafe_allow_html=True,
)
