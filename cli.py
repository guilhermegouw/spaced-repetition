import questionary
import typer
from rich.console import Console

from helpers.challenges import (add_new_challenge, list_challenges,
                                review_challenges)
from helpers.questions import (add_new_question, list_questions,
                               review_questions)

app = typer.Typer()
console = Console()


@app.command()
def add():
    """
    Add a new question to the database.
    """
    add_type = questionary.select(
        "What would you like to add?", choices=["Question", "Challenge"]
    ).ask()

    if add_type == "Question":
        add_new_question(console)

    elif add_type == "Challenge":
        add_new_challenge(console)


@app.command()
def review():
    """
    Review due questions and update their SM-2 values.
    """
    review_type = questionary.select(
        "What would you like to review?", choices=["Questions", "Challenges"]
    ).ask()

    if review_type == "Questions":
        review_questions(console)
    elif review_type == "Challenges":
        review_challenges(console)


@app.command()
def list():
    """
    List all questions and challenges in the database.
    """
    list_type = questionary.select(
        "What yould you like to list?", choices=["Questions", "Challenges"]
    ).ask()

    if list_type == "Questions":
        list_questions(console)
    elif list_type == "Challenges":
        list_challenges(console)


if __name__ == "__main__":
    app()
