import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime
import io
import os

def extract_pdf_metadata(pdf_file):
    """Extract metadata and page count from PDF"""
    try:
        pdf_file.seek(0)
        reader = PdfReader(pdf_file)
        metadata = reader.metadata
        
        # Try to extract date from metadata
        date = None
        if metadata:
            # Check various date fields
            date_fields = ['/CreationDate', '/ModDate']
            for field in date_fields:
                if field in metadata and metadata[field]:
                    date_str = metadata[field]
                    # PDF dates are in format: D:YYYYMMDDHHmmSS
                    if date_str.startswith('D:'):
                        date_str = date_str[2:10]
                        try:
                            date = datetime.strptime(date_str, '%Y%m%d')
                            break
                        except:
                            pass
        
        title = metadata.get('/Title', '') if metadata else ''
        author = metadata.get('/Author', '') if metadata else ''
        
        return {
            'title': title if title else pdf_file.name,
            'author': author,
            'date': date,
            'pages': len(reader.pages),
            'file_obj': pdf_file
        }
    except Exception as e:
        st.error(f"Error reading {pdf_file.name}: {str(e)}")
        return None

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
        info['file_obj'].seek(0)
        reader = PdfReader(info['file_obj'])
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

# File uploader
uploaded_files = st.file_uploader(
    "Upload PDF files",
    type=['pdf'],
    accept_multiple_files=True,
    help="Upload 2 or more PDF files to merge"
)

if uploaded_files and len(uploaded_files) > 0:
    st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
    
    # Extract metadata
    with st.spinner("Analyzing PDFs..."):
        pdf_info_list = []
        for pdf_file in uploaded_files:
            info = extract_pdf_metadata(pdf_file)
            if info:
                pdf_info_list.append(info)
    
    if pdf_info_list:
        # Sort by date (files without dates go to the end)
        pdf_info_list.sort(key=lambda x: x['date'] if x['date'] else datetime.max)
        
        # Display preview
        st.subheader("📋 Document Preview (Sorted by Date)")
        
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        with col1:
            st.markdown("**Document Title**")
        with col2:
            st.markdown("**Date**")
        with col3:
            st.markdown("**Pages**")
        with col4:
            st.markdown("**Author**")
        
        st.divider()
        
        for idx, info in enumerate(pdf_info_list, 1):
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            with col1:
                title = info['title'] if info['title'] else f"Document {idx}"
                st.text(title[:50] + "..." if len(title) > 50 else title)
            with col2:
                st.text(info['date'].strftime('%Y-%m-%d') if info['date'] else 'No date')
            with col3:
                st.text(info['pages'])
            with col4:
                st.text(info['author'][:15] if info['author'] else '-')
        
        st.divider()
        
        # Merge button
        if st.button("🔗 Merge PDFs", type="primary", use_container_width=True):
            with st.spinner("Merging PDFs..."):
                try:
                    merged_pdf = merge_pdfs_with_cover(pdf_info_list)
                    
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
    else:
        st.error("❌ Could not read any of the uploaded PDFs. Please check the files and try again.")
else:
    st.info("👆 Upload PDF files to get started")
    
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        1. **Upload PDFs**: Click the upload button and select 2 or more PDF files
        2. **Review**: The app will extract metadata and sort files by date
        3. **Merge**: Click the "Merge PDFs" button
        4. **Download**: Download your merged PDF with an auto-generated cover sheet
        
        **Features:**
        - Automatic sorting by document date
        - Cover page with document details
        - Preserves all pages from all documents
        - Works on mobile and desktop
        """)

st.markdown("---")
st.markdown("*Built with Streamlit*")