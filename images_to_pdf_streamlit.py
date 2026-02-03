"""
Streamlit app: upload PNG/JPEG images and merge them into a single PDF for download.
"""
import streamlit as st

try:
    from PyPDF2 import PdfReader, PdfWriter
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    from PIL import Image
    from PIL.ExifTags import TAGS
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
    This app requires additional packages. Install with:

    ```bash
    pip install PyPDF2 reportlab Pillow
    ```
    """)
    st.stop()


def extract_image_metadata(image_file, filename):
    """Extract metadata from image (JPEG or PNG)."""
    try:
        image_file.seek(0)
        image_bytes = image_file.read()
        image_file.seek(0)

        image = Image.open(io.BytesIO(image_bytes))

        date = None
        author = None
        exif_data = image.getexif() if hasattr(image, "getexif") else None

        if exif_data:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag in ("DateTime", "DateTimeOriginal", "DateTimeDigitized"):
                    try:
                        date = datetime.strptime(str(value), "%Y:%m:%d %H:%M:%S")
                        break
                    except Exception:
                        pass
                if tag in ("Artist", "Copyright") and value:
                    author = str(value)

        width, height = image.size
        return {
            "file_type": "image",
            "title": filename,
            "author": author or "—",
            "date": date,
            "pages": 1,
            "file_bytes": image_bytes,
            "filename": filename,
            "width": width,
            "height": height,
        }
    except Exception as e:
        return {"error": str(e), "filename": filename}


def create_cover_page(file_info_list, generation_date):
    """Create a cover page PDF listing the images."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 1 * inch, "Images to PDF")

    c.setFont("Helvetica", 12)
    c.drawCentredString(
        width / 2, height - 1.5 * inch,
        f"Generated on: {generation_date.strftime('%B %d, %Y')}"
    )

    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, height - 2.2 * inch, "Images included (in order)")

    y_position = height - 2.6 * inch
    c.setFont("Helvetica", 10)

    for idx, info in enumerate(file_info_list, 1):
        if y_position < 1.5 * inch:
            c.showPage()
            y_position = height - 1 * inch
            c.setFont("Helvetica", 10)

        title = (info.get("title") or info["filename"])[:70]
        if len(info.get("title", "") or info["filename"]) > 70:
            title = title + "..."

        c.drawString(1 * inch, y_position, f"{idx}. {title}")
        y_position -= 0.25 * inch
        details = [f"{info.get('width', '?')}×{info.get('height', '?')}"]
        if info.get("date"):
            details.append(info["date"].strftime("%Y-%m-%d"))
        c.setFont("Helvetica", 9)
        c.drawString(1.2 * inch, y_position, "  ".join(details))
        y_position -= 0.35 * inch
        c.setFont("Helvetica", 10)

    c.save()
    buffer.seek(0)
    return buffer


def image_to_pdf_page(image_bytes):
    """Convert one image (PNG/JPEG) to a single PDF page (fit on letter, centered)."""
    buffer = io.BytesIO()
    image = Image.open(io.BytesIO(image_bytes))
    img_width, img_height = image.size
    page_width, page_height = letter

    scale_x = (page_width - 2 * inch) / img_width
    scale_y = (page_height - 2 * inch) / img_height
    scale = min(scale_x, scale_y)
    new_width = img_width * scale
    new_height = img_height * scale
    x_offset = (page_width - new_width) / 2
    y_offset = (page_height - new_height) / 2

    # Convert image to RGB if needed (ReportLab requires RGB)
    if image.mode == "RGBA":
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[-1])
        image = background
    elif image.mode not in ("RGB", "L"):
        image = image.convert("RGB")

    # ImageReader can accept PIL Image objects directly
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawImage(ImageReader(image), x_offset, y_offset, width=new_width, height=new_height, preserveAspectRatio=True)
    c.save()
    buffer.seek(0)
    return buffer


def merge_images_to_pdf(file_info_list, include_cover=True):
    """Merge image infos into a single PDF; optionally add a cover page."""
    writer = PdfWriter()

    if include_cover and file_info_list:
        generation_date = datetime.now()
        cover_buffer = create_cover_page(file_info_list, generation_date)
        cover_reader = PdfReader(cover_buffer)
        for page in cover_reader.pages:
            writer.add_page(page)

    for info in file_info_list:
        image_pdf_buffer = image_to_pdf_page(info["file_bytes"])
        reader = PdfReader(image_pdf_buffer)
        for page in reader.pages:
            writer.add_page(page)

    output_buffer = io.BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)
    return output_buffer


# --- Streamlit UI ---
st.set_page_config(page_title="Images to PDF", page_icon="🖼️", layout="wide")

st.title("🖼️ Images to PDF")
st.markdown("Upload PNG or JPEG images to merge them into a single PDF and download it.")

if "processed_files" not in st.session_state:
    st.session_state.processed_files = []
if "merged_pdf_bytes" not in st.session_state:
    st.session_state.merged_pdf_bytes = None
if "merged_pdf_filename" not in st.session_state:
    st.session_state.merged_pdf_filename = None

uploaded_files = st.file_uploader(
    "Upload PNG or JPEG images",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
    help="Select one or more image files. On mobile, 1–2 files at a time is more reliable.",
    key="image_uploader",
)

if uploaded_files:
    current_filenames = [f.name for f in uploaded_files]
    existing_filenames = [f["filename"] for f in st.session_state.processed_files]
    new_files = [f for f in uploaded_files if f.name not in existing_filenames]

    if new_files:
        with st.spinner(f"Processing {len(new_files)} new file(s)…"):
            for uploaded_file in new_files:
                try:
                    info = extract_image_metadata(uploaded_file, uploaded_file.name)
                    if "error" not in info:
                        st.session_state.processed_files.append(info)
                        st.success(f"✅ Added: {uploaded_file.name}")
                    else:
                        st.error(f"❌ Error reading {uploaded_file.name}: {info['error']}")
                except Exception as e:
                    st.error(f"❌ Failed to process {uploaded_file.name}: {str(e)}")
                time.sleep(0.1)

if st.session_state.processed_files:
    st.success(f"✅ {len(st.session_state.processed_files)} image(s) ready to merge")

    sorted_files = sorted(
        st.session_state.processed_files,
        key=lambda x: x["date"] if x["date"] else datetime.max,
    )

    st.subheader("📋 Preview (sorted by date)")
    for idx, info in enumerate(sorted_files, 1):
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                title = info.get("title") or info["filename"]
                date_str = info["date"].strftime("%Y-%m-%d") if info["date"] else "No date"
                size_str = f"{info.get('width', '?')}×{info.get('height', '?')}"
                st.markdown(f"**{idx}. {title}**")
                st.caption(f"📅 {date_str}  |  📐 {size_str}")
            with col2:
                if st.button("🗑️", key=f"remove_img_{idx}", help="Remove this image"):
                    st.session_state.processed_files = [
                        f for f in st.session_state.processed_files
                        if f["filename"] != info["filename"]
                    ]
                    st.session_state.merged_pdf_bytes = None
                    st.session_state.merged_pdf_filename = None
                    st.rerun()

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.processed_files = []
            st.session_state.merged_pdf_bytes = None
            st.session_state.merged_pdf_filename = None
            st.rerun()
    with col2:
        include_cover = st.checkbox("Include cover page", value=True)

    if st.button("🔗 Merge to PDF", type="primary", use_container_width=True):
        with st.spinner("Merging images into PDF…"):
            try:
                merged_buffer = merge_images_to_pdf(sorted_files, include_cover=include_cover)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"images_to_pdf_{timestamp}.pdf"
                st.session_state.merged_pdf_bytes = merged_buffer.getvalue()
                st.session_state.merged_pdf_filename = filename
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error creating PDF: {str(e)}")
                st.exception(e)

    if st.session_state.merged_pdf_bytes and st.session_state.merged_pdf_filename:
        st.success("✅ PDF ready. Download below.")
        st.download_button(
            label="⬇️ Download PDF",
            data=st.session_state.merged_pdf_bytes,
            file_name=st.session_state.merged_pdf_filename,
            mime="application/pdf",
            use_container_width=True,
        )
else:
    st.info("👆 Upload PNG or JPEG images to get started.")
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        - **Supported:** PNG, JPEG (`.png`, `.jpg`, `.jpeg`)
        - **Order:** Images are sorted by date (EXIF or file) and merged in that order.
        - **Cover page:** Optional first page listing all image names and sizes.
        - **Download:** After merging, use **Download PDF** to save the file.
        - On mobile, upload 1–2 files at a time for best reliability.
        """)

st.markdown("---")
st.markdown("*Built with Streamlit*")
