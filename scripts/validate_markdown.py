#!/usr/bin/env python3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

POSTS_DIR = Path("posts/en")
IMAGES_DIR = Path("static/assets/blog-images")
REQUIRED_FIELDS = [
    "title",
    "subtitle",
    "author",
    "date",
    "permalink",
    "tags",
    "shortcontent",
]
OPTIONAL_IMAGE_FIELDS = ["author_image", "image"]

# get only the changed md files, if any
def changed_markdown_files():
    try:
        result = subprocess.run(
            [
                "git",
                "diff",
                "--name-only",
                "--diff-filter=AM",
                "origin/main...HEAD",
            ],
            text=True,
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as error:
        message = error.stderr.strip() or error.stdout.strip()
        print(f"Unable to get changed Markdown files: {message}")
        sys.exit(1)

    return [
        Path(line)
        for line in result.stdout.splitlines()
        if line.startswith("posts/en/") and line.endswith(".md")
    ]

# this function looks for other posts' permalinks in order to ensure the uniqueness
def load_existing_permalinks(files_under_review):
    permalinks = set()

    # look for permalink in already published blog files
    for path in POSTS_DIR.glob("*.md"):
        if path in files_under_review:
            continue

        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()

        for line in lines:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            if key.strip() == "permalink":
                permalinks.add(value.strip())

    return permalinks

# this function performs all the steps in order to validate the post
def validate_post(path, known_permalinks):
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # CHECK: separator existence
    separator_index = None
    for index, line in enumerate(lines):
        if line.strip() == "---":
            separator_index = index
            break
    if separator_index is None:
        return f"{path}: missing required '---' separator"

    # get each key-value from the metadata
    metadata = {}
    for line in lines[:separator_index]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()

    # CHECK: required fields
    for field in REQUIRED_FIELDS:
        if not metadata.get(field, ""):
            return f"{path}: missing or empty required field '{field}'"

    # CHECK: correct date format   
    date_value = metadata.get("date", "")
    if date_value:
        try:
            datetime.strptime(date_value, "%B %d, %Y")
        except ValueError:
            return f"{path}: field 'date' must match format '%B %d, %Y' "

    # CHECK: unique permalink
    permalink = metadata.get("permalink", "")
    if permalink:
        if permalink in known_permalinks:
            return f"{path}: duplicate permalink '{permalink}'"
        known_permalinks.add(permalink)

    # CHECK: if optional fields exists, it must have a value, representing a valid path
    for field in OPTIONAL_IMAGE_FIELDS:
        if field not in metadata:
            continue

        image_name = metadata[field]
        if not image_name:
            return f"{path}: optional field '{field}' is present but empty"

        image_path = IMAGES_DIR / image_name
        if not image_path.is_file():
            return f"{path}: field '{field}' references missing file '{image_path}'"

    # CHECK: body is required
    body = "\n".join(lines[separator_index + 1 :]).strip()
    if not body:
        return f"{path}: article body after '---' must not be empty"
    
    # all checks passed, no error is returned
    return None

def main():
    files = changed_markdown_files()
    known_permalinks = load_existing_permalinks(set(files))
    errors = []

    for path in files:
        error = validate_post(path, known_permalinks)
        if error:
            errors.append(error)

    if errors:
        print("Markdown validation failed:")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)

    print("Markdown validation passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
