"""
TailorTalk: AI-Powered Saree Visual Similarity Search Application
Haute Couture Atelier for Byrappa Silks Heritage Sarees
Backend: LangChain + Gemini 3.7 Flash + FashionCLIP + ChromaDB + OpenCV
"""

import os
import logging
import sys

# Suppress verbose transformers and Hugging Face Hub internal startup logs
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Pre-suppress loggers that emit noise during import
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("transformers.image_processing_utils").setLevel(logging.CRITICAL)
logging.getLogger("transformers.image_processing_utils_fast").setLevel(logging.CRITICAL)
# Suppress google-genai AFC (automatic function calling) recommendation message
logging.getLogger("google_genai.models").setLevel(logging.ERROR)
logging.getLogger("google.genai").setLevel(logging.ERROR)

import io
import json
import base64
import importlib
import warnings
from typing import Optional, List, Dict, Any, Union
from PIL import Image
import streamlit as st
from dotenv import load_dotenv

# Suppress SDK and third-party warnings
warnings.filterwarnings("ignore")


# Load local environment variables from .env
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="TailorTalk | Byrappa Silks Visual Stylist",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.ui_components import (
    inject_boutique_css,
    render_boutique_header,
    render_product_card,
    render_results_grid,
    render_stylist_recommendation,
    get_default_drape_advice,
    SAMPLE_INSPIRATIONS
)

# Suppress raw print() [ERROR] messages from transformers auto_docstring.py
# (DeepseekVL, Kimi_K25, PaddleOCR undocumented kwargs warnings)
_original_stdout = sys.stdout
sys.stdout = open(os.devnull, "w")
try:
    from src.agent import create_saree_agent
    from src.search_engine import SareeSearchEngine
finally:
    sys.stdout.close()
    sys.stdout = _original_stdout

@st.cache_resource(show_spinner=False)
def get_search_engine() -> SareeSearchEngine:
    """Retrieve warm cached singleton instance of SareeSearchEngine."""
    return SareeSearchEngine.get_instance()

# Pre-warm search engine
search_engine = get_search_engine()

# Inject warm boutique CSS
inject_boutique_css()

# API Key Resolution (from .env, environment, or Streamlit secrets)
resolved_api_key = os.getenv("GOOGLE_API_KEY", "")
if not resolved_api_key:
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            resolved_api_key = st.secrets["GOOGLE_API_KEY"]
    except Exception:
        pass

if "api_key" not in st.session_state:
    st.session_state.api_key = resolved_api_key

if "last_query_img" not in st.session_state:
    st.session_state.last_query_img = None

if "last_img_url" not in st.session_state:
    st.session_state.last_img_url = ""

# Initialize session state for conversation
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Greetings. I am Vira, your couture saree stylist from Byrappa Silks (Established 1928).\n\nUpload a saree photograph, paste an image link, or ask me for specific weaves (such as Kanchipuram Silk, Banarasi, Organza Tissue, or Munga Crape). How may I assist your drape search today?",
            "results": None
        }
    ]

# ---------------------------------------------------------------------------
# Sidebar: Atelier Brand & Search Controls (No Emojis)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-crest">HAUTE COUTURE</div>
        <div class="sidebar-brand-title">Byrappa Silks</div>
        <div class="sidebar-brand-subtitle">AI VISUAL CONCIERGE</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Search Preferences")
    top_k = st.slider("Number of Matches", min_value=3, max_value=9, value=6, step=3)
    
    fabric_choice = st.selectbox(
        "Weave & Fabric Filter",
        options=["All Weaves", "Kanchipuram Silk", "Banarasi", "Organza", "Munga Crape", "Pashmina", "Tissue", "Tussar"]
    )
    selected_fabric = None if fabric_choice == "All Weaves" else fabric_choice

    # Catalogue Index Status
    try:
        engine = SareeSearchEngine.get_instance()
        indexed_count = engine.vector_store.count()
        st.markdown(f"""
        <div class="index-status-card">
            <strong>{indexed_count:,} Handcrafted Sarees</strong> indexed and active
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        st.markdown("""
        <div class="index-status-card">
            Catalogue index synchronizing...
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("Start New Consultation", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Greetings. I am Vira, your couture saree stylist. Please upload a photograph, paste an image link, or describe your desired weave and occasion.",
                "results": None
            }
        ]
        st.session_state.last_query_img = None
        st.session_state.last_img_url = ""
        st.rerun()

    # Developer configuration (only visible as a collapsed drawer if API key is not configured in .env)
    if not st.session_state.api_key:
        st.markdown("---")
        with st.expander("Developer Setup (Missing API Key)", expanded=False):
            st.caption("Provide your Google Gemini API key to activate the AI Agent if not set in server environment.")
            dev_key = st.text_input("Gemini API Key", type="password", key="dev_api_key_input")
            if dev_key:
                st.session_state.api_key = dev_key
                os.environ["GOOGLE_API_KEY"] = dev_key
                st.success("API key registered.")
                st.rerun()

# ---------------------------------------------------------------------------
# Main Banner & Layout
# ---------------------------------------------------------------------------
render_boutique_header()

# ---------------------------------------------------------------------------
# Visual Match Studio (Interactive Tabs - No Emojis)
# ---------------------------------------------------------------------------
st.markdown("### Visual Match Studio")
tab_upload, tab_url, tab_curated = st.tabs([
    "Upload Saree Photo",
    "Paste Image Link",
    "Curated Inspiration Gallery"
])

pending_query_text: Optional[str] = None
pending_query_img: Optional[Image.Image] = None
pending_img_url: str = ""

with tab_upload:
    st.caption("Upload any saree photo (JPG, PNG, WebP) to discover visually identical weaves in the Byrappa Silks archive.")
    col_up1, col_up2 = st.columns([2, 1])
    with col_up1:
        uploaded_file = st.file_uploader(
            "Drop saree photo here",
            type=["webp", "jpg", "jpeg", "png"],
            label_visibility="collapsed"
        )
    with col_up2:
        if uploaded_file:
            pil_img = Image.open(uploaded_file).convert("RGB")
            st.image(pil_img, caption="Query Preview", width="stretch")
            if st.button("Find Matching Sarees", type="primary", use_container_width=True, key="btn_search_upload"):
                pending_query_text = "Find visually similar sarees for this uploaded photo."
                pending_query_img = pil_img

with tab_url:
    st.caption("Paste a direct public image link to match against our collection.")
    col_url1, col_url2 = st.columns([3, 1])
    with col_url1:
        url_input = st.text_input(
            "Saree Image URL",
            placeholder="https://example.com/saree-photograph.jpg",
            label_visibility="collapsed"
        )
    with col_url2:
        url_search_clicked = st.button("Match URL", type="primary", use_container_width=True, key="btn_search_url")
    
    if url_search_clicked and url_input.strip():
        pending_query_text = f"Find sarees visually matching this image link: {url_input.strip()}"
        pending_img_url = url_input.strip()

with tab_curated:
    st.caption("Select an authentic piece from our atelier to test multi-signal visual similarity search.")
    cols = st.columns(4)
    for idx, sample in enumerate(SAMPLE_INSPIRATIONS):
        with cols[idx]:
            st.markdown(f"""
            <div class="sample-pill-card">
                <img src="{sample['image_url']}" class="sample-thumb" alt="{sample['title']}" />
                <div class="sample-name">{sample['title']}</div>
                <div class="sample-badge">{sample['fabric']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Match This {sample['fabric'].split()[0]}", key=f"btn_sample_{idx}", use_container_width=True):
                pending_query_text = sample["query_prompt"]
                pending_img_url = sample["image_url"]

# ---------------------------------------------------------------------------
# Quick Suggestion Chips for Stylist Conversation (No Emojis)
# ---------------------------------------------------------------------------
st.markdown("##### Quick Stylist Inquiries:")
col_q1, col_q2, col_q3, col_q4 = st.columns(4)
if col_q1.button("Pastel Organza Sarees", use_container_width=True):
    pending_query_text = "Show me elegant pastel organza sarees with delicate border work."
if col_q2.button("Banarasi Silk with Zari", use_container_width=True):
    pending_query_text = "Find pure Banarasi silk sarees with rich golden zari pallu."
if col_q3.button("Festive Green Sarees", use_container_width=True):
    pending_query_text = "Find festive green silk sarees for auspicious occasions."
if col_q4.button("Lightweight Munga Crape", use_container_width=True):
    pending_query_text = "Show me lightweight Munga Crape sarees under ₹5,000."

st.markdown("---")

# ---------------------------------------------------------------------------
# Core Search Query & Stylist Pipeline
# ---------------------------------------------------------------------------
def process_search_query(
    user_text: str = "",
    query_img: Optional[Image.Image] = None,
    img_url: str = ""
):
    """Execute high-speed visual similarity search and boutique styling advice."""
    engine = get_search_engine()

    # Update persistent reference for follow-up turns
    if query_img:
        st.session_state.last_query_img = query_img
    if img_url:
        st.session_state.last_img_url = img_url

    effective_img = query_img or (st.session_state.last_query_img if not user_text else None)
    effective_url = img_url or (st.session_state.last_img_url if not user_text else "")

    user_msg_content = user_text if user_text else "Curate visual matches for this saree."
    st.session_state.messages.append({
        "role": "user",
        "content": user_msg_content,
        "query_image": query_img if query_img else (img_url if img_url else None),
        "results": None
    })

    extracted_results = None
    output_text = ""
    recommendation_text = ""

    # FAST PATH 1: Image provided (Upload, URL, or Curated Inspiration Sample)
    if query_img or img_url or (not user_text and (effective_img or effective_url)):
        src = query_img if query_img else (img_url if img_url else (effective_img or effective_url))
        try:
            extracted_results = engine.search_by_image(
                image_source=src,
                top_k=top_k,
                fabric_filter=selected_fabric
            )
        except Exception as e:
            st.error(f"Visual analysis error: {e}")
            extracted_results = []

        if extracted_results:
            top_fabric = extracted_results[0].get("fabric", "Silk")
            top_color = extracted_results[0].get("primary_color", "")
            # Fast AI Stylist Advice Generation
            if st.session_state.api_key:
                try:
                    agent = create_saree_agent(api_key=st.session_state.api_key)
                    recommendation_text = agent.generate_stylist_advice(
                        top_matches=extracted_results,
                        user_context=user_text
                    )
                except Exception:
                    recommendation_text = ""

            if not recommendation_text:
                recommendation_text = get_default_drape_advice(top_fabric, top_color)

            st.session_state.messages.append({
                "role": "assistant",
                "content": "",
                "recommendation": recommendation_text,
                "results": extracted_results
            })
            return

    # FAST PATH 2: Conversational Chat or Text Search
    if user_text:
        try:
            if st.session_state.api_key:
                agent = create_saree_agent(api_key=st.session_state.api_key)
                prompt_input = user_text
                if selected_fabric:
                    prompt_input += f"\n[Preferred Fabric]: {selected_fabric}"
                prompt_input += f"\n[Requested Top-K]: {top_k}"

                response = agent.invoke(
                    input_text=prompt_input,
                    chat_history=st.session_state.messages[:-1]
                )
                output_text = response.get("output", "")
                extracted_results = response.get("results")

            # Direct text search fallback if needed
            if not extracted_results and any(kw in user_text.lower() for kw in ["find", "saree", "show", "search", "looking for", "silk", "organza", "banarasi", "crape"]):
                extracted_results = engine.search_by_text(
                    query_text=user_text,
                    top_k=top_k
                )

            if extracted_results:
                if output_text:
                    lines = [
                        line for line in output_text.split("\n")
                        if not (
                            line.strip().startswith("1.") or line.strip().startswith("2.") or
                            line.strip().startswith("3.") or line.strip().startswith("4.") or
                            line.strip().startswith("5.") or line.strip().startswith("6.") or
                            line.strip().startswith("- Match") or line.strip().startswith("- Fabric") or
                            line.strip().startswith("- Palette") or line.strip().startswith("- Price") or
                            line.strip().startswith("- SKU") or line.strip().startswith("Here are the") or
                            line.strip().startswith("I have analyzed")
                        )
                    ]
                    recommendation_text = "\n".join(lines).strip()

                if not recommendation_text:
                    top_fabric = extracted_results[0].get("fabric", "Silk")
                    recommendation_text = get_default_drape_advice(top_fabric)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "",
                    "recommendation": recommendation_text,
                    "results": extracted_results
                })
            else:
                fallback_reply = output_text if output_text else "How may I assist your saree styling and drape search today?"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": fallback_reply,
                    "results": None
                })
        except Exception:
            # Resilient direct search fallback
            fallback_results = engine.search_by_text(query_text=user_text, top_k=top_k)
            if fallback_results:
                top_fabric = fallback_results[0].get("fabric", "Silk")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "",
                    "recommendation": get_default_drape_advice(top_fabric),
                    "results": fallback_results
                })
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Our atelier stylist is currently assisting with your selection. Please try rephrasing your search or selecting a sample drape.",
                    "results": None
                })

# Process pending queries from toolbar or curated gallery
if pending_query_text or pending_query_img or pending_img_url:
    process_search_query(
        user_text=pending_query_text or "",
        query_img=pending_query_img,
        img_url=pending_img_url
    )
    st.rerun()

# ---------------------------------------------------------------------------
# Natural Infinite Scroll Chat Stream (ChatGPT / Claude Style)
# ---------------------------------------------------------------------------
st.markdown("### Consultation Stream")

total_messages = len(st.session_state.messages)

for idx, msg in enumerate(st.session_state.messages):
    is_latest = (idx == total_messages - 1)
    with st.chat_message(msg["role"]):
        if is_latest:
            st.markdown('<div id="latest-consultation-anchor" style="height: 1px; margin-top: -10px;"></div>', unsafe_allow_html=True)
        if msg.get("query_image"):
            st.image(msg["query_image"], caption="Query Drape", width=220)
        if msg.get("results"):
            render_results_grid(msg["results"], num_cols=3)
            rec = msg.get("recommendation") or msg.get("content", "")
            if rec and rec.strip():
                render_stylist_recommendation(rec)
        else:
            if msg.get("content"):
                st.markdown(msg["content"])

# Bottom anchor at end of conversation stream
st.markdown('<div id="page-bottom-anchor" style="height: 1px;"></div>', unsafe_allow_html=True)

# Robust smooth auto-scrolling to the latest response across Streamlit view containers
st.html("""
<script>
    function autoScrollToLatest() {
        try {
            const parentDoc = window.parent.document;
            const bottomAnchor = parentDoc.getElementById('page-bottom-anchor');
            const latestAnchor = parentDoc.getElementById('latest-consultation-anchor');

            // Try scrolling the Streamlit main scroll container
            const scrollContainer = parentDoc.querySelector('[data-testid="stAppViewContainer"]') ||
                                    parentDoc.querySelector('section.main') ||
                                    parentDoc.querySelector('[data-testid="stMain"]') ||
                                    parentDoc.querySelector('.main');

            if (bottomAnchor) {
                bottomAnchor.scrollIntoView({ behavior: 'smooth', block: 'end' });
            } else if (latestAnchor) {
                latestAnchor.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }

            if (scrollContainer) {
                scrollContainer.scrollTo({
                    top: scrollContainer.scrollHeight,
                    behavior: 'smooth'
                });
            }

            // Also scroll the parent window itself as a fallback
            window.parent.scrollTo({
                top: window.parent.document.body.scrollHeight,
                behavior: 'smooth'
            });
        } catch (err) {
            try {
                window.parent.scrollTo({
                    top: window.parent.document.body.scrollHeight,
                    behavior: 'smooth'
                });
            } catch (e) {}
        }
    }

    // Staggered triggers to ensure smooth scroll after card and image rendering
    requestAnimationFrame(() => autoScrollToLatest());
    setTimeout(autoScrollToLatest, 150);
    setTimeout(autoScrollToLatest, 400);
    setTimeout(autoScrollToLatest, 800);
    setTimeout(autoScrollToLatest, 1500);
</script>
""", unsafe_allow_javascript=True)

# ---------------------------------------------------------------------------
# Interactive Chat Input Bar
# ---------------------------------------------------------------------------
chat_prompt = st.chat_input("Ask Vira anything about saree weaves, styling, or describe a look...")
if chat_prompt:
    process_search_query(user_text=chat_prompt)
    st.rerun()
