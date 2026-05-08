import streamlit as st
import json

from enrollment_starter_refactored import (
    CURRENT_STUDENT,
    EnrollmentDatabase,
    EnrollmentService,
)


database = EnrollmentDatabase()
service = EnrollmentService(database)

database.create_tables()
database.seed_sample_data()


def setup_session_state():
    if "current_student" not in st.session_state:
        st.session_state.current_student = {
            **CURRENT_STUDENT,
            "role": "student",
        }

    if "role" not in st.session_state:
        st.session_state.role = "student"

    if "page" not in st.session_state:
        st.session_state.page = "dashboard"

    if "selected_class" not in st.session_state:
        st.session_state.selected_class = None

    if "feedback" not in st.session_state:
        st.session_state.feedback = None


def show_feedback():
    feedback = st.session_state.feedback

    if feedback:
        message_type, message = feedback

        if message_type == "success":
            st.success(message)
        elif message_type == "warning":
            st.warning(message)
        elif message_type == "error":
            st.error(message)

        st.session_state.feedback = None


def dashboard_page():
    student = st.session_state.current_student

    st.title("Student Dashboard")
    st.caption(f"Logged in as {student['name']}")

    show_feedback()

    summary = service.get_student_summary(student["user_id"])
    enrolled_classes = service.get_student_enrollments(student["user_id"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records", summary["total_records"])
    col2.metric("Enrolled", summary["enrolled"])
    col3.metric("Unenrolled", summary["unenrolled"])

    st.divider()

    st.container()
    st.subheader("My Enrolled Classes")

    if enrolled_classes:
        st.dataframe(enrolled_classes, use_container_width=True)

        class_options = {
            f"{course['course_id']} - {course['course_name']}": course
            for course in enrolled_classes
        }

        selected_label = st.selectbox(
            "Choose a class",
            list(class_options.keys()),
        )

        selected_class = class_options[selected_label]

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Go to Class"):
                st.session_state.selected_class = selected_class
                st.session_state.page = "class_page"
                st.rerun()

        with col2:
            if st.button("Unenroll"):
                success = service.soft_unenroll_student(
                    student["user_id"],
                    selected_class["course_id"],
                )

                if success:
                    st.session_state.feedback = (
                        "success",
                        f"You have unenrolled from {selected_class['course_name']}.",
                    )
                else:
                    st.session_state.feedback = (
                        "error",
                        "Unable to unenroll from this class.",
                    )

                st.rerun()
    else:
        st.warning("You are not currently enrolled in any classes.")

    st.divider()

    st.subheader("Join a Class")

    with st.form("enrollment_form"):
        enrollment_key = st.text_input("Enter enrollment key")
        submitted = st.form_submit_button("Submit Key")

        if submitted:
            result = service.enroll_with_key(
                student["user_id"],
                student["email"],
                enrollment_key,
            )

            if result:
                st.session_state.selected_class = result
                st.session_state.feedback = (
                    "success",
                    "Enrollment successful.",
                )
                st.session_state.page = "class_page"
                st.rerun()
            else:
                st.session_state.feedback = (
                    "error",
                    "Invalid enrollment key. Please try again.",
                )
                st.rerun()


def class_page():
    selected_class = st.session_state.selected_class

    if not selected_class:
        st.session_state.feedback = ("warning", "No class selected.")
        st.session_state.page = "dashboard"
        st.rerun()

    st.title(selected_class.get("course_name", "Selected Class"))
    st.caption("Class Details")

    st.write(f"**Course ID:** {selected_class.get('course_id')}")
    st.write(f"**Instructor:** {selected_class.get('instructor', 'N/A')}")
    st.write(f"**Status:** {selected_class.get('status', 'N/A')}")

    if selected_class.get("enrolled_at"):
        st.write(f"**Enrolled At:** {selected_class.get('enrolled_at')}")

    if st.button("Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()


def main():
    setup_session_state()

    if st.session_state.role != "student":
        st.error("Only students can view this page.")
        return

    if st.session_state.page == "dashboard":
        dashboard_page()
    elif st.session_state.page == "class_page":
        class_page()


if __name__ == "__main__":
    main()