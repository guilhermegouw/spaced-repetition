QUESTION_PROMPT_TEMPLATE = """
Hi Huyang, please evaluate my answer to the following question based on:
- Accuracy (0-3)
- Completeness (0-3)
- Clarity (0-3)

Please provide an average grade calculated as:
(Average Grade = (Accuracy + Completeness + Clarity) / 3)

Question:
{question}

Answer:
{answer}

Thank you!
"""

CHALLENGE_PROMPT_TEMPLATE = """
Hi Huyang, please evaluate my solution for the following challenge
based on these criteria:\n
    **Correctness** (0-3): Does the solution produce the correct results?\n
    **Clarity** (0-3): Is the code easy to understand?\n
    **Efficiency** (0-3): Is the solution optimized for performance?\n\n
    Score (0–3): (Correctness + Clarity + Efficiency) / 3\n
Here is the full content of my solution:\n
{challenge_content}\n\n
Please provide your evaluation + Score."
"""
