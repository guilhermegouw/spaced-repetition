import os
import tempfile

import pyperclip
import questionary

from db.operations import (add_question, delete_question, get_all_questions,
                           get_due_questions, mark_reviewed, update_question)
from templates import QUESTION_PROMPT_TEMPLATE


def select_due_question(console):
    """
    Fetches due questions and prompts the user to select one.
    Returns the selected question or None if no selection is made.
    """
    due_questions = get_due_questions()

    if not due_questions:
        console.print(
            "[bold green]No questions are due for review today![/bold green]"
        )
        return None

    console.print("[bold cyan]Questions due for review:[/bold cyan]")
    question_choices = [
        f"ID: {q['id']} - {q['question']}" for q in due_questions
    ]
    selected = questionary.select(
        "Select a question to answer:", choices=question_choices
    ).ask()
    if not selected:
        console.print("[bold yellow]No question selected.[/bold yellow]")
        return None

    selected_id = int(selected.split(":")[1].strip().split(" ")[0])
    return next(q for q in due_questions if q["id"] == selected_id)


def open_editor_for_question(selected_question):
    """
    Opens the editor for the selected question and retrieves the user's answer.
    Returns the user's answer as a string.
    """
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
        temp_file.write(
            f"Question: {selected_question['question']}\n\n".encode("utf-8")
        )
        temp_path = temp_file.name

    os.system(f"{os.getenv('EDITOR', 'nvim')} {temp_path}")

    with open(temp_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    os.unlink(temp_path)

    lines = content.split("\n")
    question = lines[0].replace("Question: ", "").strip()
    answer = "\n".join(lines[2:]).strip()
    return question, answer


def generate_question_prompt(console, question, answer):
    """
    Generates the evaluation prompt for the given question and answer.
    Copies the prompt to the clipboard and returns it.
    """
    prompt = QUESTION_PROMPT_TEMPLATE.format(question=question, answer=answer)
    pyperclip.copy(prompt)
    console.print(prompt.strip())
    console.print("[bold green]Prompt copied to clipboard![/bold green]")
    return prompt


def update_question_review(console, question_id, grade):
    """
    Updates the SM-2 data for the given question based on the grade.
    """
    try:
        grade = float(grade)
        if 0 <= grade <= 3:
            mark_reviewed(question_id, grade)
            console.print(
                f"[bold green]Question ID {question_id} has been reviewed and updated.[/bold green]"
            )
        else:
            console.print(
                "[bold red]Invalid grade. Please enter a value between 0 and 3.[/bold red]"
            )
    except ValueError:
        console.print(
            "[bold red]Invalid input. Please enter a numeric value.[/bold red]"
        )


def review_questions(console):
    """
    Handles the review process:
    - Fetch due questions.
    - Display a question and capture the user's answer.
    - Generate a formatted prompt for copying.
    - Wait for the user's input of the grade.
    - Update the question's review status and parameters based on the grade.
    """
    selected_question = select_due_question(console)
    if not selected_question:
        return
    question, answer = open_editor_for_question(selected_question)
    generate_question_prompt(console, question, answer)
    grade = questionary.text("Enter the average grade (0-3) received:").ask()
    update_question_review(console, selected_question["id"], grade)


def add_new_question(console):
    """
    Prompts the user to add a new question and saves it to the database.
    """
    question = questionary.text("Enter the question:").ask()
    tags = questionary.text("Enter tags (comma-separated, optional):").ask()

    if question:
        add_question(question, tags)
        console.print("[bold green]Question added successfully![/bold green]")
    else:
        console.print("[bold red]Question cannot be empty.[/bold red]")


def delete_existing_question(console):
    """
    Allows the user to delete an existing question.
    """
    questions = get_all_questions()
    if not questions:
        console.print("[bold red]No questions in the database to delete![/bold red]")
        return
    question_choices = [f"ID: {q['id']} - {q['question']}" for q in questions]
    selected = questionary.select(
        "Select a question to delete:", choices=question_choices
    ).ask()
    if not selected:
        console.print("[bold yellow]No question selected.[/bold yellow]")
        return
    selected_id = int(selected.split(":")[1].strip().split(" ")[0])
    confirm = questionary.confirm(
        f"Are you sure you want to delete this question? This action cannot be undone."
    ).ask()
    if not confirm:
        console.print("[bold yellow]Deletion cancelled.[/bold yellow]")
        return
    try:
        if delete_question(selected_id):
            console.print(f"[bold green]Question ID {selected_id} has been deleted.[/bold green]")
        else:
            console.print(f"[bold red]Failed to delete question ID {selected_id}.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error deleting question: {e}[/bold red]")


def list_questions(console):
    """
    Lists all questions in the database.
    """
    questions = get_all_questions()
    if questions:
        console.print("[bold cyan]All Questions:[/bold cyan]")
        for question in questions:
            console.print(
                f"[bold yellow]ID {question['id']}[/bold yellow]:"
                + f" {question['question']} "
                f"(Tags: {question['tags']}, "
                f"Interval: {question['interval']}, "
                f"Last Reviewed: {question['last_reviewed']})"
            )
    else:
        console.print(
            "[bold green]No questions in the database yet![/bold green]"
        )


def update_existing_question(console):
    """
    Allows the user to update an existing question.
    """
    questions = get_all_questions()
    if not questions:
        console.print("[bold red]No questions in the database to update![/bold red]")
        return
    question_choices = [f"ID: {q['id']} - {q['question']}" for q in questions]
    selected = questionary.select(
        "Select a question to update:", choices=question_choices
    ).ask()
    if not selected:
        console.print("[bold yellow]No question selected.[/bold yellow]")
        return
    selected_id = int(selected.split(":")[1].strip().split(" ")[0])
    selected_question = next(q for q in questions if q['id'] == selected_id)
    # Ask what to update
    console.print(f"[bold cyan]Current question:[/bold cyan] {selected_question['question']}")
    console.print(f"[bold cyan]Current tags:[/bold cyan] {selected_question['tags']}")
    update_question_text = questionary.confirm("Update the question text?").ask()
    new_question = None
    if update_question_text:
        new_question = questionary.text(
            "Enter the new question text:", default=selected_question['question']
        ).ask()
    update_tags = questionary.confirm("Update the tags?").ask()
    new_tags = None
    if update_tags:
        new_tags = questionary.text(
            "Enter the new tags (comma-separated):", default=selected_question['tags'] or ""
        ).ask()
    if update_question_text or update_tags:
        update_question(selected_id, new_question, new_tags)
        console.print("[bold green]Question updated successfully![/bold green]")
    else:
        console.print("[bold yellow]No changes made.[/bold yellow]")
