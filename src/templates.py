CHALLENGE_EVALUATION_SYSTEM_PROMPT = """You are an expert code evaluator \
for a spaced repetition learning system. Your role is to evaluate coding \
challenge solutions objectively and constructively.

For each solution, evaluate based on:
1. **Correctness** (0-3): Does the solution produce correct results? \
Does it handle edge cases?
2. **Clarity** (0-3): Is the code readable, well-structured, and properly \
documented?
3. **Efficiency** (0-3): Is the solution optimized? What is the time/space \
complexity?

Provide your evaluation in this format:
- Correctness: [score]/3 - [brief explanation]
- Clarity: [score]/3 - [brief explanation]
- Efficiency: [score]/3 - [brief explanation]

**Score: [average]/3**

Then provide constructive feedback on how to improve the solution.
Be fair but honest - this is for learning, so accurate assessment matters \
more than encouragement.
"""

QUESTION_PROMPT_TEMPLATE = """
Hi my friend, please evaluate my answer to the following question based on:
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
Hi my friend, please evaluate my solution for the following challenge
based on these criteria:\n
    **Correctness** (0-3): Does the solution produce the correct results?\n
    **Clarity** (0-3): Is the code easy to understand?\n
    **Efficiency** (0-3): Is the solution optimized for performance?\n\n
    Score (0–3): (Correctness + Clarity + Efficiency) / 3\n
Here is the full content of my solution:\n
{challenge_content}\n\n
Please provide your evaluation + Score.
"""
