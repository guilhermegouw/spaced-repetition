### Spaced Repetition App

The Spaced Repetition App is a powerful CLI tool to help you efficiently review and retain knowledge using the Spaced Repetition Algorithm (SM-2). It allows you to track questions and coding challenges, ensuring you learn and improve over time.

#### Features
- *Add and Manage Questions*: Add custom questions with optional tags for categorization.
- *Code Challenge Reviews*: Add coding challenges in Python or JavaScript with support for test files.
- *Spaced Repetition Algorithm*: Automatically calculates the next review interval based on your performance.
- *Integration with Editors*: Edit solutions and answers using your preferred text editor.
- *Rich Evaluation Prompts*: Generate evaluation prompts and copy them to the clipboard for external use.
- *Cross-language Support*: Handles Python and JavaScript challenges with appropriate setups.

#### Getting Started
##### Prerequisites
1. Python: Install Python 3.8+.
2. Node.js and NPM: Install Node.js for JavaScript challenges.

##### Installation
1. Clone the repository:
```
git clone https://github.com/your-username/spaced-repetition-app.git
cd spaced-repetition-app
```

2. Set up the Python environment:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Initialize the SQLite database:
```
python main.py
```

4. Set up JavaScript testing environment: 
```
npm install
```

#### Usage

##### Add a Question
```
python cli.py add
```

- Choose Question.
- Enter the question text.
- Optionally, provide tags for categorization.

##### Add a Coding Challenge
```
python cli.py add
```

- Choose Challenge.
- Enter the question text.
- Optionally, provide tags for categorization.

