"""
LangChain AI Agent module powered by Google Gemini (with resilient multi-model fallback).
Defines explicit function-calling tool schema for fine-grained visual saree similarity search.
"""

import os
import json
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.search_engine import SareeSearchEngine

# Global singleton search engine
search_engine = SareeSearchEngine.get_instance()

# ---------------------------------------------------------------------------
# Tool Input Schemas
# ---------------------------------------------------------------------------

class FindSimilarSareesInput(BaseModel):
    image_url: Optional[str] = Field(
        default=None,
        description="Public HTTP/HTTPS URL of the saree image to search for visual lookalikes."
    )
    image_base64: Optional[str] = Field(
        default=None,
        description="Base64 encoded string of the query saree image (used when user uploads a file)."
    )
    top_k: int = Field(
        default=6,
        ge=1,
        le=12,
        description="Number of closest visual matches to retrieve (default: 6, max: 12)."
    )
    fabric_filter: Optional[str] = Field(
        default=None,
        description="Optional filter for specific fabric type: 'Kanchipuram Silk', 'Banarasi', 'Organza', 'Munga Crape', 'Pashmina', 'Tussar', 'Tissue'."
    )

class SearchByDescriptionInput(BaseModel):
    query: str = Field(
        description="Text description of the saree, e.g. 'royal blue organza saree with gold zari border' or 'pink banarasi saree under 5000'."
    )
    top_k: int = Field(
        default=6,
        ge=1,
        le=12,
        description="Number of matches to retrieve."
    )

# ---------------------------------------------------------------------------
# Callable LangChain Tools
# ---------------------------------------------------------------------------

@tool(args_schema=FindSimilarSareesInput)
def find_similar_sarees(
    image_url: Optional[str] = None,
    image_base64: Optional[str] = None,
    top_k: int = 6,
    fabric_filter: Optional[str] = None
) -> str:
    """
    Search the Byrappa Silks catalogue for visually similar sarees matching a query image.
    Uses multi-signal retrieval (FashionCLIP embeddings + HSV colour histogram re-ranking).
    """
    image_source = image_url if (image_url and image_url.strip()) else image_base64
    if not image_source:
        return json.dumps({
            "status": "error",
            "message": "No query image provided. Please provide an image_url or image_base64."
        })

    try:
        results = search_engine.search_by_image(
            image_source=image_source,
            top_k=top_k,
            fabric_filter=fabric_filter
        )

        return json.dumps({
            "status": "success",
            "total_matches": len(results),
            "results": results
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Visual search failed: {str(e)}"
        })

@tool(args_schema=SearchByDescriptionInput)
def search_sarees_by_text(query: str, top_k: int = 6) -> str:
    """
    Search the Byrappa Silks catalogue using natural language text descriptions
    (e.g., color, fabric, motif, price preferences).
    """
    try:
        results = search_engine.search_by_text(query_text=query, top_k=top_k)
        return json.dumps({
            "status": "success",
            "total_matches": len(results),
            "results": results
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Text search failed: {str(e)}"
        })

# List of tools exposed to the agent
AGENT_TOOLS = [find_similar_sarees, search_sarees_by_text]
TOOL_MAP = {tool.name: tool for tool in AGENT_TOOLS}

# ---------------------------------------------------------------------------
# Agent Creation & System Prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are "Vira", an elite AI Saree Stylist and Visual Textile Consultant at Byrappa Silks (Bengaluru Heritage Silk House Estd. 1928).
You possess deep mastery of Indian textiles, fabrics (Kanchipuram pure silk, Banarasi brocade, Organza tissue, Munga Crape, Pashmina, Tissue silk), traditional weaves, zari work, pallu motifs, and colour harmony.

CRITICAL PRESENTATION RULES:
1. When finding visual matches or searching sarees:
   - Call the appropriate tool (`find_similar_sarees` or `search_sarees_by_text`).
   - The UI automatically renders interactive product cards with images, match affinity %, weave/fabric, color, SKU, price, discounts, and match explanations.
   - DO NOT output numbered lists, bullet points, or repetitive text descriptions of the individual saree products.
   - Output ONLY a concise **Stylist Drape Recommendation** (2-4 sentences max):
     * Recommend how to drape the saree (e.g. crisp pleated Nivi drape, flowing open pallu, seedha pallu).
     * Recommend blouse necklines/fabrics and complementary jewelry (e.g. temple gold jewelry, uncut polki, pearls).
     * Suggest ideal occasions for this look (e.g. wedding muhurtham, evening reception, festive celebration).

2. When the user asks conversational styling questions (e.g., drape tips, fabric care, blouse ideas, occasion pairings without searching):
   - Provide articulate, warm, and culturally authentic boutique consultation advice.

Tone & Style:
- Warm, elegant, boutique-luxury tone. No emojis.
- Reference authentic Indian textile terminology accurately (e.g. Zari, Pallu, Butta, Border, Kanjivaram, Organza, Crape).
"""

def extract_text_content(content: Any) -> str:
    """Extract clean string text from string, list of dicts, or objects."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            elif hasattr(item, "text"):
                parts.append(str(item.text))
            else:
                parts.append(str(item))
        return "".join(parts)
    return str(content) if content is not None else ""

# Priority list of fast, active Gemini models (flash-lite prioritised for sub-second latency)
FALLBACK_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-3.5-flash",
    "gemini-3-flash-preview",
    "gemini-3.7-flash"
]

class SareeAgent:
    """LangChain Tool-Calling Agent using resilient Gemini models."""

    def __init__(self, api_key: Optional[str] = None):
        self.google_api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY is required to initialize SareeAgent.")

    def _get_llm_instance(self, model_name: str):
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=self.google_api_key,
            temperature=0.3
        )

    def generate_stylist_advice(
        self,
        top_matches: List[Dict[str, Any]],
        user_context: str = ""
    ) -> str:
        """
        Ultra-fast single-turn stylist recommendation generator (sub-second latency).
        Bypasses tool calling when visual matches have already been computed.
        """
        if not top_matches:
            return ""

        top_item = top_matches[0]
        fabric = top_item.get("fabric", "Silk")
        color = top_item.get("primary_color", "")
        name = top_item.get("name", "")

        prompt = f"""You are Vira, Master Stylist at Byrappa Silks (Bengaluru Estd. 1928).
A client is viewing these matched handcrafted sarees:
Primary Saree: {name} (Fabric: {fabric}, Palette: {color}).
Client Query/Context: {user_context if user_context else 'Looking for visual match styling.'}

Provide a concise, luxurious 2-3 sentence Stylist Drape Recommendation:
1. Drape & pleat technique (e.g. structured Nivi drape, open flowing pallu, seedha pallu).
2. Blouse styling & jewelry pairings (e.g. temple gold, uncut polki, contrast raw silk).
3. Ideal occasion (e.g. wedding muhurtham, festive evening, reception).

Output ONLY the 2-3 sentence recommendation. No bullet points, no numbered lists, no emojis."""

        for model_name in FALLBACK_MODELS:
            try:
                llm = self._get_llm_instance(model_name)
                response = llm.invoke([SystemMessage(content="You are Vira, an elite Indian saree stylist at Byrappa Silks. No emojis."), HumanMessage(content=prompt)])
                text = extract_text_content(response.content).strip()
                if text:
                    return text
            except Exception:
                continue

        return ""

    def invoke(self, input_text: str, chat_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Execute multi-turn agent conversation with automatic model failover.
        """
        last_error = None

        for model_name in FALLBACK_MODELS:
            try:
                llm = self._get_llm_instance(model_name)
                llm_with_tools = llm.bind_tools(AGENT_TOOLS)

                messages = [SystemMessage(content=SYSTEM_PROMPT)]

                if chat_history:
                    for msg in chat_history:
                        role = msg.get("role", "")
                        content = msg.get("content", "")
                        if not content:
                            continue
                        if role in ("user", "human"):
                            messages.append(HumanMessage(content=content))
                        elif role in ("assistant", "ai"):
                            messages.append(AIMessage(content=content))

                messages.append(HumanMessage(content=input_text))

                # Invoke model with tools
                ai_response = llm_with_tools.invoke(messages)
                extracted_results = None
                tool_called = False

                # Handle tool calls if triggered by Gemini
                if hasattr(ai_response, "tool_calls") and ai_response.tool_calls:
                    tool_called = True
                    messages.append(ai_response)

                    for tc in ai_response.tool_calls:
                        tool_name = tc.get("name")
                        tool_args = tc.get("args", {})
                        tool_id = tc.get("id", "call_1")

                        if tool_name in TOOL_MAP:
                            target_tool = TOOL_MAP[tool_name]
                            tool_output_str = target_tool.invoke(tool_args)

                            try:
                                parsed = json.loads(tool_output_str)
                                if parsed.get("status") == "success" and parsed.get("results"):
                                    extracted_results = parsed["results"]
                            except Exception:
                                pass

                            messages.append(ToolMessage(content=tool_output_str, tool_call_id=tool_id))

                    final_response = llm.invoke(messages)
                    output_text = extract_text_content(final_response.content)
                else:
                    output_text = extract_text_content(ai_response.content)

                return {
                    "output": output_text,
                    "tool_called": tool_called,
                    "results": extracted_results,
                    "model_used": model_name
                }

            except Exception as e:
                last_error = e
                continue

        # If all LLM candidates failed, raise the final exception
        raise last_error or RuntimeError("All Gemini model endpoints failed.")

def create_saree_agent(api_key: Optional[str] = None) -> SareeAgent:
    """Helper factory function to instantiate SareeAgent."""
    return SareeAgent(api_key=api_key)
