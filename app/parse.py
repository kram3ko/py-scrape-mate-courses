import asyncio
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


async def get_course_details(
    client: httpx.AsyncClient,
    url: str,
    name: str,
    short_description: str
) -> Course:
    try:
        resp = await client.get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "lxml")
        duration_div = soup.find(
            "div",
            class_="c-text-dark typography_microMedium__IGlfO",
            string=re.compile(r"місяц")
        )
        duration = duration_div.text.strip() if duration_div else ""

        modules = len(
            soup.find_all("div", class_="CourseModulesList_moduleListItem__b8AY9")
        )

        topics = 0
        for teg_p in soup.find_all(
            "p", class_="CourseModulesList_topicsCount__H_fv3 typography_textMain__oRJ69"  # noqa
        ):
            match = re.search(r"(\d+)", teg_p.text)
            if match:
                topics += int(match.group(1))

        return Course(
            name=name,
            short_description=short_description,
            duration=duration,
            modules=modules,
            topics=topics
        )
    except Exception as e:
        print(f"Error with name {name}: {e}")
        return Course(name, short_description, "", 0, 0)


async def get_all_courses() -> List[Course]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(BASE_URL)
        soup = BeautifulSoup(resp.content, "lxml")
        course_cards = soup.find_all("a", class_="ProfessionCard_cardWrapper__BCg0O")
        tasks = []
        for card in course_cards:
            href = card.get("href")
            if not href:
                continue
            name_tag = card.find(class_="ProfessionCard_title__m7uno")
            name = name_tag.get_text(strip=True) if name_tag else "N/A"
            desc_tag = card.find(class_="ProfessionCard_description__K8weo")
            short_description = desc_tag.get_text(strip=True) if desc_tag else ""
            tasks.append(
                get_course_details(
                    client,
                    href if href.startswith("http") else f"{BASE_URL}{href}",
                    name,
                    short_description
                )
            )
        return await asyncio.gather(*tasks)


def main() -> None:
    asyncio.run(get_all_courses())


if __name__ == "__main__":
    main()
