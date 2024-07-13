import sys
import os
import asyncio
import streamlit as st
import time
# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from restack.sdk import restack


async def main():
    # Define Streamlit app
    st.set_page_config(page_title="Ask Llama", page_icon="🦙", layout="centered")

    st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)
    
    st.subheader("Ask a question about GPT-4 Technical Report PDF")
    st.link_button("https://cdn.openai.com/papers/gpt-4.pdf", "https://cdn.openai.com/papers/gpt-4.pdf")
    api_key = st.text_input("OpenAI API Key", type="password")
    query = st.text_input("Query (source: data/gpt-4.pdf)", "What insights from the report?")

    # If the 'Submit' button is clicked
    if st.button("Submit"):
        if not query.strip():
            st.error("Please provide the search query.")
        elif not api_key.strip():
            st.error("Please provide the OpenAI API Key.")
        else:
            try:
                with st.spinner("Processing..."):
                    sdk = restack()
                    response = await sdk.workflow(
                        workflow="PdfWorkflow",
                        id=f"workflow-{int(time.time() * 1000)}-{query.replace(' ', '-')}",
                        args=[query, api_key],
                    )

                # Optionally, display specific parts of the response
                st.markdown("### Answer:")
                st.write(response.get("response", "No summary available."))
                
                st.markdown("### Source:")
                for node in response.get("source_nodes", []):
                    st.markdown(f"**Page {node['node']['metadata']['page_label']}**")
                    st.write(node['node']['text'])

                # Display the response in a more readable format
                st.markdown("### Raw response:")
                st.json(response)
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())