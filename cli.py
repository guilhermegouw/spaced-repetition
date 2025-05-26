import questionary
import typer
from rich.console import Console

from helpers.challenges import (add_new_challenge, add_testcases_to_challenge,
                                delete_existing_challenge, list_challenges,
                                review_challenges, update_existing_challenge)
from helpers.mcq_questions import (add_new_mcq_question, list_mcq_questions,
                                   review_mcq_questions,
                                   update_existing_mcq_question)
from helpers.questions import (add_new_question, delete_existing_question,
                               list_questions, review_questions,
                               update_existing_question)

app = typer.Typer()
console = Console()


@app.command()
def add():
    """
    Add a new question to the database.
    """
    add_type = questionary.select(
        "What would you like to add?", choices=[
            "Question", "Challenge", "MCQ Question"
            ]
    ).ask()

    if add_type == "Question":
        add_new_question(console)

    elif add_type == "Challenge":
        add_new_challenge(console)
    elif add_type == "MCQ Question":
        add_new_mcq_question(console)


@app.command()
def review():
    """
    Review due questions and update their SM-2 values.
    """
    review_type = questionary.select(
        "What would you like to review?", choices=[
            "Questions", "Challenges", "MCQ Questions"
        ]
    ).ask()

    if review_type == "Questions":
        review_questions(console)
    elif review_type == "Challenges":
        review_challenges(console)
    elif review_type == "MCQ Questions":
        review_mcq_questions(console)


@app.command()
def list():
    """
    List all questions and challenges in the database.
    """
    list_type = questionary.select(
        "What would you like to list?", choices=[
            "Questions", "Challenges", "MCQ Questions"
        ]
    ).ask()

    if list_type == "Questions":
        list_questions(console)
    elif list_type == "Challenges":
        list_challenges(console)
    elif list_type == "MCQ Questions":
        list_mcq_questions(console)


@app.command()
def update():
    """
    Update an existing question or challenge.
    """
    update_type = questionary.select(
        "What would you like to update?", choices=[
            "Question", "Challenge", "MCQ Question"
        ]
    ).ask()

    if update_type == "Question":
        update_existing_question(console)
    elif update_type == "Challenge":
        update_existing_challenge(console)
    elif update_type == "MCQ Question":
        update_existing_mcq_question(console)


@app.command()
def delete():
    """
    Delete an existing question or challenge from the database.
    """
    delete_type = questionary.select(
        "What would you like to delete?", choices=["Question", "Challenge"]
    ).ask()

    if delete_type == "Question":
        delete_existing_question(console)
    elif delete_type == "Challenge":
        delete_existing_challenge(console)


@app.command()
def add_testcases():
    """
    Add test cases to an existing challenge that has none.
    """
    add_testcases_to_challenge(console)


if __name__ == "__main__":
    app()
