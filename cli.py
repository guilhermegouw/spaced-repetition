import sys
from pathlib import Path

import questionary
import typer
from rich.console import Console

from src.controllers.challenge import ChallengeController
from src.controllers.export_import import ExportController, ImportController
from src.controllers.mcq import MCQController
from src.controllers.question import QuestionController

sys.path.append(str(Path(__file__).parent / "src"))

app = typer.Typer()
console = Console()

question_controller = QuestionController()
challenge_controller = ChallengeController()
mcq_controller = MCQController()
export_controller = ExportController()
import_controller = ImportController()


@app.command()
def add():
    """
    Add a new item to the database.
    """
    add_type = questionary.select(
        "What would you like to add?",
        choices=["Question", "Challenge", "MCQ Question"],
    ).ask()

    if add_type == "Question":
        question_controller.add_question()
    elif add_type == "Challenge":
        challenge_controller.add_challenge()
    elif add_type == "MCQ Question":
        mcq_controller.add_mcq_question()


@app.command()
def review():
    """
    Review due items and update their SM-2 values.
    """
    review_type = questionary.select(
        "What would you like to review?",
        choices=["Questions", "Challenges", "MCQ Questions"],
    ).ask()

    if review_type == "Questions":
        question_controller.review_questions()
    elif review_type == "Challenges":
        challenge_controller.review_challenges()
    elif review_type == "MCQ Questions":
        mcq_controller.review_mcq_questions()


@app.command()
def list():
    """
    List all items in the database.
    """
    list_type = questionary.select(
        "What would you like to list?",
        choices=["Questions", "Challenges", "MCQ Questions"],
    ).ask()

    if list_type == "Questions":
        question_controller.list_questions()
    elif list_type == "Challenges":
        challenge_controller.list_challenges()
    elif list_type == "MCQ Questions":
        mcq_controller.list_mcq_questions()


@app.command()
def update():
    """
    Update an existing item.
    """
    update_type = questionary.select(
        "What would you like to update?",
        choices=["Question", "Challenge", "MCQ Question"],
    ).ask()

    if update_type == "Question":
        question_controller.update_question()
    elif update_type == "Challenge":
        challenge_controller.update_challenge()
    elif update_type == "MCQ Question":
        mcq_controller.update_mcq_question()


@app.command()
def delete():
    """
    Delete an existing item from the database.
    """
    delete_type = questionary.select(
        "What would you like to delete?",
        choices=["Question", "Challenge", "MCQ Question"],
    ).ask()

    if delete_type == "Question":
        question_controller.delete_question()
    elif delete_type == "Challenge":
        challenge_controller.delete_challenge()
    elif delete_type == "MCQ Question":
        mcq_controller.delete_mcq_question()


@app.command()
def add_testcases():
    """
    Add test cases to an existing challenge that has none.
    """
    challenge_controller.add_testcases()


@app.command()
def stats():
    """
    Display statistics about your spaced repetition system.
    """
    console.print("[bold cyan]📊 Spaced Repetition Statistics[/bold cyan]\n")

    question_stats = question_controller.get_question_stats()
    challenge_stats = challenge_controller.get_challenge_stats()
    mcq_stats = mcq_controller.get_mcq_stats()

    if question_stats:
        console.print("[bold yellow]📝 Questions:[/bold yellow]")
        console.print(f"  Total: {question_stats['total_questions']}")
        console.print(f"  Due for review: {question_stats['due_for_review']}")
        console.print(f"  Never reviewed: {question_stats['never_reviewed']}")
        console.print(
            f"  Average interval: {question_stats['average_interval']:.1f} days"
        )
        console.print(
            f"  Average ease factor: {question_stats['average_ease_factor']:.2f}"
        )
        console.print()

    if challenge_stats:
        console.print("[bold yellow]🧩 Challenges:[/bold yellow]")
        console.print(f"  Total: {challenge_stats['total_challenges']}")
        console.print(f"  Due for review: {challenge_stats['due_for_review']}")
        console.print(
            f"  Without test cases: {challenge_stats['without_testcases']}"
        )
        console.print(f"  Python: {challenge_stats['python_challenges']}")
        console.print(
            f"  JavaScript: {challenge_stats['javascript_challenges']}"
        )
        console.print(
            f"  Average interval: {challenge_stats['average_interval']:.1f} days"
        )
        console.print(
            f"  Average ease factor: {challenge_stats['average_ease_factor']:.2f}"
        )
        console.print()

    if mcq_stats:
        console.print("[bold yellow]❓ MCQ Questions:[/bold yellow]")
        console.print(f"  Total: {mcq_stats['total_mcq_questions']}")
        console.print(f"  Due for review: {mcq_stats['due_for_review']}")
        console.print(f"  Never reviewed: {mcq_stats['never_reviewed']}")
        console.print(f"  Multiple choice: {mcq_stats['mcq_questions']}")
        console.print(f"  True/False: {mcq_stats['true_false_questions']}")
        console.print(
            f"  Average interval: {mcq_stats['average_interval']:.1f} days"
        )
        console.print(
            f"  Average ease factor: {mcq_stats['average_ease_factor']:.2f}"
        )
        console.print()

    total_items = 0
    total_due = 0

    if question_stats:
        total_items += question_stats["total_questions"]
        total_due += question_stats["due_for_review"]

    if challenge_stats:
        total_items += challenge_stats["total_challenges"]
        total_due += challenge_stats["due_for_review"]

    if mcq_stats:
        total_items += mcq_stats["total_mcq_questions"]
        total_due += mcq_stats["due_for_review"]

    console.print("[bold green]📈 Overall Summary:[/bold green]")
    console.print(f"  Total items: {total_items}")
    console.print(f"  Items due for review: {total_due}")

    if total_items > 0:
        completion_rate = ((total_items - total_due) / total_items) * 100
        console.print(f"  Up to date: {completion_rate:.1f}%")


@app.command()
def quick_review():
    """
    Quick review session - automatically shows the most overdue items.
    """
    console.print("[bold cyan]🚀 Quick Review Session[/bold cyan]\n")

    try:
        due_questions = question_controller.repository.get_due_questions()
        due_challenges = challenge_controller.repository.get_due_challenges()
        due_mcqs = mcq_controller.repository.get_due_questions()

        total_due = len(due_questions) + len(due_challenges) + len(due_mcqs)

        if total_due == 0:
            console.print(
                "[bold green]🎉 All caught up! No items due for review.[/bold green]"
            )
            return

        console.print(f"[bold yellow]📋 Items due for review:[/bold yellow]")
        console.print(f"  Questions: {len(due_questions)}")
        console.print(f"  Challenges: {len(due_challenges)}")
        console.print(f"  MCQ Questions: {len(due_mcqs)}")
        console.print(f"  Total: {total_due}\n")

        review_options = []
        if due_questions:
            review_options.append("Questions")
        if due_challenges:
            review_options.append("Challenges")
        if due_mcqs:
            review_options.append("MCQ Questions")

        if len(review_options) == 1:
            review_type = review_options[0]
        else:
            review_type = questionary.select(
                "What would you like to review first?",
                choices=review_options + ["Cancel"],
            ).ask()

        if review_type == "Questions":
            question_controller.review_questions()
        elif review_type == "Challenges":
            challenge_controller.review_challenges()
        elif review_type == "MCQ Questions":
            mcq_controller.review_mcq_questions()

    except Exception as e:
        console.print(
            f"[bold red]Error during quick review: {str(e)}[/bold red]"
        )


@app.command()
def health_check():
    """
    Check the health of your spaced repetition system.
    """
    console.print("[bold cyan]🔍 System Health Check[/bold cyan]\n")

    try:
        console.print("[bold yellow]Database Connections:[/bold yellow]")

        question_count = len(question_controller.repository.get_all())
        console.print(f"  ✓ Questions repository: {question_count} items")
        challenge_count = len(challenge_controller.repository.get_all())
        console.print(f"  ✓ Challenges repository: {challenge_count} items")
        mcq_count = len(mcq_controller.repository.get_all())
        console.print(f"  ✓ MCQ Questions repository: {mcq_count} items")
        console.print()

        console.print("[bold yellow]System Health:[/bold yellow]")
        challenges_without_testcases = (
            challenge_controller.repository.get_challenges_without_testcases()
        )
        if challenges_without_testcases:
            console.print(
                f"  ⚠️  {len(challenges_without_testcases)} challenges missing test cases"
            )
        else:
            console.print("  ✓ All challenges have test cases")

        all_questions = question_controller.repository.get_all()
        never_reviewed_questions = [
            q for q in all_questions if q.last_reviewed is None
        ]
        if never_reviewed_questions:
            console.print(
                f"  ⚠️  {len(never_reviewed_questions)} questions never reviewed"
            )
        else:
            console.print("  ✓ All questions have been reviewed")

        console.print(
            "\n[bold green]✅ System health check completed![/bold green]"
        )

    except Exception as e:
        console.print(f"[bold red]❌ Health check failed: {str(e)}[/bold red]")


@app.command()
def export(
    output: str = typer.Option(
        None, "--output", "-o", help="Output file path"
    ),
    item_type: str = typer.Option(
        None,
        "--type",
        "-t",
        help="Filter by type: questions, challenges, or mcq",
    ),
    tags: str = typer.Option(
        None, "--tags", help="Filter by tags (comma-separated)"
    ),
):
    """
    Export questions, challenges, and/or MCQs to JSON file.
    """
    console.print("[bold cyan]📤 Exporting data...[/bold cyan]\n")

    # Validate item_type
    if item_type and item_type not in ["questions", "challenges", "mcq"]:
        console.print(
            "[bold red]Error: --type must be one of: questions, challenges, mcq[/bold red]"
        )
        return

    export_controller.export_all(
        output_file=output, item_type=item_type, tags=tags
    )


@app.command()
def import_data(
    file: str = typer.Argument(..., help="JSON file to import"),
    allow_duplicates: bool = typer.Option(
        False,
        "--allow-duplicates",
        help="Allow importing duplicate items (default: skip duplicates)",
    ),
):
    """
    Import questions, challenges, and MCQs from JSON file.
    """
    console.print("[bold cyan]📥 Importing data...[/bold cyan]\n")

    import_controller.import_from_file(
        input_file=file, skip_duplicates=not allow_duplicates
    )


if __name__ == "__main__":
    app()
