import asyncio

from app.parse import get_all_courses

FOR_SURE_THIS_COURSES = [
    "QA",
    "Java",
    "Python",
    "Recruiter",
    "DevOps",
    "Digital",
    "Data"
]  # frontend is web development sometimes


def test_get_all_courses():
    all_courses = asyncio.run(get_all_courses())

    course_names = [course.name for course in all_courses]

    for course in FOR_SURE_THIS_COURSES:
        assert any(
            course.lower() in course_name.lower() for course_name in course_names
        ), f"Course '{course}' have not been parsed"
