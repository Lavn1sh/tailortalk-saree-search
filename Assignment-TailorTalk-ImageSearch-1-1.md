TailorTalk

Your Mission
Build an AI agent tool that can find visually similar clothing from an image dataset. The agent should chat naturally with the user, understand when a similarity search is being asked for, take in an image (upload or link), search a vector index behind the scenes, and return the closest matches with their
scores.

Dataset
The image database is available in the file: byrappa_tejas_31july.csv
This is a fashion catalogue of sarees — every image belongs to the same broad category, and the real differences sit in fine detail: fabric, weave, print, colour combination, border and pallu work.
Process, embed and index this dataset yourself.

Technical Stack Requirements
• Vector Database: Store and search the image embeddings using a vector store such as Pinecone, Qdrant, ChromaDB, or FAISS.
• Agent Framework: Expose the search logic as a callable tool with a clear input/output schema, using LangChain, LlamaIndex, or a comparable function-calling setup.
• Frontend: Build the chat interface using Streamlit or Gradio.

Search Quality
The quality of the matches is what is being assessed here. A basic embedding search will return loose, generic results on this dataset, since every image is the same kind of garment and the differences are fine-grained. Your results should be visually close to the query — comparable in colour, fabric, pattern and overall design — and should hold up on repeated testing with different
query images. How you achieve that is left to you.

Your Final Submission
• Deploy the application on a platform like Streamlit Community Cloud, Hugging Face Spaces, or Render. It must work out of the box, with no local setup on the reviewer's side.
• Your submission must include a working app URL, where I will test the search live, along with the Github code link.
• Include a README covering setup steps, your model / vector-DB / framework choices, what you did to improve result quality, and any assumptions or trade-offs.
Hint: The tool schema the LLM calls, and the quality of what it returns, decide the outcome here.