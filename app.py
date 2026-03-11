import streamlit as st
import boto3
import json
import time

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="MarketGenius AI",
    page_icon="✦",
    layout="wide"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0f;
    color: #e8e6f0;
}
.stApp {
    background: radial-gradient(ellipse at 20% 0%, #1a0a2e 0%, #0a0a0f 50%);
    min-height: 100vh;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #e8e6f0 0%, #a78bfa 50%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.3rem;
}
.hero-sub {
    font-size: 1.1rem;
    color: #7c7a9a;
    font-weight: 300;
    margin-bottom: 2rem;
}
.card {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
}
.card-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #a78bfa;
    margin-bottom: 0.6rem;
}
.card-content {
    font-size: 0.95rem;
    line-height: 1.7;
    color: #ccc8e8;
    white-space: pre-wrap;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    color: #e8e6f0 !important;
}
label {
    color: #9896b8 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
}
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    width: 100% !important;
    box-shadow: 0 4px 24px rgba(124,58,237,0.4) !important;
}
hr { border-color: rgba(255,255,255,0.08) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ⚠️  PASTE YOUR AWS KEYS HERE
# ─────────────────────────────────────────────
AWS_ACCESS_KEY = st.secrets["AWS_ACCESS_KEY_ID"]
AWS_SECRET_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]  # ← REPLACE THIS
AWS_REGION        = 'us-east-1'
MODEL_ID          = 'anthropic.claude-3-haiku-20240307-v1:0'

# ─────────────────────────────────────────────
# BEDROCK CLIENT
# ─────────────────────────────────────────────
@st.cache_resource
def get_bedrock_client():
    """
    HOW THIS WORKS:
    boto3 is the Python library for AWS.
    We create a 'client' which is like a phone connection to AWS Bedrock.
    We pass our keys so AWS knows who we are.
    """
    return boto3.client(
        service_name='bedrock-runtime',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

# ─────────────────────────────────────────────
# CORE AI FUNCTION — THIS IS THE MOST IMPORTANT PART
# ─────────────────────────────────────────────
def call_bedrock(prompt: str, max_tokens: int = 1500) -> str:
    """
    THIS IS HOW WE TALK TO CLAUDE AI:

    1. We build a 'body' — a dictionary with our message
    2. We call invoke_model() — this sends the prompt to AWS Bedrock
    3. AWS Bedrock forwards it to Claude (the AI model)
    4. Claude generates a response and sends it back
    5. We read and return the text

    Think of it like sending a text message to an AI and reading the reply.
    """
    client = get_bedrock_client()

    # This is the standard format for talking to Claude via Bedrock
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",        # "user" means we are sending the message
                "content": prompt      # the actual text we send to Claude
            }
        ]
    }

    # Send the request to AWS Bedrock
    response = client.invoke_model(
        modelId=MODEL_ID,              # which AI model to use
        body=json.dumps(body),         # convert dict to JSON string
        contentType="application/json",
        accept="application/json"
    )

    # Read and parse the response
    response_body = json.loads(response['body'].read())

    # Extract just the text from the response
    return response_body['content'][0]['text']

# ─────────────────────────────────────────────
# PROMPT ENGINEERING FUNCTIONS
# What is Prompt Engineering?
# It's writing smart instructions to get the best AI output.
# We inject user inputs into pre-designed templates.
# ─────────────────────────────────────────────
def build_seo_prompt(product, description, audience, tone):
    return f"""You are an expert SEO content writer.

Product: {product}
Description: {description}
Target Audience: {audience}
Tone: {tone}

Write a complete SEO-optimized blog post with:
1. Catchy H1 title with primary keyword
2. Meta description (150-160 characters)
3. Introduction paragraph
4. 3 main sections with H2 headings
5. Strong conclusion with CTA
6. List of 5 target keywords

Make it genuinely helpful and rank-worthy."""

def build_social_prompt(product, description, audience, tone):
    return f"""You are a social media expert who creates viral content.

Product: {product}
Description: {description}
Target Audience: {audience}
Tone: {tone}

Generate social media content:

INSTAGRAM POST (150 words + 15 hashtags)
TWITTER/X THREAD (5 tweets under 280 chars each)
LINKEDIN POST (professional, 200 words)
FACEBOOK POST (conversational, 100 words)

Make each platform-native and engaging."""

def build_ads_prompt(product, description, audience, tone):
    return f"""You are a PPC advertising expert.

Product: {product}
Description: {description}
Target Audience: {audience}
Tone: {tone}

Create high-converting ad copy:

GOOGLE SEARCH ADS (3 variations):
- Headline 1 (30 chars max)
- Headline 2 (30 chars max)
- Description (90 chars max)

META/FACEBOOK ADS (2 variations):
- Primary text (125 chars)
- Headline (40 chars)
- CTA button text

Focus on pain points, benefits, and urgency."""

def build_email_prompt(product, description, audience, tone):
    return f"""You are an email marketing specialist.

Product: {product}
Description: {description}
Target Audience: {audience}
Tone: {tone}

Write a 3-email marketing sequence:

EMAIL 1 - AWARENESS (subject line + 150 word body)
EMAIL 2 - CONSIDERATION (subject line + 200 word body)
EMAIL 3 - CONVERSION (subject line + 180 word body)

Include compelling subject lines and clear CTAs."""

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if 'results' not in st.session_state:
    st.session_state.results = {}
if 'count' not in st.session_state:
    st.session_state.count = 0

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="hero-title">MarketGenius AI</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Generate complete marketing campaigns powered by AWS Bedrock + Claude AI</div>', unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN LAYOUT
# ─────────────────────────────────────────────
left_col, right_col = st.columns([1, 1.6], gap="large")

with left_col:
    st.markdown("### ⚙ Campaign Settings")

    product_name = st.text_input(
        "Product / Brand Name",
        placeholder="e.g. FreshBrew Cold Coffee"
    )
    product_desc = st.text_area(
        "Product Description",
        placeholder="Describe your product, features, and value proposition...",
        height=120
    )
    target_audience = st.text_input(
        "Target Audience",
        placeholder="e.g. Millennials who love specialty coffee, aged 25-35"
    )
    tone = st.selectbox(
        "Brand Voice & Tone",
        ["Professional & Authoritative", "Friendly & Conversational",
         "Exciting & Energetic", "Luxury & Premium", "Witty & Humorous",
         "Educational & Informative"]
    )

    st.markdown("<br>", unsafe_allow_html=True)

    content_types = st.multiselect(
        "Select Content to Generate",
        ["📝 SEO Blog Post", "📱 Social Media Pack",
         "🎯 Ad Copy", "📧 Email Sequence"],
        default=["📝 SEO Blog Post", "📱 Social Media Pack"]
    )

    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("✦ Generate Campaign")

    # How it works box
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <div class="card-label">🧠 What's Happening Behind the Scenes</div>
        <div class="card-content" style="font-size:0.85rem; color:#7c7a9a;">
1. Your inputs fill into prompt templates<br><br>
2. Prompts sent to AWS Bedrock API via boto3<br><br>
3. Bedrock routes to Claude 3 Haiku AI model<br><br>
4. Claude generates content & sends back response<br><br>
5. We display the result on screen
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GENERATION LOGIC
# ─────────────────────────────────────────────
with right_col:
    st.markdown("### ✦ Generated Content")

    if generate_btn:
        if not product_name or not product_desc or not target_audience:
            st.error("⚠ Please fill in Product Name, Description, and Target Audience.")
        elif not content_types:
            st.error("⚠ Please select at least one content type.")
        else:
            st.session_state.results = {}

            generators = {
                "📝 SEO Blog Post":    ("SEO Blog Post",    build_seo_prompt),
                "📱 Social Media Pack": ("Social Media Pack", build_social_prompt),
                "🎯 Ad Copy":           ("Ad Copy",           build_ads_prompt),
                "📧 Email Sequence":    ("Email Sequence",    build_email_prompt),
            }

            progress = st.progress(0)
            total = len(content_types)

            for i, content_type in enumerate(content_types):
                label, prompt_fn = generators[content_type]
                with st.spinner(f"⏳ Generating {label}... (calling AWS Bedrock)"):
                    try:
                        prompt = prompt_fn(
                            product_name, product_desc,
                            target_audience, tone
                        )
                        result = call_bedrock(prompt)
                        st.session_state.results[content_type] = result
                        st.session_state.count += 1
                        time.sleep(0.3)
                    except Exception as e:
                        st.session_state.results[content_type] = f"ERROR: {str(e)}"

                progress.progress((i + 1) / total)

            progress.empty()
            st.success(f"✅ Generated {total} content piece(s) successfully!")

    # Display Results
    if st.session_state.results:
        for content_type, content in st.session_state.results.items():
            with st.expander(f"{content_type}", expanded=True):
                if content.startswith("ERROR"):
                    st.error(content)
                    st.info("💡 Check your AWS Secret Key in the app.py file — make sure it's correct!")
                else:
                    label = content_type.split(" ", 1)[1]
                    st.markdown(f"""
                    <div class="card">
                        <div class="card-label">{label}</div>
                        <div class="card-content">{content}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.download_button(
                        label=f"⬇ Download {label}",
                        data=content,
                        file_name=f"{product_name.replace(' ','_')}_{label.replace(' ','_')}.txt",
                        mime="text/plain",
                        key=f"dl_{content_type}"
                    )
    else:
        st.markdown("""
        <div class="card" style="text-align:center; padding:3rem 2rem;">
            <div style="font-size:3rem; margin-bottom:1rem;">✦</div>
            <div style="font-family:'Syne',sans-serif; font-size:1.1rem; color:#a78bfa; margin-bottom:0.5rem;">
                Ready to Generate
            </div>
            <div style="font-size:0.85rem; color:#5c5a78; line-height:1.6;">
                Fill in your product details on the left<br>
                and click Generate Campaign to start.<br><br>
                Each call goes to AWS Bedrock → Claude AI
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#3a3858; font-size:0.8rem; padding:1rem 0;">
    MarketGenius AI · AWS Bedrock + Claude 3 Haiku · Built for Learning GenAI
</div>
""", unsafe_allow_html=True)