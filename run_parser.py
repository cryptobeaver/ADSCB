import os
from bs4 import BeautifulSoup, Comment


def has_visible_text(element):
    if element.parent.name in [
        "style",
        "script",
        "head",
        "title",
        "meta",
        "[document]",
    ]:
        return False
    if isinstance(element, Comment):
        return False
    return True


def parse_html_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")

    visible_elements = soup.find_all(has_visible_text)

    parsed_content = []
    for element in visible_elements:
        if element.name in [
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "p",
            "div",
            "section",
            "table",
            "thead",
            "tbody",
            "tfoot",
        ]:
            tag_text = " ".join(element.find_all(text=True, recursive=False))
            tag_text = " ".join(tag_text.split())  # Remove extra whitespaces
            if tag_text:
                parsed_content.append(f"<{element.name}>{tag_text}</{element.name}>")

    parsed_content = "\n\n".join(parsed_content)

    return parsed_content


def save_parsed_file(file_path, parsed_content):
    parsed_file_path = file_path + ".parsed"
    with open(parsed_file_path, "w", encoding="utf-8") as file:
        file.write(parsed_content)


def process_files_in_folder(folder_path):
    # Iterate over the files and subfolders in the given folder
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path) and item.endswith(".html"):
            # Process HTML file
            parsed_content = parse_html_file(item_path)
            if parsed_content:
                save_parsed_file(item_path, parsed_content)
                print(f"Parsed file: {item}")
            else:
                print(f"No <h1> tags found in file: {item}")
        elif os.path.isdir(item_path):
            # Recursively process subfolder
            process_files_in_folder(item_path)


def post_process_parsed_files(folder_path):
    # Iterate over the files and subfolders in the given folder
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path) and item.endswith(".parsed"):
            # Read the parsed file
            with open(item_path, "r", encoding="utf-8") as file:
                parsed_content = file.read()

            # Remove everything before and including the "<p>Knowledge base</p>" tag
            knowledge_base_index = parsed_content.find("<p>Knowledge base</p>")
            if knowledge_base_index != -1:
                parsed_content = parsed_content[
                    knowledge_base_index + len("<p>Knowledge base</p>") :
                ]

            # Remove empty white spaces between each tag
            parsed_content = parsed_content.replace("\n\n", "\n")

            # Write the updated content back to the file
            with open(item_path, "w", encoding="utf-8") as file:
                file.write(parsed_content)
        elif os.path.isdir(item_path):
            # Recursively process subfolder
            post_process_parsed_files(item_path)


def main():
    downloaded_folder = "./langchain-docs/"
    process_files_in_folder(downloaded_folder)
    post_process_parsed_files(downloaded_folder)


if __name__ == "__main__":
    main()
