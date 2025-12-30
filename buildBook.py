#!/usr/bin/env python3
"""
Wiki to LaTeX Converter
Fetches pages from a Miraheze wiki and converts them to LaTeX
"""

import shutil
import time
import requests
import re
import os
import subprocess
from pathlib import Path
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup
import pypandoc
from urllib.parse import urljoin, urlparse, unquote
from typing import List, Dict, Any, Optional
from io import TextIOWrapper  # Import from io, not typing

from dotenv import load_dotenv


load_dotenv()
WIKI_BASE_URL = "https://style.miraheze.org"
API_URL = f"{WIKI_BASE_URL}/w/api.php"
USERNAME = "M. Kolesnichenko"
PASSWORD = os.getenv("PASSWORD")

# Output directories
OUTPUT_DIR = Path("LaTeX")
STYLE_CLS = OUTPUT_DIR / "style.cls"
CHAPTERS_DIR = OUTPUT_DIR / "chapters"
DATA_DIR = Path("data")

# Session for maintaining cookies
session = requests.Session()
session.headers.update(
    {"User-Agent": "WikiToLatexConverter/1.0 (alan.kersaudy@gmail.com)"}
)


def download_xml() -> Optional[ET.Element]:
    """
    Fetch the XML from the API
    Save it to a local file named 'book.xml'
    """
    print("1. Starting XML download...")
    print("1.1. Getting session cookies...")
    print("1.1.1 Fetching login token...")
    res = session.get(
        API_URL,
        params={
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json",
        },
    )
    print("status", res)
    login_token = res.json()["query"]["tokens"]["logintoken"]
    print("1.1.2 Logging in...")
    session.post(
        API_URL,
        data={
            "action": "clientlogin",
            "username": USERNAME,
            "password": PASSWORD,
            "loginreturnurl": API_URL,
            "logintoken": login_token,
            "format": "json",
        },
    )

    print("1.1.3 Fetching CSRF token...")
    csrf_token = session.get(
        API_URL, params={"action": "query", "meta": "tokens", "format": "json"}
    ).json()["query"]["tokens"]["csrftoken"]
    print("1.1.4 CSRF token obtained.")

    print("1.2 Downloading XML content...")
    url = f"{WIKI_BASE_URL}/wiki/Dibar:Ezporzhiañ"
    r = session.post(
        url,
        data={
            "token": csrf_token,
            "title": "Dibar:Ezporzhiañ",
            "catname": "Degemer",
            "pages": "Degemer",
            "curonly": "1",
            "templates": "1",
            "pagelink-depth": "2",
            "wpDownload": "1",
        },
    )
    r.raise_for_status()

    print("1.3 Writing XML content...")
    with open("data/book.xml", "wb") as file:
        file.write(r.content)

    print("1.5 XML download complete, parsing the XML...")
    try:
        root = ET.fromstring(r.content)
        print("1.5.1 Parsed successfully! Returning root element")
        return root
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return None


def parse_list_items(ol: BeautifulSoup, depth: int = 0) -> List[Dict[str, Any]]:
    """Recursively parse list items and their nested lists"""
    items = []
    for li in ol.find_all("li", recursive=False):
        # Find the link in this list item
        link = li.find("a")
        content = str(li.contents[0])
        text = content.strip()
        href = link.get("href", "")
        page_title = href.replace("_", " ")
        hasLink = content == str(link)
        # Convert relative URLs to absolute
        if href.startswith("/"):
            href = urljoin(WIKI_BASE_URL, href)
        item = {
            "title": page_title if hasLink else text,
            "url": href if hasLink else "",
            "hasLink": hasLink,
            "depth": depth,
            "children": [],
        }
        # Look for nested ordered lists
        nested_ol = li.find("ol")
        if nested_ol:
            item["children"] = parse_list_items(nested_ol, depth + 1)
        items.append(item)
    return items


def buildToC(root: ET.Element) -> List[Dict[str, Any]]:
    """
    Build the ToC for XML
    """
    print("2. Building Table of Contents...")
    print("2.1 Fetch the ToC markdown text in root...")
    # Placeholder implementation
    toc = []
    tocMDstr = ""
    namespace = {"mediawiki": "http://www.mediawiki.org/xml/export-0.11/"}

    for page in root.findall(".//mediawiki:page", namespace):
        title = page.find("mediawiki:title", namespace).text
        if title is not None and title == "Taolenn an danvezioù":
            print("2.2 ToC found in XML, extracting text...")
            text_elem = page.find(".//mediawiki:text", namespace)
            if text_elem is not None:
                tocMDstr = ET.fromstring(text_elem.text).text.strip()
                break
    print(f"2.3 Converting ToC to dictionary.")
    htmlToC = pypandoc.convert_text(tocMDstr, "html", format="mediawiki")
    soup = BeautifulSoup(htmlToC, "html.parser")
    parsed_ToC = parse_list_items(soup.find("ol"))
    print(f"2.4 ToC parsed! Length: {len(parsed_ToC)} items.")
    return parsed_ToC


def add_examples_to_content(content: str) -> str:
    """Process wikitext, find template transclusions and turns them into actual examples"""
    # create a regex pattern to find all the {{:<Example title>}} segments
    pattern = re.compile(r"\{\{:(.+?)\}\}")
    matches = pattern.findall(content)
    for match in matches:
        example_title = match.strip()
        print(f"    Downloading example: {example_title}")
        # Fetch the example page content
        html_content = session.get(
            API_URL,
            params={
                "action": "parse",
                "format": "json",
                "page": example_title,
            },
        ).json()["parse"]["text"]["*"]
        # Get table in html
        soup = BeautifulSoup(html_content, "html.parser")
        html_table = str(soup.find("table"))
        example_content = pypandoc.convert_text(html_table, "mediawiki", format="html")
        # Replace the template in the original content with the LaTeX example
        content = content.replace(f"{{{{:{example_title}}}}}", example_content)
    return content


def process_structure(
    file: TextIOWrapper, structure: List[Dict[str, Any]], root: ET.Element
) -> None:
    """Process the structure and create LaTeX files"""
    files = []
    for idx, item in enumerate(structure, 1):
        title = item["title"]
        depth = item["depth"]

        # Create filename
        safe_title = re.sub(r"[^\w\s-]", "", title)
        safe_title = re.sub(r"[-\s]+", "_", safe_title)
        filename = f"{safe_title}.tex"

        filepath = CHAPTERS_DIR / filename

        if item["title"].startswith(":Rummad:"):
            print(f"Skipping category page: {item['title']}")
            continue

        print(f"Creating: {'  ' * depth}{filepath}")

        chapter_content = ""

        if item["hasLink"]:
            namespace = {"mediawiki": "http://www.mediawiki.org/xml/export-0.11/"}

            wiki_content = ""
            for page in root.findall(".//mediawiki:page", namespace):
                title = page.find("mediawiki:title", namespace).text
                if title is not None and title == item["title"]:
                    wiki_content = page.find(
                        ".//mediawiki:text", namespace
                    ).text.strip()
                    wiki_content = add_examples_to_content(wiki_content)
                else:
                    pass
            chapter_content = (
                str(
                    pypandoc.convert_text(
                        wiki_content,
                        "latex",
                        format="mediawiki",
                    )
                )
                .replace(
                    "\\begin{longtable}[]{@{}ll@{}}",
                    "\\begin{longtable}[]{|p{0.45\\textwidth}|p{0.45\\textwidth}}",
                )
                .replace(
                    """\\toprule\\noalign{}
\\endhead
\\bottomrule\\noalign{}
\\endlastfoot""",
                    "",
                )
            )
        # Remove links from the wikitext
        chapter_content = re.sub(r"\\url\{.+?\}\{(.+?)\}", r"\1", chapter_content)

        with open(filepath, "w", encoding="utf-8") as f:
            category = ["part", "chapter", "chapter"]
            f.write(f"\\{category[depth]}{{{item['title']}}}\n\n")
            f.write(chapter_content.replace("subsection", "section"))

        file.write(f"{'  ' * depth}\\include{{chapters/{safe_title}}}\n")

        # Process children
        if item["children"]:
            process_structure(file, item["children"], root)

    return None


def main() -> None:
    """
    Fetch the XML from the API
    Build the ToC from XML
    Create LaTeX files from the ToC
        Use the title tag from the XML to find chapter titles
            Create a custom example generator to replace the template in wikitext
        else with empty chapter when page is missing from XML
    Remove the main.pdf file if exists and rebuild with the `pdflatex -interaction=nonstopmode main.tex` command (run twice to build the ToC properly)
    """
    # Add a time stamp to the build
    start_time = time.time()
    print("Starting build process...")
    print("Setting up directories...")
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(exist_ok=True)
        DATA_DIR.mkdir(exist_ok=True)
    if OUTPUT_DIR.exists():
        if STYLE_CLS.exists():
            with open(STYLE_CLS, "r", encoding="utf-8") as f:
                style_cls_content = f.read()
        shutil.rmtree(OUTPUT_DIR)

        OUTPUT_DIR.mkdir(exist_ok=True)
        CHAPTERS_DIR.mkdir(exist_ok=True)
        if style_cls_content:
            with open(STYLE_CLS, "w", encoding="utf-8") as f:
                f.write(style_cls_content)

    root = download_xml()

    toc = buildToC(root)

    main_file = OUTPUT_DIR / "main.tex"

    print("3. Creating main LaTeX file...")
    with open(main_file, "w", encoding="utf-8") as f:
        f.write(
            r"""\documentclass{style}


\title{Arlivioù ar Brezhoneg}
\author{Maria Kolesnichenko}
\date{\today}

\begin{document}

\maketitle
\tableofcontents
\cleardoublepage

"""
        )
        # Add includes
        print("3.2 Creating and adding the chapters:")
        process_structure(f, toc, root)

        f.write(
            r"""
\end{document}
"""
        )

    print(f"3.3 Main file created successfully!")
    end_time = time.time()
    print("This took %.2f seconds" % (end_time - start_time))


main()
