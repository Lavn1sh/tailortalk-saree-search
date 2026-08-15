"""
Bespoke UI components and cozy luxury atelier styling for TailorTalk Saree Consultant.
Warm light sage / olive green palette, cozy editorial serif typography, zero emojis.
Designed for a natural, harmonious reading and interaction flow.
"""

import streamlit as st
from typing import List, Dict, Any, Optional

def inject_boutique_css():
    """Inject bespoke stylesheet for warm, cozy light green luxury atelier experience."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,400;1,9..144,500&family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Warm Light Green (Sage & Heritage Olive) Design Tokens */
    :root {
        --color-bg-base: #F9FAF7;
        --color-bg-sidebar: #EDF2EA;
        --color-surface-card: #FFFFFF;
        --color-surface-hover: #F5F9F4;
        --color-accent-green: #3D6B4F;
        --color-accent-green-dark: #2B4E38;
        --color-accent-green-soft: #E6F0E4;
        --color-accent-gold: #C5A059;
        --color-accent-gold-soft: #FAF5E8;
        --color-text-primary: #1E2621;
        --color-text-secondary: #4F5E54;
        --color-text-subtle: #7D8D82;
        --color-border-subtle: #D6E0D3;
        --color-border-hover: #3D6B4F;
        --color-tag-bg: #EDF3EB;
        --color-success: #287038;
        --color-success-bg: #E2F2E4;
        --font-serif: 'Fraunces', 'Lora', Georgia, serif;
        --font-serif-sub: 'Lora', Georgia, serif;
        --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Base Page & App Styling */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        font-family: var(--font-sans) !important;
        color: var(--color-text-primary) !important;
        background-color: var(--color-bg-base) !important;
        -webkit-font-smoothing: antialiased;
    }

    header[data-testid="stHeader"] {
        background-color: var(--color-bg-base) !important;
    }

    /* Cozy Headings */
    h1, h2, h3, h4, .serif-font {
        font-family: var(--font-serif) !important;
        font-weight: 600 !important;
        color: var(--color-text-primary) !important;
        letter-spacing: -0.015em;
    }

    h1 {
        font-size: 2.2rem !important;
        line-height: 1.25 !important;
    }

    h2 {
        font-size: 1.65rem !important;
        line-height: 1.3 !important;
    }

    h3 {
        font-size: 1.35rem !important;
        line-height: 1.35 !important;
    }

    p, span, label, div {
        color: var(--color-text-primary);
    }

    /* Container Layout */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 5rem !important;
        max-width: 1160px !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: var(--color-bg-sidebar) !important;
        border-right: 1px solid var(--color-border-subtle) !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stSidebarContent"] {
        background-color: var(--color-bg-sidebar) !important;
        padding: 1.5rem 1.2rem !important;
    }

    .sidebar-brand {
        text-align: left;
        padding: 4px 0 16px 0;
        border-bottom: 1px solid var(--color-border-subtle);
        margin-bottom: 18px;
    }

    .sidebar-brand-crest {
        font-size: 0.70rem;
        font-weight: 700;
        letter-spacing: 0.18em;
        color: var(--color-accent-green);
        text-transform: uppercase;
        margin-bottom: 3px;
    }

    .sidebar-brand-title {
        font-family: var(--font-serif);
        font-size: 1.65rem;
        font-weight: 600;
        color: var(--color-text-primary);
        line-height: 1.2;
        margin: 2px 0 0 0;
    }

    .sidebar-brand-subtitle {
        font-size: 0.72rem;
        font-weight: 500;
        color: var(--color-text-secondary);
        letter-spacing: 0.08em;
    }

    .index-status-card {
        background: var(--color-surface-card);
        border: 1px solid var(--color-border-subtle);
        border-radius: 8px;
        padding: 10px 14px;
        margin: 14px 0;
        font-size: 0.82rem;
        color: var(--color-text-secondary);
        box-shadow: 0 1px 4px rgba(30, 38, 33, 0.03);
    }

    .index-status-card strong {
        color: var(--color-accent-green);
    }

    /* Atelier Banner Header */
    .atelier-banner {
        background: var(--color-surface-card);
        border: 1px solid var(--color-border-subtle);
        border-radius: 14px;
        padding: 28px 34px;
        margin-bottom: 24px;
        position: relative;
        box-shadow: 0 4px 18px rgba(30, 38, 33, 0.04);
    }

    .atelier-banner::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        border-top-left-radius: 14px;
        border-top-right-radius: 14px;
        background: linear-gradient(90deg, #3D6B4F, #C5A059, #3D6B4F);
    }

    .atelier-crest {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.20em;
        text-transform: uppercase;
        color: var(--color-accent-green);
        margin-bottom: 8px;
    }

    .atelier-title {
        font-family: var(--font-serif);
        font-size: 2.15rem;
        font-weight: 600;
        line-height: 1.22;
        color: var(--color-text-primary);
        margin: 0 0 10px 0;
    }

    .atelier-desc {
        color: var(--color-text-secondary);
        font-size: 0.94rem;
        line-height: 1.55;
        max-width: 840px;
        margin: 0;
    }

    .feature-pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 16px;
    }

    .feature-pill {
        font-size: 0.73rem;
        font-weight: 500;
        padding: 4px 11px;
        border-radius: 6px;
        background: var(--color-accent-green-soft);
        border: 1px solid rgba(61, 107, 79, 0.22);
        color: var(--color-accent-green);
    }

    /* Streamlit Tabs & Form Controls */
    div[data-baseweb="tab-list"] {
        border-bottom: 1px solid var(--color-border-subtle) !important;
        gap: 8px !important;
        background-color: transparent !important;
    }

    div[data-baseweb="tab"] {
        font-family: var(--font-sans) !important;
        font-size: 0.90rem !important;
        font-weight: 500 !important;
        color: var(--color-text-secondary) !important;
        padding: 10px 16px !important;
        border-radius: 6px 6px 0 0 !important;
        background-color: transparent !important;
    }

    div[data-baseweb="tab"][aria-selected="true"] {
        color: var(--color-accent-green) !important;
        font-weight: 600 !important;
        border-bottom: 2px solid var(--color-accent-green) !important;
    }

    /* File Uploader */
    div[data-testid="stFileUploader"] {
        background-color: var(--color-bg-base) !important;
        border: 1.5px dashed var(--color-border-subtle) !important;
        border-radius: 10px !important;
        padding: 14px !important;
    }

    div[data-testid="stFileUploader"]:hover {
        border-color: var(--color-accent-green) !important;
    }

    /* Slider styling */
    div[data-testid="stSlider"] [role="slider"] {
        background-color: var(--color-accent-green) !important;
        border-color: var(--color-accent-green) !important;
    }

    /* Selectbox styling */
    div[data-baseweb="select"] > div {
        background-color: var(--color-surface-card) !important;
        border: 1px solid var(--color-border-subtle) !important;
        border-radius: 8px !important;
        color: var(--color-text-primary) !important;
    }

    /* Text Inputs */
    div[data-testid="stTextInput"] input {
        background-color: var(--color-surface-card) !important;
        border: 1px solid var(--color-border-subtle) !important;
        border-radius: 8px !important;
        color: var(--color-text-primary) !important;
        font-family: var(--font-sans) !important;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: var(--color-accent-green) !important;
        box-shadow: 0 0 0 1px var(--color-accent-green) !important;
    }

    /* Buttons */
    div.stButton > button {
        background-color: var(--color-surface-card);
        color: var(--color-text-primary);
        border: 1px solid var(--color-border-subtle);
        border-radius: 8px;
        font-family: var(--font-sans);
        font-size: 0.85rem;
        font-weight: 500;
        padding: 7px 14px;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(30, 38, 33, 0.04);
    }

    div.stButton > button:hover {
        background-color: var(--color-surface-hover);
        border-color: var(--color-accent-green);
        color: var(--color-accent-green);
        transform: translateY(-1px);
        box-shadow: 0 3px 8px rgba(61, 107, 79, 0.12);
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3D6B4F 0%, #2B4E38 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(61, 107, 79, 0.25) !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #2B4E38 0%, #1E3727 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(61, 107, 79, 0.35) !important;
    }

    /* Consultation Stream & Chat Message Styling */
    div[data-testid="stChatMessage"], .stChatMessage {
        background-color: var(--color-surface-card) !important;
        border: 1px solid var(--color-border-subtle) !important;
        border-radius: 12px !important;
        padding: 18px 22px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 2px 10px rgba(30, 38, 33, 0.03) !important;
    }

    div[data-testid="stChatMessage"] p, 
    div[data-testid="stChatMessage"] div,
    .stChatMessage p, 
    .stChatMessage div {
        color: var(--color-text-primary) !important;
        font-family: var(--font-sans) !important;
        font-size: 0.95rem;
        line-height: 1.62;
    }

    div[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"] {
        background-color: var(--color-accent-green-soft) !important;
        border: 1px solid rgba(61, 107, 79, 0.2) !important;
    }

    /* Stylist Drape Recommendation Callout Box */
    .stylist-recommendation-box {
        background: #F4F8F3;
        border: 1px solid #D2E2D0;
        border-left: 4px solid var(--color-accent-green);
        border-radius: 8px;
        padding: 14px 18px;
        margin-top: 16px;
        margin-bottom: 6px;
        font-size: 0.92rem;
        line-height: 1.58;
        color: var(--color-text-primary);
        box-shadow: 0 1px 4px rgba(30, 38, 33, 0.03);
    }

    .stylist-recommendation-title {
        font-family: var(--font-serif-sub);
        font-weight: 600;
        color: var(--color-accent-green);
        font-size: 0.96rem;
        margin-bottom: 5px;
        letter-spacing: -0.01em;
    }

    .stylist-recommendation-text {
        color: var(--color-text-primary);
        font-size: 0.91rem;
        line-height: 1.55;
    }

    /* Chat Input Bar at Bottom */
    div[data-testid="stChatInput"] {
        background-color: transparent !important;
    }

    div[data-testid="stChatInput"] textarea {
        background-color: var(--color-surface-card) !important;
        border: 1px solid var(--color-border-subtle) !important;
        border-radius: 10px !important;
        color: var(--color-text-primary) !important;
        font-family: var(--font-sans) !important;
        font-size: 0.92rem !important;
        box-shadow: 0 2px 10px rgba(30, 38, 33, 0.05) !important;
    }

    div[data-testid="stChatInput"] textarea:focus {
        border-color: var(--color-accent-green) !important;
        box-shadow: 0 0 0 1px var(--color-accent-green), 0 3px 12px rgba(61, 107, 79, 0.10) !important;
    }

    div[data-testid="stChatInput"] button {
        color: var(--color-accent-green) !important;
    }

    /* Saree Showcase Product Cards */
    .saree-card {
        background: var(--color-surface-card);
        border: 1px solid var(--color-border-subtle);
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 18px;
        transition: all 0.28s ease;
        box-shadow: 0 2px 10px rgba(30, 38, 33, 0.04);
        display: flex;
        flex-direction: column;
        height: 100%;
        position: relative;
    }

    .saree-card:hover {
        transform: translateY(-4px);
        background: var(--color-surface-hover);
        border-color: var(--color-border-hover);
        box-shadow: 0 10px 24px rgba(61, 107, 79, 0.12);
    }

    .card-img-wrapper {
        position: relative;
        width: 100%;
        height: 230px;
        border-radius: 8px;
        overflow: hidden;
        background-color: #EEF3EC;
        margin-bottom: 12px;
    }

    .card-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.35s ease;
    }

    .saree-card:hover .card-img {
        transform: scale(1.035);
    }

    .score-ribbon {
        position: absolute;
        top: 8px;
        right: 8px;
        background: #F9FCF8;
        color: var(--color-accent-green);
        border: 1px solid var(--color-border-subtle);
        font-family: var(--font-sans);
        font-size: 0.70rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        box-shadow: 0 2px 6px rgba(30, 38, 33, 0.08);
    }

    .saree-title {
        font-family: var(--font-serif-sub);
        color: var(--color-text-primary);
        font-size: 1.05rem;
        font-weight: 600;
        line-height: 1.35;
        margin: 0 0 8px 0;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        min-height: 2.8rem;
    }

    .meta-tag-row {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin-bottom: 10px;
    }

    .meta-tag {
        font-size: 0.70rem;
        font-weight: 500;
        padding: 2px 8px;
        border-radius: 4px;
        background: var(--color-tag-bg);
        color: var(--color-text-secondary);
        border: 1px solid var(--color-border-subtle);
    }

    .meta-fabric {
        background: var(--color-accent-green-soft);
        color: var(--color-accent-green);
        border-color: rgba(61, 107, 79, 0.22);
    }

    .stylist-note {
        font-size: 0.76rem;
        color: var(--color-text-secondary);
        background: #F4F8F3;
        border-left: 3px solid var(--color-accent-green);
        padding: 6px 10px;
        border-radius: 0 4px 4px 0;
        margin-bottom: 12px;
        line-height: 1.45;
    }

    .price-row {
        display: flex;
        align-items: baseline;
        gap: 8px;
        margin-top: auto;
        margin-bottom: 12px;
    }

    .price-current {
        color: var(--color-text-primary);
        font-size: 1.22rem;
        font-weight: 700;
        font-family: var(--font-sans);
    }

    .price-original {
        color: var(--color-text-subtle);
        font-size: 0.85rem;
        text-decoration: line-through;
    }

    .price-discount-tag {
        background: var(--color-success-bg);
        color: var(--color-success);
        font-size: 0.70rem;
        font-weight: 600;
        padding: 2px 6px;
        border-radius: 4px;
    }

    .action-link {
        display: block;
        text-align: center;
        background: var(--color-bg-base);
        color: var(--color-accent-green) !important;
        text-decoration: none !important;
        font-size: 0.82rem;
        font-weight: 600;
        padding: 8px 12px;
        border-radius: 6px;
        border: 1px solid var(--color-border-subtle);
        transition: all 0.2s ease;
    }

    .action-link:hover {
        background: var(--color-accent-green);
        color: #FFFFFF !important;
        border-color: var(--color-accent-green);
        box-shadow: 0 2px 8px rgba(61, 107, 79, 0.2);
    }

    /* Sample Inspiration Cards */
    .sample-pill-card {
        background: var(--color-surface-card);
        border: 1px solid var(--color-border-subtle);
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        transition: all 0.22s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 1px 4px rgba(30, 38, 33, 0.03);
    }

    .sample-pill-card:hover {
        border-color: var(--color-accent-green);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(61, 107, 79, 0.10);
    }

    .sample-thumb {
        width: 100%;
        height: 95px;
        border-radius: 6px;
        object-fit: cover;
        margin-bottom: 8px;
    }

    .sample-name {
        font-family: var(--font-serif-sub);
        font-size: 0.90rem;
        font-weight: 600;
        color: var(--color-text-primary);
        line-height: 1.25;
        margin-bottom: 4px;
    }

    .sample-badge {
        font-size: 0.68rem;
        font-weight: 500;
        color: var(--color-accent-green);
        background: var(--color-accent-green-soft);
        padding: 2px 6px;
        border-radius: 4px;
        display: inline-block;
    }

    /* Custom Slim Warm Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: var(--color-bg-base);
    }
    ::-webkit-scrollbar-thumb {
        background: var(--color-border-subtle);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--color-accent-green);
    }
    </style>
    """, unsafe_allow_html=True)

def render_boutique_header():
    """Render the warm heritage atelier banner."""
    st.markdown("""
    <div class="atelier-banner">
        <div class="atelier-crest">BYRAPPA SILKS ATELIER · ESTABLISHED 1928</div>
        <h1 class="atelier-title">Haute Couture Saree Visual Stylist</h1>
        <p class="atelier-desc">
            Discover exquisite Indian handlooms and weaves through multi-signal visual similarity search. 
            Our consultant analyzes weave texture, zari density, pallu artistry, and color harmony to find exact and complementary lookalikes.
        </p>
        <div class="feature-pill-row">
            <span class="feature-pill">FashionCLIP Embeddings</span>
            <span class="feature-pill">HSV Color & Weave Re-ranking</span>
            <span class="feature-pill">1,069 Handcrafted Sarees</span>
            <span class="feature-pill">Gemini 3.7 Flash Stylist</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_product_card(item: Dict[str, Any]):
    """Render an editorial-grade product card with rich metadata."""
    name = item.get("name", "Pure Silk Saree")
    image_url = item.get("image_url", "")
    sku = item.get("sku", "")
    retail = item.get("retail_price", 0)
    discounted = item.get("discounted_price", 0)
    fabric = item.get("fabric", "Silk Saree")
    color = item.get("primary_color", "")
    score_pct = item.get("similarity_pct", round(item.get("similarity_score", 0) * 100, 1))
    explanation = item.get("match_explanation", "Visually cohesive drape match.")
    website_link = item.get("website_link", "#")

    try:
        disc_int = int(float(discounted))
        ret_int = int(float(retail))
    except (ValueError, TypeError):
        disc_int = 0
        ret_int = 0

    discount_tag_html = ""
    if ret_int > disc_int and disc_int > 0:
        pct_off = round(((ret_int - disc_int) / ret_int) * 100)
        discount_tag_html = f'<span class="price-discount-tag">{pct_off}% OFF</span>'

    card_html = f"""
    <div class="saree-card">
        <div class="card-img-wrapper">
            <img src="{image_url}" alt="{name}" class="card-img" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=400';" />
            <div class="score-ribbon">{score_pct}% Match</div>
        </div>
        <div class="saree-title" title="{name}">{name}</div>
        <div class="meta-tag-row">
            <span class="meta-tag meta-fabric">{fabric}</span>
            {f'<span class="meta-tag">{color}</span>' if color else ''}
            <span class="meta-tag">SKU: {sku}</span>
        </div>
        <div class="stylist-note">
            {explanation}
        </div>
        <div class="price-row">
            <span class="price-current">₹{disc_int:,}</span>
            {f'<span class="price-original">₹{ret_int:,}</span>' if ret_int > disc_int else ''}
            {discount_tag_html}
        </div>
        <a href="{website_link}" target="_blank" rel="noopener noreferrer" class="action-link">
            View in Boutique →
        </a>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def render_results_grid(results: List[Dict[str, Any]], num_cols: int = 3):
    """Render a responsive grid of matched saree product cards."""
    if not results:
        return

    cols = st.columns(num_cols)
    for idx, item in enumerate(results):
        with cols[idx % num_cols]:
            render_product_card(item)

def render_stylist_recommendation(recommendation_text: str):
    """Render an editorial stylist drape & pairing recommendation box at the end of matches."""
    if not recommendation_text or not recommendation_text.strip():
        return
    st.markdown(f"""
    <div class="stylist-recommendation-box">
        <div class="stylist-recommendation-title">Stylist Drape & Pairing Recommendation</div>
        <div class="stylist-recommendation-text">{recommendation_text.strip()}</div>
    </div>
    """, unsafe_allow_html=True)

def get_default_drape_advice(fabric: str = "Silk", color: str = "") -> str:
    """Generate authentic, weave-specific drape advice when direct search is performed."""
    fab_lower = (fabric or "").lower()
    if "kanchi" in fab_lower or "kanjivaram" in fab_lower:
        return "For this regal Kanchipuram silk weave, style with crisp, structured Nivi pleats and a contrast raw silk or gold zari embroidered blouse. Complement the look with traditional antique temple jewelry for weddings and auspicious occasions."
    elif "banaras" in fab_lower or "pashmina" in fab_lower:
        return "Drape this opulent Banarasi brocade with a grand open floating pallu to showcase the intricate kadwa zari motifs. Pair with an elbow-sleeve silk blouse and heritage gold jhumkas."
    elif "organza" in fab_lower or "tissue" in fab_lower:
        return "Style this lightweight, sheer organza with a delicate pinned drape and a sleeveless or sweetheart-neckline satin blouse. Accentuate with minimalist polki or pearl accessories for evening receptions."
    elif "munga" in fab_lower or "crape" in fab_lower or "georgette" in fab_lower:
        return "This fluid, lightweight drape pairs effortlessly with a contemporary contrast blouse and statement silver-gilt earrings—ideal for cocktail evenings and festive get-togethers."
    else:
        return "Drape with neat, classic pleats to emphasize the weave's natural luster and border craftsmanship. Pair with handcrafted jewelry and a tailored contrast blouse."

# Curated sample sarees from the authentic Byrappa dataset for 1-click test showcase (No emojis)
SAMPLE_INSPIRATIONS = [
    {
        "title": "Pink Pashmina Banarasi",
        "fabric": "Banarasi Brocade",
        "color": "Rose Pink",
        "image_url": "https://byrappasilk.in/storage/uploads/bsrKlEUvx7qmaeA5iC1nEQymK9K4CcA3u9t6LC7G.webp",
        "sku": "QS204820",
        "query_prompt": "Find sarees visually similar to this Pink Pashmina Banarasi with gold zari border."
    },
    {
        "title": "White & Gold Organza",
        "fabric": "Organza Tissue",
        "color": "Ivory Gold",
        "image_url": "https://byrappasilk.in/storage/uploads/1cssgxdhsRwGnhP955n8kvXnhiWPEyThh9sbIaAI.webp",
        "sku": "QA255622",
        "query_prompt": "Find sarees with sheer shimmer similar to this White & Gold Organza Tissue drape."
    },
    {
        "title": "Floral Crimson Organza",
        "fabric": "Printed Organza",
        "color": "Crimson Red",
        "image_url": "https://byrappasilk.in/storage/uploads/qg47mgXZJa6Hkt1a0Aglo3GRHjpGUffdBTyBpORV.webp",
        "sku": "QA254685",
        "query_prompt": "Find sarees matching this Crimson Red Floral Organza with artisanal borders."
    },
    {
        "title": "Cobalt Blue Munga Crape",
        "fabric": "Munga Crape",
        "color": "Royal Blue",
        "image_url": "https://byrappasilk.in/storage/uploads/DOh6Yh13wqTpvxICi9rpCGyRG72bAtKTM2bhkxMi.webp",
        "sku": "AA313403",
        "query_prompt": "Find sarees similar in shade and texture to this Cobalt Blue Munga Crape."
    }
]
