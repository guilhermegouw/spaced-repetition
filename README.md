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

5. Configure environment variables:
```
cp .env-sample .env
```

Edit `.env` and configure your settings (see API Configuration below).

##### API Configuration (Z.AI / GLM)

The app integrates with Z.AI's GLM API for automatic evaluation of your challenge solutions. To enable this feature:

1. **Get your API key**: Visit [Z.AI API Key Management](https://z.ai/manage-apikey/apikey-list) and create an API key.

2. **Configure the `.env` file**:
```
# Required: Your Z.AI API key
ZAI_API_KEY=your-api-key-here

# Optional: API endpoint ("default" or "coding" for coding-specific evaluation)
ZAI_BASE_URL=default

# Optional: Enable/disable API evaluation (default: true)
ZAI_ENABLED=true

# Optional: Fall back to clipboard if API fails (default: true)
USE_CLIPBOARD_FALLBACK=true
```

**Notes:**
- The app uses the `glm-4.7` model by default
- If `ZAI_ENABLED=false` or no API key is configured, the app will copy evaluation prompts to your clipboard instead
- When `USE_CLIPBOARD_FALLBACK=true`, the app will automatically fall back to clipboard if the API call fails

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

