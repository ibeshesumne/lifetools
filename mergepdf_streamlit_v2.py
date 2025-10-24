import streamlit as st

# Check for required packages
try:
    from PyPDF2 import PdfReader, PdfWriter
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    MISSING_PACKAGE = str(e)

from datetime import datetime
import io
import time

if not DEPENDENCIES_AVAILABLE:
    st.error("⚠️ Missing Required Packages")
    st.markdown("""
    This app requires additional packages. Please create a `requirements.txt` file in your app directory with:
    
    ```
    PyPDF2==3.0.1
    reportlab==4.0.7
    ```
    
    **For local use:**
    ```bash
    pip install PyPDF2 reportlab
    ```
    
    **For Streamlit Cloud:**
    Add the requirements.txt file to your repository.
    """)
    st.stop()

def extract_pdf_metadata(pdf_file, filename):
    """Extract metadata and page count from PDF"""
    try:
        pdf_file.seek(0)
        pdf_bytes = pdf_file.read()
        pdf_file.seek(0)
        
        reader = PdfReader(io.BytesIO(pdf_bytes))
        metadata = reader.metadata
        
        # Try to extract date from metadata
        date = None
        if metadata:
            # Check various date fields
            date_fields = ['/CreationDate', '/ModDate']
            for field in date_fields:
                if field in metadata and metadata[field]:
                    date_str = str(metadata[field])
                    # PDF dates are in format: D:YYYYMMDDHHmmSS
                    if date_str.startswith('D:'):
                        date_str = date_str[2:10]
                        try:
                            date = datetime.strptime(date_str, '%Y%m%d')
                            break
                        except:
                            pass
        
        title = str(metadata.get('/Title', '')) if metadata else ''
        author = str(metadata.get('/Author', '')) if metadata else ''
        
        return {
            'title': title if title else filename,
            'author': author,
            'date': date,
            'pages': len(reader.pages),
            'file_bytes': pdf_bytes,
            'filename': filename
        }
    except Exception as e:
        return {
            'error': str(e),
            'filename': filename
        }

def create_cover_page(pdf_info_list, generation_date):
    """Create a cover page PDF with document details"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 1*inch, "Merged PDF Collection")
    
    # Generation date
    c.setFont("Helvetica", 12)
    c.drawCentredString(width/2, height - 1.5*inch, 
                       f"Generated on: {generation_date.strftime('%B %d, %Y')}")
    
    # Summary
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 2.2*inch, "Document Summary")
    
    c.setFont("Helvetica", 11)
    total_pages = sum(info['pages'] for info in pdf_info_list)
    c.drawString(1*inch, height - 2.5*inch, f"Total Documents: {len(pdf_info_list)}")
    c.drawString(1*inch, height - 2.8*inch, f"Total Pages: {total_pages}")
    
    # Document list
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 3.4*inch, "Documents Included (in order):")
    
    y_position = height - 3.8*inch
    c.setFont("Helvetica", 9)
    
    for idx, info in enumerate(pdf_info_list, 1):
        if y_position < 1.5*inch:
            c.showPage()
            y_position = height - 1*inch
            c.setFont("Helvetica", 9)
        
        # Document number and title
        doc_title = info['title'] if info['title'] else f"Document {idx}"
        if len(doc_title) > 70:
            doc_title = doc_title[:67] + "..."
        
        c.setFont("Helvetica-Bold", 9)
        c.drawString(1*inch, y_position, f"{idx}. {doc_title}")
        y_position -= 0.2*inch
        
        # Details
        c.setFont("Helvetica", 8)
        details = []
        if info['date']:
            details.append(f"Date: {info['date'].strftime('%Y-%m-%d')}")
        if info['author']:
            details.append(f"Author: {info['author']}")
        details.append(f"Pages: {info['pages']}")
        
        c.drawString(1.2*inch, y_position, " | ".join(details))
        y_position -= 0.35*inch
    
    c.save()
    buffer.seek(0)
    return buffer

def merge_pdfs_with_cover(pdf_info_list):
    """Merge PDFs with cover page"""
    writer = PdfWriter()
    
    # Create and add cover page
    generation_date = datetime.now()
    cover_buffer = create_cover_page(pdf_info_list, generation_date)
    cover_reader = PdfReader(cover_buffer)
    for page in cover_reader.pages:
        writer.add_page(page)
    
    # Add all PDFs in order
    for info in pdf_info_list:
        reader = PdfReader(io.BytesIO(info['file_bytes']))
        for page in reader.pages:
            writer.add_page(page)
    
    # Write to buffer
    output_buffer = io.BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)
    return output_buffer

# Streamlit UI
st.set_page_config(page_title="PDF Merger", page_icon="📄", layout="wide")

st.title("📄 PDF Merger with Cover Sheet")
st.markdown("Upload multiple PDFs to merge them with an auto-generated cover page, sorted by date.")

# Initialize session state for uploaded files
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []

# File uploader with key to help with re-rendering
uploaded_files = st.file_uploader(
    "Upload PDF files (one at a time works better on mobile)",
    type=['pdf'],
    accept_multiple_files=True,
    help="Upload PDF files to merge. On mobile, uploading 1-2 files at a time is more reliable.",
    key='pdf_uploader'
)

# Process uploaded files
if uploaded_files:
    # Get list of new files
    current_filenames = [f.name for f in uploaded_files]
    existing_filenames = [f['filename'] for f in st.session_state.processed_files]
    
    # Check for new files
    new_files = [f for f in uploaded_files if f.name not in existing_filenames]
    
    if new_files:
        with st.spinner(f"Processing {len(new_files)} new file(s)..."):
            for pdf_file in new_files:
                try:
                    info = extract_pdf_metadata(pdf_file, pdf_file.name)
                    if 'error' not in info:
                        st.session_state.processed_files.append(info)
                        st.success(f"✅ Added: {pdf_file.name}")
                    else:
                        st.error(f"❌ Error reading {pdf_file.name}: {info['error']}")
                except Exception as e:
                    st.error(f"❌ Failed to process {pdf_file.name}: {str(e)}")
                time.sleep(0.1)  # Small delay to prevent overwhelming mobile devices

# Display current files
if st.session_state.processed_files:
    st.success(f"✅ {len(st.session_state.processed_files)} file(s) ready to merge")
    
    # Sort by date
    sorted_files = sorted(
        st.session_state.processed_files,
        key=lambda x: x['date'] if x['date'] else datetime.max
    )
    
    # Display preview
    st.subheader("📋 Document Preview (Sorted by Date)")
    
    # Show table of files
    for idx, info in enumerate(sorted_files, 1):
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                title = info['title'] if info['title'] else info['filename']
                date_str = info['date'].strftime('%Y-%m-%d') if info['date'] else 'No date'
                st.markdown(f"**{idx}. {title}**")
                st.caption(f"📅 {date_str} | 📄 {info['pages']} pages | ✍️ {info['author'] if info['author'] else 'Unknown'}")
            with col2:
                if st.button("🗑️", key=f"remove_{idx}", help="Remove this file"):
                    st.session_state.processed_files = [
                        f for f in st.session_state.processed_files 
                        if f['filename'] != info['filename']
                    ]
                    st.rerun()
    
    st.divider()
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.processed_files = []
            st.rerun()
    
    with col2:
        if st.button("🔗 Merge PDFs", type="primary", use_container_width=True):
            with st.spinner("Merging PDFs..."):
                try:
                    merged_pdf = merge_pdfs_with_cover(sorted_files)
                    
                    # Generate filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"merged_pdfs_{timestamp}.pdf"
                    
                    st.success("✅ PDFs merged successfully!")
                    
                    # Download button
                    st.download_button(
                        label="⬇️ Download Merged PDF",
                        data=merged_pdf,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error merging PDFs: {str(e)}")
                    st.exception(e)
else:
    st.info("👆 Upload PDF files to get started")
    
    with st.expander("ℹ️ How to use (especially on mobile)"):
        st.markdown("""
        **For best results on Android:**
        1. **Upload files one or two at a time** - This is more reliable than uploading many files at once
        2. **Wait for confirmation** - Each file will show a ✅ when successfully added
        3. **Add more files** - Use the same upload button to add more PDFs
        4. **Review your files** - Check the list to ensure all PDFs are loaded
        5. **Remove mistakes** - Use the 🗑️ button next to any file you want to remove
        6. **Merge** - Click "Merge PDFs" when ready
        7. **Download** - Save your merged PDF with the cover sheet
        
        **Features:**
        - Automatic sorting by document date
        - Cover page with document details
        - Preserves all pages from all documents
        - Works on mobile and desktop
        - Files persist until you clear them or merge
        """)

st.markdown("---")
st.markdown("*Built with Streamlit*")