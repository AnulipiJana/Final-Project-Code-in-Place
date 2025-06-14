import gradio as gr
import csv

# Batch database
batch_courses = {}
students = {}  # Format: {batch_name: {student_name: {course: score, '__attendance__': attendance}}}

# Grading function
def get_grade(avg):
    if avg >= 90: return "O"
    elif avg >= 80: return "E"
    elif avg >= 70: return "A"
    elif avg >= 60: return "B"
    elif avg >= 50: return "C"
    else: return "F"

# Add courses to a batch
def setup_batch(batch_name, courses):
    if not batch_name or not courses:
        return "❌ Enter both batch name and courses."
    course_list = [s.strip() for s in courses.split(",") if s.strip()]
    if not course_list:
        return "❌ No valid courses provided."
    batch_courses[batch_name] = course_list
    students[batch_name] = {}
    return f"✅ Courses set for batch {batch_name}: {', '.join(course_list)}"

# Add all scores at once
def add_all_scores(batch_name, name, scores_str, attendance):
    if batch_name not in batch_courses:
        return "⚠️ Batch not set up yet."
    courses = batch_courses[batch_name]
    scores = [s.strip() for s in scores_str.split(",")]
    if len(courses) != len(scores):
        return f"⚠️ Expected {len(courses)} scores but got {len(scores)}."
    try:
        scores = [float(s) for s in scores]
        attendance = float(attendance)
    except ValueError:
        return "❌ All scores and attendance must be numbers."
    if name not in students[batch_name]:
        students[batch_name][name] = {}
    for course, score in zip(courses, scores):
        students[batch_name][name][course] = score
    students[batch_name][name]['__attendance__'] = attendance
    return f"✅ Added scores and attendance for {name} in batch {batch_name}."

# Show report
def show_report(batch_name, name):
    if batch_name not in students or name not in students[batch_name]:
        return "⚠️ Student not found."
    marks = students[batch_name][name]
    total = sum(v for k, v in marks.items() if k != '__attendance__')
    count = len([k for k in marks if k != '__attendance__'])
    avg = total / count
    grade = get_grade(avg)
    attendance = marks.get('__attendance__', 'N/A')

    report = f"📘 Report Card for {name} (Batch {batch_name})\n"
    for course, mark in marks.items():
        if course != '__attendance__':
            report += f"{course}: {mark}\n"
    report += f"\nAverage: {avg:.2f}\nGrade: {grade}\nAttendance: {attendance}%"
    return report

# Save report to file
def download_report(batch_name, name):
    if batch_name not in students or name not in students[batch_name]:
        return None
    filename = f"{batch_name}_{name.replace(' ', '_')}_report.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Course", "Score"])
        for course, score in students[batch_name][name].items():
            if course != '__attendance__':
                writer.writerow([course, score])
        total = sum(v for k, v in students[batch_name][name].items() if k != '__attendance__')
        count = len([k for k in students[batch_name][name] if k != '__attendance__'])
        avg = total / count
        writer.writerow(["Average", avg])
        writer.writerow(["Grade", get_grade(avg)])
        writer.writerow(["Attendance", students[batch_name][name].get('__attendance__', 'N/A')])
    return filename

# Show courses of a batch
def show_batch_courses(batch_name):
    if batch_name in batch_courses:
        return f"Courses for batch {batch_name}: {', '.join(batch_courses[batch_name])}"
    return "⚠️ Batch not found."

# Gradio UI
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🏫 Student Grade Tracker
    Set up batches with fixed courses ||  Add scores for each cources in report card || Display and Download grade cards
    """)

    with gr.Tab("1️⃣ Setup Batch"):
        batch_input = gr.Textbox(label="Batch Name", placeholder="e.g. XY_00")
        courses_input = gr.Textbox(label="Courses (comma-separated)", placeholder="e.g. Python, Java, C")
        setup_btn = gr.Button("✅ Set Courses")
        setup_status = gr.Textbox(label="Status")

    with gr.Tab("2️⃣ Add All Scores"):
        batch_add = gr.Textbox(label="Batch Name")
        batch_course_display_add = gr.Textbox(label="Courses for the Batch", lines=2, interactive=False)
        name_input = gr.Textbox(label="Student Name")
        scores_input = gr.Textbox(label="Scores (comma-separated, same order as courses)")
        attendance_input = gr.Textbox(label="Attendance (%)")
        add_btn = gr.Button("➕ Enter")
        add_status = gr.Textbox(label="Status")

    with gr.Tab("3️⃣ Show Report"):
        name_report = gr.Textbox(label="Student Name")
        batch_report = gr.Textbox(label="Batch Name")
        batch_course_display = gr.Textbox(label="Courses for the Batch", lines=2, interactive=False)
        show_btn = gr.Button("📄 Show Report")
        report_output = gr.Textbox(label="Report", lines=10)
        download_btn = gr.Button("⬇️ Download Report as CSV")
        report_file = gr.File(label="Download Link")

    setup_btn.click(setup_batch, inputs=[batch_input, courses_input], outputs=setup_status)
    batch_add.change(show_batch_courses, inputs=batch_add, outputs=batch_course_display_add)
    add_btn.click(add_all_scores, inputs=[batch_add, name_input, scores_input, attendance_input], outputs=add_status)
    batch_report.change(show_batch_courses, inputs=batch_report, outputs=batch_course_display)
    show_btn.click(show_report, inputs=[batch_report, name_report], outputs=report_output)
    download_btn.click(download_report, inputs=[batch_report, name_report], outputs=report_file)

demo.launch()
