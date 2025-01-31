import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO

# Register the 'DejaVu Sans' font
pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))

# Helper function to calculate text width for underlining
def get_text_width(text, font_size, font_name='DejaVuSans'):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    return stringWidth(text, font_name, font_size)

# Helper function to generate PDF with underlined date range and bolded days
def generate_pdf(lessons_data, subjects, lessons, total_amount, student_name, extra_lessons, logo_path=None):
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    
    # Set font to DejaVu Sans (similar to Notion's 'Sans-Serif')
    c.setFont("DejaVuSans", 12)
    
    # Header
    if logo_path:
        c.drawImage(logo_path, 40, 720, width=1.5*inch, height=0.75*inch)

    c.setFont("DejaVuSans-Bold", 16)
    c.drawString(100, 760, "Tutoring Invoice")

    # Student's Name at the top right
    c.setFont("DejaVuSans", 12)
    if student_name:
        c.drawString(450, 760, f"{student_name}")

    # Add lessons data (date range, day, time)
    y_position = 740
    for lesson in lessons_data:
        date_range = lesson['date_range']
        day = lesson['day']
        time = lesson['time']
        
        # Add date range with underline
        c.setFont("DejaVuSans", 12)
        c.drawString(100, y_position, f"{date_range}")
        date_range_width = get_text_width(date_range, 12)
        c.line(100, y_position - 2, 100 + date_range_width, y_position - 2)
        y_position -= 20
        
        # Add day and time
        c.drawString(100, y_position, day)
        c.drawString(180, y_position, f"({time})")
        y_position -= 20

    # Add extra lessons
    for extra_day, extra_time in extra_lessons:
        c.setFont("DejaVuSans", 12)
        c.drawString(100, y_position, f"Extra Lesson: {extra_day}")
        c.drawString(260, y_position, f"({extra_time})")
        y_position -= 20

    # Table header
    c.setFont("DejaVuSans-Bold", 12)
    c.drawString(100, y_position, "Subject")
    c.drawString(270, y_position, "Number of Lessons")
    c.drawString(420, y_position, "Total ($)")
    
    # Draw a line below the headers
    c.line(90, y_position - 5, 500, y_position - 5)

    # Table rows
    c.setFont("DejaVuSans", 12)
    y_position -= 25
    for subject, lesson in zip(subjects, lessons):
        c.drawString(100, y_position, subject)
        c.drawString(270, y_position, str(lesson))
        c.drawString(420, y_position, f"{lesson * 150}")
        y_position -= 20

    # Draw a line above the total amount
    c.line(270, y_position - 10, 500, y_position - 10)

    # Total amount
    c.setFont("DejaVuSans-Bold", 12)
    c.drawString(270, y_position - 30, "Total:")
    c.drawString(420, y_position - 30, f"${total_amount}")

    # Footer (optional)
    c.setFont("DejaVuSans", 10)
    c.setFillColor(colors.grey)
    c.drawString(100, 100, "Made by kateyki")

    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

# Streamlit app
st.title("Babygirl's Invoice Generator")

# Student's name input
student_name = st.text_input("Student's Name")

# Lessons data input
if 'lessons_data' not in st.session_state:
    st.session_state['lessons_data'] = []

# Add new lesson button
if st.button("Add Lesson"):
    st.session_state['lessons_data'].append({"date_range": "", "day": "", "time": ""})

# Display current lessons data
for idx, lesson in enumerate(st.session_state['lessons_data']):
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    with col1:
        start_date = st.date_input(f"Start Date {idx+1}", key=f"start_date_{idx}")
        end_date = st.date_input(f"End Date {idx+1}", key=f"end_date_{idx}")
        if start_date and end_date:
            st.session_state['lessons_data'][idx]['date_range'] = f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
    with col2:
        st.session_state['lessons_data'][idx]['day'] = st.text_input(
            "Day", key=f"day_{idx}"
        )
    with col3:
        st.session_state['lessons_data'][idx]['time'] = st.text_input(
            "Time Slot (e.g., 9AM-11AM)", key=f"time_{idx}"
        )
    with col4:
        # Add a remove button for the lesson
        if st.button("Remove", key=f"remove_lesson_{idx}"):
            del st.session_state['lessons_data'][idx]
            st.experimental_rerun()

# Extract lessons data into a list
lessons_data = st.session_state['lessons_data']

# Extra lessons input
if 'extra_lessons' not in st.session_state:
    st.session_state['extra_lessons'] = []

# Add new extra lesson button
if st.button("Add Extra Lesson"):
    st.session_state['extra_lessons'].append({"extra_day": "", "extra_time": ""})

# Display current extra lessons
for idx, extra_lesson in enumerate(st.session_state['extra_lessons']):
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.session_state['extra_lessons'][idx]['extra_day'] = st.text_input(
            "Extra Lesson Day", key=f"extra_day_{idx}"
        )
    with col2:
        st.session_state['extra_lessons'][idx]['extra_time'] = st.text_input(
            "Time Slot (e.g., 2PM-4PM)", key=f"extra_time_{idx}"
        )
    with col3:
        # Add a remove button for the extra lesson
        if st.button("Remove Extra", key=f"remove_extra_{idx}"):
            del st.session_state['extra_lessons'][idx]
            st.experimental_rerun()

# Extract extra lessons into a list
extra_lessons = [(el['extra_day'], el['extra_time']) for el in st.session_state['extra_lessons']]

# Subjects and lessons input
if 'subjects_data' not in st.session_state:
    st.session_state['subjects_data'] = []

# Add new subject button
if st.button("Add Subject"):
    st.session_state['subjects_data'].append({"subject": "", "lessons": 1})

# Display current subjects
for idx, subject_data in enumerate(st.session_state['subjects_data']):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.session_state['subjects_data'][idx]['subject'] = st.text_input(
            "Subject", key=f"subject_{idx}"
        )
    with col2:
        st.session_state['subjects_data'][idx]['lessons'] = st.number_input(
            "Lessons", min_value=0.5, step=0.5, format="%.1f", key=f"lessons_{idx}"
        )
    with col3:
        # Add a remove button for each subject
        if st.button("Remove", key=f"remove_{idx}"):
            del st.session_state['subjects_data'][idx]
            st.experimental_rerun()

# Extract subjects and lessons into separate lists
subjects = [data['subject'] for data in st.session_state['subjects_data']]
lessons = [data['lessons'] for data in st.session_state['subjects_data']]

# Calculate total amount
total_amount = sum(lessons) * 150

# Display total
st.write(f"Total Amount: ${total_amount}")

# Generate PDF button
if st.button("Generate PDF"):
    if lessons_data and subjects and student_name:
        pdf_buffer = generate_pdf(lessons_data, subjects, lessons, total_amount, student_name, extra_lessons)
        st.download_button("Download Invoice", pdf_buffer, "invoice.pdf")
    else:
        st.error("Please fill in all fields before generating the PDF.")
