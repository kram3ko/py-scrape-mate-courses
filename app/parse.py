import asyncio
import csv
import re
from dataclasses import dataclass
from typing import List

import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://mate.academy"


@dataclass
class Course:
    name: str
    short_description: str
    duration: str
    modules: int = 0
    topics: int = 0


async def get_course_details(client: httpx.AsyncClient, url: str, name: str) -> Course:
    resp = await client.get(url)
    soup = BeautifulSoup(resp.content, "lxml")
    desc = soup.find("p", class_="typography_textMain__oRJ69 CourseModulesList_aboutCourse__gmavO")
    duration_div = soup.find("div", class_="c-text-dark typography_microMedium__IGlfO", string=re.compile(r"місяц"))
    duration = duration_div.text.strip() if duration_div else ""

    modules = len(soup.find_all("div", class_="CourseModulesList_moduleListItem__b8AY9"))

    topics = 0
    for p in soup.find_all("p", class_="CourseModulesList_topicsCount__H_fv3 typography_textMain__oRJ69"):
        match = re.search(r"(\d+)", p.text)
        if match:
            topics += int(match.group(1))

    return Course(
        name=name,
        short_description=desc.text.strip() if desc else "",
        duration=duration,
        modules=modules,
        topics=topics
    )


async def get_all_courses() -> List[Course]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(BASE_URL)
        soup = BeautifulSoup(resp.content, "lxml")
        courses_block = soup.find("ul", class_="FooterLinks_navList__iWcAG")
        if not courses_block:
            return []
        course_links = courses_block.find_all("a")
        tasks = [
            get_course_details(
                client,
                f"{BASE_URL}{href}" if href and not href.startswith("http") else href,
                a.text.strip()
            )
            for a in course_links
            if (href := a.get("href"))
        ]
        return await asyncio.gather(*tasks)


def save_courses_to_csv(courses, filename="courses.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Description", "Duration", "Modules", "Topics"])
        for course in courses:
            writer.writerow([
                course.name,
                course.short_description,
                course.duration,
                course.modules,
                course.topics
            ])


def main():
    courses = asyncio.run(get_all_courses())
    save_courses_to_csv(courses)


if __name__ == "__main__":
    main()
