import html
import re
from collections import Counter

import streamlit as st
from google import genai
from google.genai import types
from textblob import TextBlob


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Signal — AI Content Studio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* -----------------------------------------------------
       GLOBAL
    ----------------------------------------------------- */

    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

    html, body, [class*="css"] {
        font-family: "DM Sans", sans-serif;
    }

    .stApp {
        background: #F7F8FC;
        color: #171923;
    }

    [data-testid="stSidebar"] {
        display: none !important;
    }

    .main .block-container {
        padding-top: 0.5rem;
        padding-bottom: 3rem;
    }

    .main-wrap {
        max-width: 1250px;
        margin: 0 auto;
        padding: 25px 35px 50px 35px;
    }


    /* -----------------------------------------------------
       TOP NAVIGATION
    ----------------------------------------------------- */

    .top-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 0 30px 0;
        border-bottom: 1px solid #E7E8EF;
    }

    .brand {
        font-family: "Playfair Display", serif;
        font-size: 30px;
        font-weight: 700;
        color: #171923;
        letter-spacing: -0.8px;
        line-height: 1;
    }

    .brand-sub {
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 2px;
        color: #777B8A;
        margin-top: 6px;
    }

    .assignment-badge {
        display: inline-flex;
        align-items: center;
        padding: 8px 13px;
        border-radius: 20px;
        background: #EFEDFF;
        color: #5B4CF6;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.7px;
    }


    /* -----------------------------------------------------
       HERO
    ----------------------------------------------------- */

    .hero {
        padding: 60px 0 45px 0;
        max-width: 850px;
    }

    .hero-kicker {
        display: inline-block;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.8px;
        color: #5B4CF6;
        margin-bottom: 16px;
    }

    .hero-title {
        font-family: "Playfair Display", serif;
        font-size: clamp(48px, 7vw, 78px);
        font-weight: 700;
        line-height: 0.95;
        letter-spacing: -3px;
        color: #171923;
        margin: 0;
    }

    .hero-description {
        margin-top: 25px;
        max-width: 690px;
        color: #666A79;
        font-size: 17px;
        line-height: 1.7;
    }


    /* -----------------------------------------------------
       TABS
    ----------------------------------------------------- */

    .stTabs {
        margin-top: 5px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid #E3E4EB;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        padding: 0 18px;
        color: #707483;
        font-size: 13px;
        font-weight: 600;
        border-radius: 8px 8px 0 0;
    }

    .stTabs [aria-selected="true"] {
        color: #5B4CF6 !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #5B4CF6;
    }


    /* -----------------------------------------------------
       SECTION HEADINGS
    ----------------------------------------------------- */

    .section-kicker {
        color: #5B4CF6;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .section-title {
        font-family: "Playfair Display", serif;
        font-size: 30px;
        font-weight: 700;
        color: #171923;
        margin-bottom: 6px;
    }

    .section-description {
        color: #737786;
        font-size: 14px;
        line-height: 1.6;
        margin-bottom: 25px;
    }


    /* -----------------------------------------------------
       INPUTS
    ----------------------------------------------------- */

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    textarea {
        border-radius: 9px !important;
    }

    div[data-baseweb="select"] > div {
        background: #FFFFFF !important;
        border-color: #DDE0E8 !important;
    }

    input,
    textarea {
        background: #FFFFFF !important;
        border: 1px solid #DDE0E8 !important;
    }

    textarea {
        min-height: 180px !important;
    }

    label {
        font-size: 12px !important;
        font-weight: 600 !important;
        color: #4F5362 !important;
    }


    /* -----------------------------------------------------
       BUTTONS
    ----------------------------------------------------- */

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


    /* -----------------------------------------------------
       OUTPUT AREA
    ----------------------------------------------------- */

    .output-box {
        background: #FFFFFF;
        border: 1px solid #E3E5EC;
        border-radius: 12px;
        padding: 25px;
        margin-top: 20px;
        box-shadow: 0 8px 25px rgba(23, 25, 35, 0.04);
    }

    .output-label {
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.4px;
        color: #8A8E9C;
        text-transform: uppercase;
        margin-bottom: 14px;
    }


    /* -----------------------------------------------------
       METRIC CARDS
    ----------------------------------------------------- */

    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E3E5EC;
        border-radius: 12px;
        padding: 20px;
        min-height: 110px;
    }

    .metric-label {
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1px;
        color: #8A8E9C;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .metric-value {
        font-size: 27px;
        font-weight: 700;
        color: #171923;
    }


    /* -----------------------------------------------------
       KEYWORD TAGS
    ----------------------------------------------------- */

    .keyword-tag {
        display: inline-block;
        padding: 7px 10px;
        margin: 4px 5px 4px 0;
        border-radius: 20px;
        background: #EFEDFF;
        color: #5B4CF6;
        font-size: 11px;
        font-weight: 600;
    }


    /* -----------------------------------------------------
       INFO BOX
    ----------------------------------------------------- */

    .info-box {
        background: #F0EEFF;
        border: 1px solid #DDD8FF;
        border-radius: 10px;
        padding: 16px 18px;
        color: #5147A6;
        font-size: 12px;
        line-height: 1.6;
        margin-bottom: 20px;
    }


    /* -----------------------------------------------------
       PARAMETER CARDS
    ----------------------------------------------------- */

    .parameter-card {
        background: #FFFFFF;
        border: 1px solid #E3E5EC;
        border-radius: 12px;
        padding: 20px;
        min-height: 260px;
        box-shadow: 0 6px 20px rgba(23, 25, 35, 0.03);
    }

    .parameter-name {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        color: #5B4CF6;
        margin-bottom: 10px;
    }

    .parameter-description {
        font-size: 12px;
        color: #777B88;
        line-height: 1.5;
        margin-bottom: 15px;
    }


    /* -----------------------------------------------------
       FOOTER
    ----------------------------------------------------- */

    .footer {
        border-top: 1px solid #E3E4EB;
        margin-top: 55px;
        padding-top: 20px;
        color: #9296A3;
        font-size: 11px;
        text-align: center;
    }


    /* -----------------------------------------------------
       MOBILE
    ----------------------------------------------------- */

    @media (max-width: 700px) {

        .main-wrap {
            padding: 20px 18px 40px 18px;
        }

        .top-nav {
            align-items: flex-start;
            gap: 15px;
        }

        .assignment-badge {
            font-size: 8px;
            padding: 7px 9px;
        }

        .hero {
            padding: 40px 0 30px 0;
        }

        .hero-title {
            font-size: 52px;
        }

        .hero-description {
            font-size: 15px;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 0 10px;
            font-size: 11px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# GEMINI GENERATION
# =========================================================

def generate_response(
    prompt,
    thinking_level="medium",
    max_tokens=1024,
):
    api_key = st.secrets.get(
        "GEMINI_API_KEY",
        "",
    ).strip()

    if not api_key:
        return (
            "GEMINI_API_KEY is not configured.\n\n"
            "Open your Streamlit Community Cloud app → "
            "Settings → Secrets and add:\n\n"
            'GEMINI_API_KEY = "YOUR_API_KEY"'
        )

    if thinking_level not in {
        "low",
        "medium",
        "high",
    }:
        thinking_level = "medium"

    try:
        client = genai.Client(
            api_key=api_key
        )

        config = types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            thinking_config=types.ThinkingConfig(
                thinking_level=thinking_level
            ),
        )

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=config,
        )

        if response and response.text:
            return response.text.strip()

        return "No response was returned by the AI model."

    except Exception as exc:
        return f"AI generation error:\n\n{exc}"


# =========================================================
# PROMPT BUILDERS
# =========================================================

def build_prompt(content_type, topic):
    if content_type == "Poem":
        return f"""
You are a creative writing assistant.

Write an original poem about:
{topic}

Requirements:
- 3 to 5 stanzas
- Strong imagery
- Natural language
- Emotional but not overly complicated
- Give the poem a suitable title
"""

    if content_type == "Story":
        return f"""
You are a professional short-story writer.

Write an original short story about:
{topic}

Requirements:
- Give it a title
- Clear beginning, middle and ending
- Include a small conflict
- Use realistic dialogue where appropriate
- Keep it engaging and easy to read
"""

    return f"""
You are a social media content strategist.

Create a social media post about:
{topic}

Requirements:
- Start with an engaging hook
- Keep the writing concise
- Use natural language
- Include a clear call to action
- Add 4 to 6 relevant hashtags
"""


def generate_content(content_type, topic):
    prompt = build_prompt(
        content_type,
        topic,
    )

    return generate_response(
        prompt,
        thinking_level="medium",
        max_tokens=900,
    )


def generate_podcast_plan(topic):
    prompt = f"""
You are an experienced podcast producer.

Create a complete podcast episode plan for:
{topic}

Include:

1. Episode title
2. Episode hook
3. Short introduction
4. 4 to 6 main segments
5. Questions for the host
6. Questions for the guest
7. Audience engagement idea
8. Closing statement

Make the structure practical and easy to follow.
"""

    return generate_response(
        prompt,
        thinking_level="medium",
        max_tokens=1200,
    )


# =========================================================
# TEXT ANALYSIS
# =========================================================

STOP_WORDS = {
    "the",
    "and",
    "for",
    "that",
    "this",
    "with",
    "from",
    "have",
    "has",
    "are",
    "was",
    "were",
    "will",
    "would",
    "could",
    "should",
    "about",
    "into",
    "your",
    "you",
    "they",
    "their",
    "there",
    "then",
    "than",
    "them",
    "what",
    "when",
    "where",
    "which",
    "while",
    "also",
    "just",
    "very",
    "more",
    "some",
    "such",
    "only",
    "been",
    "being",
    "because",
    "but",
    "not",
    "can",
    "our",
    "out",
    "all",
    "any",
    "how",
    "its",
    "it's",
    "too",
    "was",
    "who",
    "why",
    "his",
    "her",
    "she",
    "him",
    "our",
    "we",
    "i",
    "a",
    "an",
    "in",
    "on",
    "of",
    "to",
    "is",
    "it",
    "as",
    "at",
    "or",
    "be",
    "by",
}


def analyze_text(text):
    blob = TextBlob(text)

    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    if polarity > 0.1:
        sentiment = "Positive"
    elif polarity < -0.1:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    words = re.findall(
        r"\b[a-zA-Z]{3,}\b",
        text.lower(),
    )

    filtered_words = [
        word
        for word in words
        if word not in STOP_WORDS
    ]

    keywords = Counter(
        filtered_words
    ).most_common(10)

    return (
        sentiment,
        polarity,
        subjectivity,
        keywords,
    )


# =========================================================
# PARAMETER EXPERIMENT
# =========================================================

def parameter_experiment(topic):
    base_prompt = f"""
Explain the following topic for a college student:

{topic}

Use:
- Simple language
- Clear structure
- One practical example
- Short conclusion
"""

    results = {}

    for level in [
        "low",
        "medium",
        "high",
    ]:
        results[level] = generate_response(
            base_prompt,
            thinking_level=level,
            max_tokens=400,
        )

    return results


# =========================================================
# MAIN PAGE
# =========================================================

st.markdown(
    """
    <div class="main-wrap">

        <div class="top-nav">
            <div>
                <div class="brand">Signal</div>
                <div class="brand-sub">
                    AI CONTENT STUDIO
                </div>
            </div>

            <div class="assignment-badge">
                ASSIGNMENT 8 · PROMPT ENGINEERING
            </div>
        </div>

        <div class="hero">
            <div class="hero-kicker">
                AI CONTENT WORKSPACE
            </div>

            <h1 class="hero-title">
                Signal
            </h1>

            <div class="hero-description">
                A small studio for scripting content,
                planning an episode, and reading the room —
                built for Walchand Institute of Technology,
                Solapur.
            </div>
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "✦ Write",
        "🎙 Plan an episode",
        "◌ Read the room",
        "⌁ Parameter lab",
    ]
)


# =========================================================
# TAB 1 — CONTENT GENERATION
# =========================================================

with tab1:

    st.markdown(
        """
        <div style="padding-top:30px;">
            <div class="section-kicker">
                CREATE
            </div>

            <div class="section-title">
                Turn an idea into content.
            </div>

            <div class="section-description">
                Choose a format, describe your topic,
                and generate content using a structured prompt.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(
        [1, 2],
        gap="large",
    )

    with col1:

        content_type = st.selectbox(
            "Content type",
            [
                "Poem",
                "Story",
                "Social Media Post",
            ],
        )

    with col2:

        topic = st.text_input(
            "Topic",
            placeholder="e.g. The future of artificial intelligence",
        )

    generate_button = st.button(
        "Generate content",
        key="generate_content",
    )

    if generate_button:

        if not topic.strip():

            st.warning(
                "Please enter a topic first."
            )

        else:

            with st.spinner(
                "Creating your content..."
            ):

                result = generate_content(
                    content_type,
                    topic,
                )

            st.markdown(
                """
                <div class="output-box">
                    <div class="output-label">
                        Generated content
                    </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                result
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )


# =========================================================
# TAB 2 — PODCAST PLANNING
# =========================================================

with tab2:

    st.markdown(
        """
        <div style="padding-top:30px;">
            <div class="section-kicker">
                PODCAST PLANNER
            </div>

            <div class="section-title">
                Build the episode before you record.
            </div>

            <div class="section-description">
                Generate a structured podcast outline
                with hooks, segments, questions and a closing.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    podcast_topic = st.text_input(
        "Episode topic",
        placeholder="e.g. How AI is changing education",
        key="podcast_topic",
    )

    podcast_button = st.button(
        "Create episode plan",
        key="create_episode_plan",
    )

    if podcast_button:

        if not podcast_topic.strip():

            st.warning(
                "Please enter an episode topic first."
            )

        else:

            with st.spinner(
                "Planning your episode..."
            ):

                podcast_result = generate_podcast_plan(
                    podcast_topic
                )

            st.markdown(
                """
                <div class="output-box">
                    <div class="output-label">
                        Episode plan
                    </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                podcast_result
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )


# =========================================================
# TAB 3 — TEXT ANALYSIS
# =========================================================

with tab3:

    st.markdown(
        """
        <div style="padding-top:30px;">
            <div class="section-kicker">
                TEXT ANALYSIS
            </div>

            <div class="section-title">
                Read the room.
            </div>

            <div class="section-description">
                Inspect sentiment, subjectivity and
                frequent keywords in any piece of text.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    analysis_text = st.text_area(
        "Text to analyse",
        placeholder=(
            "Paste an article, review, social media post, "
            "or any other text here..."
        ),
        height=220,
    )

    analyze_button = st.button(
        "Analyse text",
        key="analyse_text",
    )

    if analyze_button:

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

            st.markdown(
                "<div style='height:18px;'></div>",
                unsafe_allow_html=True,
            )

            metric1, metric2, metric3 = st.columns(
                3,
                gap="medium",
            )

            with metric1:

                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">
                            Sentiment
                        </div>

                        <div class="metric-value">
                            {html.escape(sentiment)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with metric2:

                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">
                            Polarity
                        </div>

                        <div class="metric-value">
                            {polarity:.2f}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with metric3:

                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">
                            Subjectivity
                        </div>

                        <div class="metric-value">
                            {subjectivity:.2f}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                "<div style='height:25px;'></div>",
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <div class="output-box">
                    <div class="output-label">
                        Top keywords
                    </div>
                """,
                unsafe_allow_html=True,
            )

            if keywords:

                keyword_html = ""

                for word, count in keywords:

                    keyword_html += (
                        f'<span class="keyword-tag">'
                        f'{html.escape(word)} · {count}'
                        f'</span>'
                    )

                st.markdown(
                    keyword_html,
                    unsafe_allow_html=True,
                )

            else:

                st.write(
                    "No frequent keywords found."
                )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )


# =========================================================
# TAB 4 — PARAMETER LAB
# =========================================================

with tab4:

    st.markdown(
        """
        <div style="padding-top:30px;">
            <div class="section-kicker">
                PROMPT EXPERIMENT
            </div>

            <div class="section-title">
                Compare thinking levels.
            </div>

            <div class="section-description">
                Run the same prompt using low, medium
                and high thinking levels and compare
                how the responses differ.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="info-box">
            This experiment keeps the prompt the same
            while changing the Gemini thinking level.
            This helps demonstrate how a model parameter
            can influence response depth and reasoning.
        </div>
        """,
        unsafe_allow_html=True,
    )

    experiment_topic = st.text_input(
        "Experiment topic",
        placeholder="e.g. Explain how blockchain works",
        key="experiment_topic",
    )

    experiment_button = st.button(
        "Run parameter experiment",
        key="run_parameter_experiment",
    )

    if experiment_button:

        if not experiment_topic.strip():

            st.warning(
                "Please enter a topic first."
            )

        else:

            with st.spinner(
                "Running three experiments..."
            ):

                experiment_results = parameter_experiment(
                    experiment_topic
                )

            low_col, medium_col, high_col = st.columns(
                3,
                gap="medium",
            )

            with low_col:

                st.markdown(
                    """
                    <div class="parameter-card">

                        <div class="parameter-name">
                            LOW
                        </div>

                        <div class="parameter-description">
                            Lower thinking effort.
                        </div>

                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    experiment_results["low"]
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True,
                )

            with medium_col:

                st.markdown(
                    """
                    <div class="parameter-card">

                        <div class="parameter-name">
                            MEDIUM
                        </div>

                        <div class="parameter-description">
                            Balanced thinking effort.
                        </div>

                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    experiment_results["medium"]
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True,
                )

            with high_col:

                st.markdown(
                    """
                    <div class="parameter-card">

                        <div class="parameter-name">
                            HIGH
                        </div>

                        <div class="parameter-description">
                            Higher thinking effort.
                        </div>

                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    experiment_results["high"]
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True,
                )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="main-wrap">

        <div class="footer">
            Signal · AI Content Studio
            &nbsp;·&nbsp;
            Assignment 8 — Prompt Engineering
            &nbsp;·&nbsp;
            Walchand Institute of Technology, Solapur
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)
