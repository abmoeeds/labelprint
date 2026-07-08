import streamlit as st
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
from datetime import datetime

def generate_thermal_label(text, alignment, is_bold, is_underline, font_size, width_mm, height_mm):
    # Dynamic dimensions based on user inputs
    width = width_mm * mm
    height = height_mm * mm
    
    buffer = io.BytesIO()
    
    # Calculate margins dynamically: use 3mm or smaller if the label is tiny
    margin_size = min(3, width_mm * 0.05, height_mm * 0.05) * mm
    
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=(width, height),
        leftMargin=margin_size, 
        rightMargin=margin_size, 
        topMargin=margin_size, 
        bottomMargin=margin_size
    )
    
    align_map = {
        "Left": TA_LEFT,
        "Center": TA_CENTER,
        "Right": TA_RIGHT
    }
    
    styles = getSampleStyleSheet()
    custom_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontName="Helvetica",
        fontSize=font_size,
        leading=font_size + 4, 
        alignment=align_map[alignment]
    )
    
    story = []
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        if line.strip() == "":
            formatted_lines.append("")
            continue
            
        processed_line = line
        if is_bold:
            processed_line = f"<b>{processed_line}</b>"
        if is_underline:
            processed_line = f"<u>{processed_line}</u>"
            
        formatted_lines.append(processed_line)
    
    full_html_text = "<br/>".join(formatted_lines)
    story.append(Paragraph(full_html_text, custom_style))
    
    try:
        doc.build(story)
    except Exception as e:
        # Graceful handling if text overflows the custom dimensions
        st.error("⚠️ The text size or length is too large for these label dimensions. Try reducing the font size.")
        return None
        
    buffer.seek(0)
    return buffer

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Custom Size Thermal Label Gen", page_icon="🏷️")
st.title("🏷️ Dynamic Thermal Label Gen")

# --- Sidebar Configuration ---
st.sidebar.header("📏 Label Dimensions")
col_w, col_h = st.sidebar.columns(2)
with col_w:
    label_width = st.number_input("Width (mm)", min_value=10, max_value=200, value=60, step=1)
with col_h:
    label_height = st.number_input("Height (mm)", min_value=10, max_value=200, value=30, step=1)

st.sidebar.header("📁 File Saving Options")
file_prefix = st.sidebar.text_input("File Name Prefix", value="label")

st.sidebar.header("🎨 Text Styling")
text_alignment = st.sidebar.radio(
    "Text Alignment",
    options=["Left", "Center", "Right"],
    index=1
)

col1, col2 = st.sidebar.columns(2)
with col1:
    make_bold = st.checkbox("Bold (B)", value=True)
with col2:
    make_underline = st.checkbox("Underline (U)", value=False)

font_size = st.sidebar.slider("Font Size (pt)", min_value=6, max_value=36, value=11)

# --- Main UI Area ---
st.subheader("Label Content")
label_input = st.text_area(
    "Enter label text:", 
    value="BARGAIN BOUTIQUE\nSKU: 987654321\n$14.99",
    height=120
)

if st.button("✨ Generate & Preview"):
    with st.spinner("Calculating canvas layout..."):
        pdf_data = generate_thermal_label(
            label_input, 
            text_alignment, 
            make_bold, 
            make_underline, 
            font_size,
            label_width,
            label_height
        )
        
        if pdf_data is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_prefix = "".join(c for c in file_prefix if c.isalnum() or c in ('_', '-')).strip()
            if not clean_prefix:
                clean_prefix = "label"
                
            # Embed the dimensions directly into the filename to keep things organized
            unique_filename = f"{clean_prefix}_{label_width}x{label_height}_{timestamp}.pdf"
            
            st.success(f"Label created for dimensions **{label_width}mm × {label_height}mm**!")
            
            st.download_button(
                label="📥 Download Custom PDF",
                data=pdf_data,
                file_name=unique_filename,
                mime="application/pdf"
            )
