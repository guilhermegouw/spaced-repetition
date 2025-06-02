import random

import questionary

from db.operations import (add_mcq_question, get_all_mcq_questions,
                           get_due_mcq_questions, get_mcq_question_by_id,
                           mark_reviewed_mcq, update_mcq_question)


def add_new_mcq_question(console):
    """
    Prompts the user to add a new MCQ question and saves it to the database.
    """
    question = questionary.text("Enter the question:").ask()
    if not question:
        console.print("[bold red]Question cannot be empty.[/bold red]")
        return

    question_type = questionary.select(
        "What type of question is this?",
        choices=["mcq", "true_false"]
    ).ask()

    if not question_type:
        console.print("[bold yellow]No question type selected.[/bold yellow]")
        return

    if question_type == "true_false":
        option_a = "True"
        option_b = "False"
        option_c = None
        option_d = None

        correct_option = questionary.select(
            "Which is the correct answer?",
            choices=["a (True)", "b (False)"]
        ).ask()

        if not correct_option:
            console.print("[bold yellow]No correct option selected.[/bold yellow]")
            return

        correct_option = correct_option[0]

        console.print("\n[bold cyan]Now let's add explanations for each option:[/bold cyan]")
        
        if correct_option == 'a':
            explanation_a = questionary.text("Explain why 'True' is correct:").ask()
            explanation_b = questionary.text("Explain why 'False' is incorrect:").ask()
        else:
            explanation_a = questionary.text("Explain why 'True' is incorrect:").ask()
            explanation_b = questionary.text("Explain why 'False' is correct:").ask()
        
        explanation_c = None
        explanation_d = None

    else:
        option_a = questionary.text("Enter option A:").ask()
        option_b = questionary.text("Enter option B:").ask()
        option_c = questionary.text("Enter option C:").ask()
        option_d = questionary.text("Enter option D:").ask()

        if not all([option_a, option_b, option_c, option_d]):
            console.print(
                    "[bold red]All four options are required for MCQ questions.[/bold red]"
            )
            return

        choices = [
            f"a) {option_a}",
            f"b) {option_b}",
            f"c) {option_c}",
            f"d) {option_d}"
        ]

        correct_choice = questionary.select(
            "Which option is correct?",
            choices=choices
        ).ask()

        if not correct_choice:
            console.print("[bold yellow]No correct option selected.[/bold yellow]")
            return

        correct_option = correct_choice[0]

        console.print("\n[bold cyan]Now let's add explanations for each option:[/bold cyan]")
        
        explanation_a = questionary.text(
            f"Explain option A ({option_a}) - {'CORRECT' if correct_option == 'a' else 'Why it is wrong'}:"
        ).ask()
        
        explanation_b = questionary.text(
            f"Explain option B ({option_b}) - {'CORRECT' if correct_option == 'b' else 'Why it is wrong'}:"
        ).ask()
        
        explanation_c = questionary.text(
            f"Explain option C ({option_c}) - {'CORRECT' if correct_option == 'c' else 'Why it is wrong'}:"
        ).ask()
        
        explanation_d = questionary.text(
            f"Explain option D ({option_d}) - {'CORRECT' if correct_option == 'd' else 'Why it is wrong'}:"
        ).ask()

    tags = questionary.text("Enter tags (comma-separated, optional):").ask()
    if not tags:
        tags = None

    try:
        add_mcq_question(
            question=question,
            question_type=question_type,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_option=correct_option,
            tags=tags,
            explanation_a=explanation_a,
            explanation_b=explanation_b,
            explanation_c=explanation_c,
            explanation_d=explanation_d
        )
        console.print("[bold green]MCQ question added successfully![/bold green]")
        console.print(f"[bold cyan]Question:[/bold cyan] {question}")
        console.print(f"[bold cyan]Type:[/bold cyan] {question_type}")
        console.print(f"[bold cyan]Correct answer:[/bold cyan] {correct_option.upper()}")
        if tags:
            console.print(f"[bold cyan]Tags:[/bold cyan] {tags}")
    except Exception as e:
        console.print(f"[bold red]Error adding MCQ question: {e}[/bold red]")


def list_mcq_questions(console):
    """
    Lists all MCQ questions in the database.
    """
    mcq_questions = get_all_mcq_questions()
    if mcq_questions:
        console.print("[bold cyan]All MCQ Questions:[/bold cyan]")
        for question in mcq_questions:
            console.print(
                f"[bold yellow]ID {question['id']}[/bold yellow]: "
                f"{question['question']} "
                f"(Type: {question['question_type']}, "
                f"Tags: {question['tags'] or 'None'}, "
                f"Interval: {question['interval']}, "
                f"Last Reviewed: {question['last_reviewed'] or 'Never'})"
            )
    else:
        console.print(
            "[bold green]No MCQ questions in the database yet![/bold green]"
        )


def update_existing_mcq_question(console):
    """
    Allows the user to update an existing MCQ question.
    """
    mcq_questions = get_all_mcq_questions()
    if not mcq_questions:
        console.print("[bold red]No MCQ questions in the database to update![/bold red]")
        return
    question_choices = [f"ID: {q['id']} - {q['question']}" for q in mcq_questions]
    selected = questionary.select(
        "Select an MCQ question to update:", choices=question_choices
    ).ask()
    if not selected:
        console.print("[bold yellow]No question selected.[/bold yellow]")
        return
    selected_id = int(selected.split(":")[1].strip().split(" ")[0])
    selected_question = next(q for q in mcq_questions if q['id'] == selected_id)
    console.print(f"[bold cyan]Current question:[/bold cyan] {selected_question['question']}")
    console.print(f"[bold cyan]Current type:[/bold cyan] {selected_question['question_type']}")
    console.print(f"[bold cyan]Current tags:[/bold cyan] {selected_question['tags'] or 'None'}")
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
        if not new_tags:
            new_tags = None
    if update_question_text or update_tags:
        try:
            update_mcq_question(selected_id, new_question, new_tags)
            console.print("[bold green]MCQ question updated successfully![/bold green]")
        except Exception as e:
            console.print(f"[bold red]Error updating MCQ question: {e}[/bold red]")
    else:
        console.print("[bold yellow]No changes made.[/bold yellow]")


def display_explanation(console, option_letter, option_text, explanation, is_correct, is_user_choice):
    """
    Helper function to display explanations with appropriate formatting.
    """
    if is_user_choice:
        if is_correct:
            console.print(f"\n[bold green]✓ Your choice: {option_letter.upper()}) {option_text}[/bold green]")
            console.print(f"[bold green]Why this is correct:[/bold green] {explanation}")
        else:
            console.print(f"\n[bold red]✗ Your choice: {option_letter.upper()}) {option_text}[/bold red]")
            console.print(f"[bold red]Why this is wrong:[/bold red] {explanation}")
    elif is_correct and not is_user_choice:
        console.print(f"\n[bold cyan]✓ Correct answer: {option_letter.upper()}) {option_text}[/bold cyan]")
        console.print(f"[bold cyan]Why this is correct:[/bold cyan] {explanation}")


def review_mcq_questions(console):
    """
    Handles the MCQ review process with 5-step UI flow:
    1. Get list of due questions (clean display)
    2. User selects question to answer
    3. Display question with randomized options
    4. Get user answer and confidence level
    5. Show feedback and update SM-2 with penalty system
    """
    # Step 1: Get due questions and display clean list
    due_questions = get_due_mcq_questions()
    if not due_questions:
        console.print("[bold green]No MCQ questions are due for review today![/bold green]")
        return
    console.print("[bold cyan]MCQ Questions due for review (sorted by priority):[/bold cyan]")
    question_choices = []
    for q in due_questions:
        days_overdue = round(q['days_overdue'], 1)
        choice_text = f"ID: {q['id']} - {q['question']} (Type: {q['question_type']}, {days_overdue} days overdue)"
        question_choices.append(choice_text)

    # Step 2: User selects question
    selected = questionary.select(
        "Select a question to review:", choices=question_choices
    ).ask()
    if not selected:
        console.print("[bold yellow]No question selected.[/bold yellow]")
        return
    selected_id = int(selected.split(":")[1].strip().split(" ")[0])
    question_data = get_mcq_question_by_id(selected_id)
    if not question_data:
        console.print("[bold red]Question not found![/bold red]")
        return

    # Step 3: Display question with randomized options
    console.print(f"\n[bold cyan]Question:[/bold cyan] {question_data['question']}")
    console.print(f"[bold cyan]Type:[/bold cyan] {question_data['question_type']}")
    if question_data['tags']:
        console.print(f"[bold cyan]Tags:[/bold cyan] {question_data['tags']}")
    options = []
    if question_data['question_type'] == 'true_false':
        options = [
            ('a', question_data['option_a']),
            ('b', question_data['option_b'])
        ]
    else:
        options = [
            ('a', question_data['option_a']),
            ('b', question_data['option_b']),
            ('c', question_data['option_c']),
            ('d', question_data['option_d'])
        ]
    # Randomize option order (option rotation feature!)
    random.shuffle(options)
    console.print("\n[bold yellow]Options:[/bold yellow]")
    display_choices = []
    option_mapping = {}  # Maps display letter to original letter
    for i, (original_letter, option_text) in enumerate(options):
        display_letter = chr(ord('a') + i)  # a, b, c, d for display
        option_mapping[display_letter] = original_letter
        console.print(f"  {display_letter}) {option_text}")
        display_choices.append(f"{display_letter}) {option_text}")
    # Get user's answer
    user_choice = questionary.select(
        "\nWhat is your answer?",
        choices=display_choices
    ).ask()
    if not user_choice:
        console.print("[bold yellow]No answer selected.[/bold yellow]")
        return
    user_answer_display = user_choice[0]  # Extract display letter (a, b, c, d)
    user_answer_original = option_mapping[user_answer_display]  # Map back to original

    # Step 4: Get confidence level
    confidence = questionary.select(
        "How confident are you in your answer?",
        choices=["low", "medium", "high"]
    ).ask()
    if not confidence:
        console.print("[bold yellow]No confidence level selected.[/bold yellow]")
        return

    # Step 5: Show feedback and update SM-2
    is_correct = (user_answer_original == question_data['correct_option'])
    console.print(f"\n[bold cyan]=== FEEDBACK ===[/bold cyan]")
    
    user_option_text = question_data[f'option_{user_answer_original}']
    user_explanation = question_data[f'explanation_{user_answer_original}']
    
    if user_explanation:
        display_explanation(
            console, 
            user_answer_original, 
            user_option_text, 
            user_explanation, 
            is_correct, 
            True
        )
    
    if not is_correct:
        correct_option_text = question_data[f'option_{question_data["correct_option"]}']
        correct_explanation = question_data[f'explanation_{question_data["correct_option"]}']
        
        if correct_explanation:
            display_explanation(
                console,
                question_data['correct_option'],
                correct_option_text,
                correct_explanation,
                True,
                False
            )
    
    console.print(f"\n[bold cyan]Your confidence:[/bold cyan] {confidence}")
    
    # Apply penalty system and update SM-2
    try:
        mark_reviewed_mcq(selected_id, is_correct, confidence)
        console.print(f"[bold green]Question updated successfully![/bold green]")
        # Special feedback for corner cases
        if not is_correct and confidence == 'high':
            console.print("[bold yellow]⚠️  High confidence with wrong answer detected - applying enhanced penalty to combat misconception.[/bold yellow]")
        elif is_correct and confidence == 'low':
            console.print("[bold blue]ℹ️  Correct but uncertain - will progress conservatively to build confidence.[/bold blue]")
    except Exception as e:
        console.print(f"[bold red]Error updating question: {e}[/bold red]")
    
    another = questionary.confirm("Review another MCQ question?").ask()
    if another:
        review_mcq_questions(console)
