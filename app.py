import streamlit as st
import os
from markitdown import MarkItDown
import requests

def format_size(size_bytes):
    """Converts bytes to a human-readable string (KB/MB)."""
    if size_bytes == 0: return "0 B"
    units = ("B", "KB", "MB", "GB")
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.2f} {units[i]}"

def main():
    st.set_page_config(page_title="Universal Doc Converter", page_icon="📝", layout="wide")
    st.title("📝 Universal Document Reader")

    mid = MarkItDown()

    uploaded_files = st.file_uploader(
        "Upload files", 
        type=["docx", "xlsx", "pptx", "pdf", "html", "htm", "zip"],
        accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            base_name = os.path.splitext(file_name)[0]
            temp_path = f"temp_{file_name}"
            
            try:
                # Get Original Size
                original_size = uploaded_file.size
                
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                with st.spinner(f"Converting {file_name}..."):
                    result = mid.convert(temp_path)
                    md_content = result.text_content
                
                # Calculate Converted Size
                converted_size = len(md_content.encode('utf-8'))
                
                with st.expander(f"✅ Processed: {file_name}", expanded=True):
                    # Create Tabs
                    tab1, tab2 = st.tabs(["📄 Content Preview", "📊 File Size Comparison"])
                    
                    with tab1:
                        st.text_area("Markdown Output", md_content, height=300, key=f"p_{file_name}")
                        col1, col2 = st.columns(2)
                        col1.download_button("📥 Download .md", md_content, f"{base_name}.md", "text/markdown", key=f"m_{file_name}")
                        col2.download_button("📥 Download .txt", md_content, f"{base_name}.txt", "text/plain", key=f"t_{file_name}")

                    with tab2:
                        # [NEW] File Size Comparison Logic
                        reduction = 100 * (1 - (converted_size / original_size)) if original_size > 0 else 0
                        
                        st.subheader("Size Analysis")
                        st.table({
                            "Version": ["Original File", "Converted Text"],
                            "Size": [format_size(original_size), format_size(converted_size)]
                        })
                        
                        if reduction > 0:
                            st.success(f"✨ Text version is **{reduction:.1f}% smaller** than the original.")
                        else:
                            st.info("The converted version is roughly the same size as the original.")

            except Exception:
                st.error(f"⚠️ Could not read {file_name}. Please check the format.")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

if __name__ == "__main__":
    main()
