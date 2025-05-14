import os
import re
import shutil
import subprocess

import pyperclip
import questionary

from db.operations import (add_challenge, delete_challenge, get_all_challenges,
                           get_challenges_without_testcases,
                           get_due_challenges, mark_reviewed_challenge,
                           update_challenge, update_challenge_testcases)
from templates import CHALLENGE_PROMPT_TEMPLATE


def select_due_challenge(console):
    """
    Fetches due challenges and prompts the user to select one.
    Returns the selected challenge or None if no selection is made.
    """
    due_challenges = get_due_challenges()

    if not due_challenges:
        console.print(
            "[bold green]No challenges are due for review today![/bold green]"
        )
        return None

    console.print("[bold cyan]Challenges due for review:[/bold cyan]")
    challenge_choices = [
        f"ID: {c['id']} - {c['title']}" for c in due_challenges
    ]
    selected = questionary.select(
        "Select a challenge to review:", choices=challenge_choices
    ).ask()
    if not selected:
        console.print("[bold yellow]No challenge selected.[/bold yellow]")
        return None

    selected_id = int(selected.split(":")[1].strip().split(" ")[0])
    return next(c for c in due_challenges if c["id"] == selected_id)


def setup_python_files(challenge, folder_name):
    challenge_path = os.path.join(folder_name, "challenge.py")
    with open(challenge_path, "w", encoding="utf-8") as challenge_file:
        challenge_file.write(
            f'"""\n'
            f"Title: {challenge['title']}\n\n"
            f"Description:\n{challenge['description']}\n"
            f'"""\n\n\n'
            f"def {folder_name}():\n"
            f"    # Write your solution here...\n"
            f"    pass\n"
        )

    test_path = os.path.join(folder_name, "test_challenge.py")
    if challenge["testcases"]:
        with open(test_path, "w", encoding="utf-8") as test_file:
            imports = f"import pytest\n\nfrom challenge import {folder_name}\n"
            test_file.write(imports)
            test_file.write(challenge["testcases"])
    return challenge_path


def setup_javascript_files(challenge, folder_name):
    """
    Sets up JavaScript challenge files in the specified folder.
    The test file follows Jest's naming conventions for automatic discovery.
    Returns the path to the challenge file.
    """
    function_name = "".join(
        word.capitalize() if i > 0 else word
        for i, word in enumerate(folder_name.split("_"))
    )

    challenge_path = os.path.join(folder_name, "challenge.js")
    with open(challenge_path, "w", encoding="utf-8") as challenge_file:
        challenge_file.write(
            f"/*\n"
            f"Title: {challenge['title']}\n\n"
            f"Description:\n{challenge['description']}\n"
            f"*/\n\n"
            f"function {function_name}() {{\n"
            f"    // write your solution here...\n"
            f"}}\n\n"
            f"module.exports = {function_name};"
        )

    test_path = os.path.join(folder_name, "challenge.test.js")
    if challenge["testcases"]:
        with open(test_path, "w", encoding="utf-8") as test_file:
            test_file.write(
                f"const {function_name} = require('./challenge');\n\n"
                f"{challenge['testcases']}\n"
            )
    return challenge_path


def sanitize_folder_name(title):
    """
    Converts a title into a valid folder name:
    - Replaces spaces with underscores.
    - Removes invalid characters (non-alphanumeric or underscore).
    - Converts to lowercase.
    """
    sanitized_name = re.sub(r"[^a-zA-Z0-9\s]", "", title)
    sanitized_name = re.sub(r"\s+", "_", sanitized_name)
    return sanitized_name.lower()


def setup_challenge_files(challenge):
    """
    Creates a folder and files (challenge.py and test_challenge.py) for the
    challenge.
    Returns the folder path and the path to challenge.py.
    """
    folder_name = sanitize_folder_name(challenge["title"])
    os.makedirs(folder_name, exist_ok=True)
    challenge_path = ""
    if challenge["language"] == "python":
        challenge_path = setup_python_files(challenge, folder_name)
    elif challenge["language"] == "javascript":
        challenge_path = setup_javascript_files(challenge, folder_name)
    else:
        raise ValueError(f"Unsupported language: {challenge['language']}")

    return folder_name, challenge_path


def generate_challenge_prompt(console, challenge_file):
    """
    Generates the evaluation prompt for the challenge.
    Copies the prompt to the clipboard and returns it.
    """
    with open(challenge_file, "r", encoding="utf-8") as f:
        challenge_content = f.read()

    prompt = CHALLENGE_PROMPT_TEMPLATE.format(
        challenge_content=challenge_content
    )
    pyperclip.copy(prompt)
    console.print("[bold cyan]Evaluation Prompt:[/bold cyan]\n")
    console.print(prompt.strip())
    console.print("[bold green]Prompt copied to clipboard![/bold green]")
    return prompt


def update_challenge_review(console, challenge_id, grade):
    """
    Updates the SM-2 data for the given challenge based on the grade.
    """
    try:
        grade = float(grade)
        if 0 <= grade <= 3:
            mark_reviewed_challenge(challenge_id, grade)
            console.print(
                f"[bold green]Challenge ID {challenge_id}"
                + " has been reviewed and updated.[/bold green]"
            )
        else:
            console.print(
                "[bold red]Invalid grade."
                + " Please enter a value between 0 and 3.[/bold red]"
            )
    except ValueError:
        console.print(
            "[bold red]Invalid input. Please enter a numeric value.[/bold red]"
        )


def review_challenges(console):
    """
    Handles the review process for challenges:
    - Fetch due challenges.
    - Open the challenge description and test cases in an editor.
    - Prompt the user for a grade.
    - Update the SM-2 parameters for the challenge.
    """
    selected_challenge = select_due_challenge(console)

    if not selected_challenge:
        return

    folder_name, challenge_path = setup_challenge_files(selected_challenge)

    if os.getenv("EDITOR") == "code":
        vscode_flow(console, folder_name, challenge_path)
    else:
        os.system(f"{os.getenv('EDITOR', 'nvim')} {challenge_path}")
        generate_challenge_prompt(console, challenge_path)

    grade = questionary.text(
        "Enter your score for this challenge (0-3):"
    ).ask()
    update_challenge_review(console, selected_challenge["id"], grade)
    shutil.rmtree(folder_name)


def vscode_flow(console, folder_name, challenge_path):
    if os.path.isdir(folder_name):
        subprocess.run(["code", folder_name])
    else:
        console.print("Challenge folder does not exist!")
    input("Press ENTER once the challenge is solved...")
    generate_challenge_prompt(console, challenge_path)


def add_new_challenge(console):
    """
    Prompts the user to add a new challenge and saves it to the database.
    """
    title = questionary.text("Enter the title of the challenge:").ask()
    description = questionary.text(
        "Enter the description of the challenge:"
    ).ask()
    language = questionary.select(
        "Choose the language for the challenge:",
        choices=["python", "javascript"],
    ).ask()
    testcases = questionary.text("Enter test cases (optional):").ask()

    if title and description and language:
        add_challenge(title, description, language, testcases)
        console.print("[bold green]Challenge added successfully![/bold green]")
    else:
        console.print(
            "[bold red]All required fields must be filled![/bold red]"
        )


def delete_existing_challenge(console):
    """
    Allows the user to delete an existing challenge.
    """
    challenges = get_all_challenges()
    if not challenges:
        console.print("[bold red]No challenges in the database to delete![/bold red]")
        return
    challenge_choices = [f"ID: {c['id']} - {c['title']}" for c in challenges]
    selected = questionary.select(
        "Select a challenge to delete:", choices=challenge_choices
    ).ask()
    if not selected:
        console.print("[bold yellow]No challenge selected.[/bold yellow]")
        return
    selected_id = int(selected.split(":")[1].strip().split(" ")[0])
    confirm = questionary.confirm(
        f"Are you sure you want to delete this challenge? This action cannot be undone."
    ).ask()
    if not confirm:
        console.print("[bold yellow]Deletion cancelled.[/bold yellow]")
        return
    try:
        if delete_challenge(selected_id):
            console.print(f"[bold green]Challenge ID {selected_id} has been deleted.[/bold green]")
        else:
            console.print(f"[bold red]Failed to delete challenge ID {selected_id}.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error deleting challenge: {e}[/bold red]")


def list_challenges(console):
    """
    Lists all challenges in the database.
    """
    challenges = get_all_challenges()
    if challenges:
        console.print("[bold cyan]All Challenges:[/bold cyan]")
        for challenge in challenges:
            console.print(
                f"[bold yellow]ID {challenge['id']}[/bold yellow]:"
                + f" {challenge['title']} "
                f"(Language: {challenge['language']}, Interval:"
                + f" {challenge['interval']}, "
                f"Last Reviewed: {challenge['last_reviewed']})"
            )
    else:
        console.print(
            "[bold green]No challenges in the database yet![/bold green]"
        )


def add_testcases_to_challenge(console):
    """
    Allows the user to add test cases to an existing challenge that currently
    lacks it.
    """
    challenges = get_challenges_without_testcases()

    if not challenges:
        console.print(
            "[bold green]All challenges already have test cases![/bold green]"
        )
        return

    challenge_choices = [f"ID: {c['id']} - {c['title']}" for c in challenges]
    selected = questionary.select(
        "Select a challenge to add testcases:", choices=challenge_choices
    ).ask()

    if not selected:
        console.print("[bold yellow]No challenge selected.[/bold yellow]")
        return

    selected_id = int(selected.split(":")[1].strip().split(" ")[0])
    testcases = questionary.text(
        "Enter test cases (format as needed/imports aren't necessary):"
    ).ask()

    if not testcases.strip():
        console.print("[bold red]Test cases cannot be empty![/bold red]")
        return
    update_challenge_testcases(selected_id, testcases)
    console.print("[bold green]Test cases added successfully![/bold green]")


def update_existing_challenge(console):
    """
    Allows the user to update an existing challenge.
    """
    challenges = get_all_challenges()
    if not challenges:
        console.print("[bold red]No challenges in the database to update![/bold red]")
        return
    challenge_choices = [f"ID: {c['id']} - {c['title']}" for c in challenges]
    selected = questionary.select(
        "Select a challenge to update:", choices=challenge_choices
    ).ask()
    if not selected:
        console.print("[bold yellow]No challenge selected.[/bold yellow]")
        return
    selected_id = int(selected.split(":")[1].strip().split(" ")[0])
    selected_challenge = next(c for c in challenges if c['id'] == selected_id)
    console.print(f"[bold cyan]Current title:[/bold cyan] {selected_challenge['title']}")
    console.print(f"[bold cyan]Current description:[/bold cyan] {selected_challenge['description']}")
    console.print(f"[bold cyan]Current language:[/bold cyan] {selected_challenge['language']}")
    update_title = questionary.confirm("Update the title?").ask()
    new_title = None
    if update_title:
        new_title = questionary.text(
            "Enter the new title:", default=selected_challenge['title']
        ).ask()
    update_description = questionary.confirm("Update the description?").ask()
    new_description = None
    if update_description:
        new_description = questionary.text(
            "Enter the new description:", default=selected_challenge['description']
        ).ask()
    update_language = questionary.confirm("Update the language?").ask()
    new_language = None
    if update_language:
        new_language = questionary.select(
            "Choose the new language:",
            choices=["python", "javascript"],
            default=selected_challenge['language']
        ).ask()
    update_testcases = questionary.confirm("Update the test cases?").ask()
    new_testcases = None
    if update_testcases:
        new_testcases = questionary.text(
            "Enter the new test cases:", default=selected_challenge['testcases'] or ""
        ).ask()
    if any([update_title, update_description, update_language, update_testcases]):
        update_challenge(selected_id, new_title, new_description, new_language, new_testcases)
        console.print("[bold green]Challenge updated successfully![/bold green]")
    else:
        console.print("[bold yellow]No changes made.[/bold yellow]")
