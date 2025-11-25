# Unit Testing Plan for Spaced Repetition Application

**Goal:** Achieve >85% code coverage with meaningful unit tests

## Executive Summary

| Layer | Files | Priority | Estimated Tests |
|-------|-------|----------|-----------------|
| Models | 4 | HIGH | ~45 tests |
| Repositories | 3 | HIGH | ~60 tests |
| Controllers | 4 | MEDIUM | ~50 tests |
| Views | 3 | LOW | ~20 tests |
| CLI | 1 | LOW | ~15 tests |
| Utils | 1 | MEDIUM | ~10 tests |
| **Total** | **16** | - | **~200 tests** |

---

## 1. Project Setup

### 1.1 Install Additional Test Dependencies

```bash
poetry add --group dev pytest-cov pytest-mock faker
```

- `pytest-cov`: Coverage reporting
- `pytest-mock`: Simplified mocking
- `faker`: Generate realistic test data

### 1.2 Create Test Directory Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── test_sm2.py
│   │   ├── test_question.py
│   │   ├── test_challenge.py
│   │   └── test_mcq.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── test_question_repository.py
│   │   ├── test_challenge_repository.py
│   │   └── test_mcq_repository.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── test_question_controller.py
│   │   ├── test_challenge_controller.py
│   │   ├── test_mcq_controller.py
│   │   └── test_export_import_controller.py
│   ├── views/
│   │   ├── __init__.py
│   │   ├── test_question_view.py
│   │   ├── test_challenge_view.py
│   │   └── test_mcq_view.py
│   └── utils/
│       ├── __init__.py
│       └── test_json_schema.py
└── integration/
    ├── __init__.py
    └── test_workflows.py
```

### 1.3 Configure pytest in pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = [
    "--cov=src",
    "--cov=cli",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=85"
]

[tool.coverage.run]
source = ["src", "cli.py"]
omit = ["tests/*", "*/__init__.py"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.:",
    "raise NotImplementedError"
]
```

---

## 2. Test Implementation Plan (By Priority)

### Phase 1: Models (Highest Priority - Pure Logic)

#### 2.1 SM2Calculator (`src/models/sm2.py`) - ~20 tests

**Why first:** Pure functions with no dependencies, core business logic.

| Test Case | Method | Description |
|-----------|--------|-------------|
| `test_calculate_next_review_rating_5` | `calculate_next_review` | Perfect response increases interval |
| `test_calculate_next_review_rating_4` | `calculate_next_review` | Good response increases interval |
| `test_calculate_next_review_rating_3` | `calculate_next_review` | Correct response maintains learning |
| `test_calculate_next_review_rating_2` | `calculate_next_review` | Hard response resets to 1 |
| `test_calculate_next_review_rating_1` | `calculate_next_review` | Wrong response resets to 1 |
| `test_calculate_next_review_rating_0` | `calculate_next_review` | Complete blackout resets |
| `test_ease_factor_minimum_bound` | `calculate_next_review` | EF never goes below 1.3 |
| `test_ease_factor_increases_on_good` | `calculate_next_review` | EF increases with good ratings |
| `test_interval_first_review` | `calculate_next_review` | Interval=1 → specific behavior |
| `test_interval_second_review` | `calculate_next_review` | Interval progression |
| `test_mcq_correct_high_confidence` | `calculate_mcq_review` | Best case MCQ scenario |
| `test_mcq_correct_low_confidence` | `calculate_mcq_review` | Correct but guessed |
| `test_mcq_wrong_high_confidence` | `calculate_mcq_review` | Misconception penalty |
| `test_mcq_wrong_low_confidence` | `calculate_mcq_review` | Expected mistake |
| `test_is_overdue_true` | `is_overdue` | Past due date |
| `test_is_overdue_false` | `is_overdue` | Not yet due |
| `test_is_overdue_today` | `is_overdue` | Due today = not overdue |
| `test_days_overdue_positive` | `days_overdue` | Calculate days past due |
| `test_days_overdue_zero` | `days_overdue` | Due today |
| `test_days_overdue_negative` | `days_overdue` | Not yet due |

#### 2.2 Question Model (`src/models/question.py`) - ~8 tests

| Test Case | Description |
|-----------|-------------|
| `test_question_valid_creation` | Valid question with all fields |
| `test_question_minimal_creation` | Only required fields |
| `test_question_empty_text_fails` | Validation rejects empty |
| `test_question_whitespace_only_fails` | Validation rejects whitespace |
| `test_question_tags_normalization` | Tags list normalization |
| `test_question_default_sm2_values` | Default interval/ease_factor |
| `test_question_with_id` | ID field handling |
| `test_question_serialization` | model_dump() works |

#### 2.3 Challenge Model (`src/models/challenge.py`) - ~10 tests

| Test Case | Description |
|-----------|-------------|
| `test_challenge_valid_python` | Valid Python challenge |
| `test_challenge_valid_javascript` | Valid JavaScript challenge |
| `test_challenge_invalid_language` | Invalid language rejected |
| `test_challenge_empty_title_fails` | Empty title validation |
| `test_challenge_empty_description_fails` | Empty description validation |
| `test_challenge_with_testcases` | Testcases string handling |
| `test_challenge_without_testcases` | Optional testcases |
| `test_challenge_tags_normalization` | Tags handling |
| `test_challenge_default_sm2_values` | Default SM2 values |
| `test_challenge_serialization` | model_dump() works |

#### 2.4 MCQQuestion Model (`src/models/mcq.py`) - ~15 tests

| Test Case | Description |
|-----------|-------------|
| `test_mcq_valid_creation` | Valid 4-option MCQ |
| `test_mcq_true_false_valid` | Valid true/false question |
| `test_mcq_true_false_requires_two_options` | TF needs only A/B |
| `test_mcq_type_requires_four_options` | MCQ needs A-D |
| `test_mcq_empty_question_fails` | Empty question rejected |
| `test_mcq_invalid_correct_option` | Invalid option letter |
| `test_mcq_explanations_optional` | Explanations not required |
| `test_mcq_all_explanations` | All 4 explanations |
| `test_mcq_partial_explanations` | Some explanations |
| `test_mcq_correct_option_uppercase` | Normalize to lowercase |
| `test_mcq_tags_handling` | Tags list processing |
| `test_mcq_default_type` | Defaults to 'mcq' |
| `test_mcq_serialization` | model_dump() works |
| `test_mcq_option_c_d_none_for_tf` | TF ignores C/D |
| `test_mcq_cross_validation` | Type-option consistency |

---

### Phase 2: Repositories (High Priority - Data Layer)

**Strategy:** Use in-memory SQLite database for isolation.

#### Shared Fixture (`conftest.py`)

```python
import pytest
import sqlite3
from src.db.schema import initialize_database
from src.db.database_manager import DatabaseManager

@pytest.fixture
def test_db():
    """Create in-memory database for testing."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    # Initialize schema
    cursor = conn.cursor()
    # Execute schema creation SQL
    initialize_database(conn)
    yield conn
    conn.close()

@pytest.fixture
def db_manager(test_db):
    """DatabaseManager with test database."""
    manager = DatabaseManager(test_db)
    return manager
```

#### 2.5 QuestionRepository (`src/repositories/question.py`) - ~20 tests

| Test Case | Description |
|-----------|-------------|
| `test_add_question` | Insert new question |
| `test_add_question_returns_id` | Returns inserted ID |
| `test_get_by_id_exists` | Retrieve existing question |
| `test_get_by_id_not_found` | Returns None for missing |
| `test_get_all_empty` | Empty database |
| `test_get_all_with_data` | Returns all questions |
| `test_get_due_questions` | Due date filtering |
| `test_get_due_questions_ordering` | Overdue first ordering |
| `test_get_due_questions_empty` | No due questions |
| `test_get_by_tags_single` | Single tag filter |
| `test_get_by_tags_multiple` | Multiple tags (AND) |
| `test_get_by_tags_no_match` | No matching tags |
| `test_update_question_text` | Update question text |
| `test_update_question_tags` | Update tags |
| `test_update_partial` | Partial update |
| `test_update_nonexistent` | Update missing ID |
| `test_delete_question` | Delete existing |
| `test_delete_nonexistent` | Delete missing ID |
| `test_mark_reviewed` | Update SM2 values |
| `test_row_to_question` | Row mapping |

#### 2.6 ChallengeRepository (`src/repositories/challenge.py`) - ~22 tests

| Test Case | Description |
|-----------|-------------|
| `test_add_challenge` | Insert new challenge |
| `test_add_challenge_with_testcases` | Challenge with testcases |
| `test_get_by_id_exists` | Retrieve existing |
| `test_get_by_id_not_found` | Returns None |
| `test_get_all_empty` | Empty database |
| `test_get_all_with_data` | Returns all |
| `test_get_due_challenges` | Due date filtering |
| `test_get_due_challenges_by_language` | Filter by Python/JS |
| `test_get_without_testcases` | Missing testcases query |
| `test_get_by_tags_single` | Single tag filter |
| `test_get_by_tags_multiple` | Multiple tags |
| `test_update_challenge_title` | Update title |
| `test_update_challenge_description` | Update description |
| `test_update_challenge_testcases` | Update testcases |
| `test_update_challenge_language` | Update language |
| `test_update_partial` | Partial update |
| `test_update_nonexistent` | Update missing |
| `test_delete_challenge` | Delete existing |
| `test_delete_nonexistent` | Delete missing |
| `test_mark_reviewed` | Update SM2 values |
| `test_add_testcases` | Add testcases to existing |
| `test_row_to_challenge` | Row mapping |

#### 2.7 MCQRepository (`src/repositories/mcq.py`) - ~20 tests

| Test Case | Description |
|-----------|-------------|
| `test_add_mcq` | Insert MCQ question |
| `test_add_true_false` | Insert true/false |
| `test_get_by_id_exists` | Retrieve existing |
| `test_get_by_id_not_found` | Returns None |
| `test_get_all_empty` | Empty database |
| `test_get_all_with_data` | Returns all |
| `test_get_due_mcqs` | Due date filtering |
| `test_get_due_mcqs_by_type` | Filter MCQ/TF |
| `test_get_by_tags` | Tag filtering |
| `test_update_mcq_question` | Update question text |
| `test_update_mcq_options` | Update options |
| `test_update_mcq_correct_option` | Update answer |
| `test_update_explanations` | Update explanations |
| `test_update_partial` | Partial update |
| `test_delete_mcq` | Delete existing |
| `test_mark_reviewed` | Update SM2 values |
| `test_mark_reviewed_with_misconception` | Penalty applied |
| `test_get_options` | Retrieve options dict |
| `test_get_explanations` | Retrieve explanations |
| `test_row_to_mcq` | Row mapping |

---

### Phase 3: Controllers (Medium Priority - Orchestration)

**Strategy:** Mock repositories and views.

#### 2.8 QuestionController (`src/controllers/question.py`) - ~12 tests

| Test Case | Description |
|-----------|-------------|
| `test_add_question_success` | Add flow succeeds |
| `test_add_question_cancelled` | User cancels |
| `test_review_with_due_questions` | Review flow |
| `test_review_no_due_questions` | Nothing to review |
| `test_list_questions` | List all |
| `test_list_questions_by_tags` | Filtered list |
| `test_update_question_success` | Update flow |
| `test_update_question_cancelled` | User cancels |
| `test_delete_question_confirmed` | Delete with confirm |
| `test_delete_question_cancelled` | Delete cancelled |
| `test_get_stats` | Statistics calculation |
| `test_quick_review` | Quick review mode |

#### 2.9 ChallengeController (`src/controllers/challenge.py`) - ~14 tests

| Test Case | Description |
|-----------|-------------|
| `test_add_challenge_success` | Add flow succeeds |
| `test_add_challenge_cancelled` | User cancels |
| `test_review_with_due_challenges` | Review flow |
| `test_review_no_due_challenges` | Nothing to review |
| `test_review_by_language` | Filter by language |
| `test_list_challenges` | List all |
| `test_list_by_tags` | Filtered list |
| `test_update_challenge_success` | Update flow |
| `test_update_challenge_cancelled` | User cancels |
| `test_delete_challenge_confirmed` | Delete confirmed |
| `test_delete_challenge_cancelled` | Delete cancelled |
| `test_add_testcases` | Add testcases flow |
| `test_get_stats` | Statistics |
| `test_workspace_management` | File I/O handling |

#### 2.10 MCQController (`src/controllers/mcq.py`) - ~12 tests

| Test Case | Description |
|-----------|-------------|
| `test_add_mcq_success` | Add MCQ flow |
| `test_add_true_false_success` | Add TF flow |
| `test_add_cancelled` | User cancels |
| `test_review_with_due` | Review flow |
| `test_review_no_due` | Nothing to review |
| `test_review_correct_answer` | Correct answer handling |
| `test_review_wrong_answer` | Wrong answer handling |
| `test_review_with_confidence` | Confidence levels |
| `test_list_mcqs` | List all |
| `test_update_mcq` | Update flow |
| `test_delete_mcq` | Delete flow |
| `test_get_stats` | Statistics |

#### 2.11 Export/Import Controllers (`src/controllers/export_import.py`) - ~12 tests

| Test Case | Description |
|-----------|-------------|
| `test_export_all` | Export all data |
| `test_export_questions_only` | Filter by type |
| `test_export_challenges_only` | Filter by type |
| `test_export_mcqs_only` | Filter by type |
| `test_export_by_tags` | Filter by tags |
| `test_export_empty` | No data to export |
| `test_import_questions` | Import questions |
| `test_import_challenges` | Import challenges |
| `test_import_mcqs` | Import MCQs |
| `test_import_skip_duplicates` | Duplicate handling |
| `test_import_invalid_json` | Error handling |
| `test_import_schema_validation` | Validation errors |

---

### Phase 4: Utils (Medium Priority)

#### 2.12 JSON Schema Utils (`src/utils/json_schema.py`) - ~10 tests

| Test Case | Description |
|-----------|-------------|
| `test_export_schema_valid` | Valid schema creation |
| `test_serialize_question` | Question serialization |
| `test_serialize_challenge` | Challenge serialization |
| `test_serialize_mcq` | MCQ serialization |
| `test_serialize_with_none_values` | Handle None fields |
| `test_deserialize_question` | Question deserialization |
| `test_deserialize_challenge` | Challenge deserialization |
| `test_deserialize_mcq` | MCQ deserialization |
| `test_validate_import_data` | Import validation |
| `test_invalid_import_data` | Invalid data handling |

---

### Phase 5: Views (Lower Priority - UI Layer)

**Strategy:** Mock questionary and rich console.

#### 2.13 QuestionView (`src/views/question.py`) - ~8 tests

| Test Case | Description |
|-----------|-------------|
| `test_prompt_question_text` | Text input prompt |
| `test_prompt_tags` | Tags input |
| `test_display_question` | Question display |
| `test_display_stats` | Stats display |
| `test_prompt_rating` | Rating selection |
| `test_select_question` | Question selection |
| `test_confirm_delete` | Delete confirmation |
| `test_display_success` | Success message |

#### 2.14 ChallengeView (`src/views/challenge.py`) - ~8 tests

| Test Case | Description |
|-----------|-------------|
| `test_prompt_title` | Title input |
| `test_prompt_description` | Description input |
| `test_prompt_language` | Language selection |
| `test_display_challenge` | Challenge display |
| `test_workspace_setup` | Workspace creation |
| `test_workspace_cleanup` | Workspace deletion |
| `test_select_challenge` | Challenge selection |
| `test_display_stats` | Stats display |

#### 2.15 MCQView (`src/views/mcq.py`) - ~8 tests

| Test Case | Description |
|-----------|-------------|
| `test_prompt_question` | Question input |
| `test_prompt_options` | Options input |
| `test_prompt_answer` | Answer selection |
| `test_display_mcq` | MCQ display |
| `test_display_with_randomization` | Option shuffling |
| `test_prompt_confidence` | Confidence level |
| `test_display_feedback` | Answer feedback |
| `test_select_mcq` | MCQ selection |

---

### Phase 6: CLI Integration (Lower Priority)

#### 2.16 CLI Commands (`cli.py`) - ~15 tests

| Test Case | Description |
|-----------|-------------|
| `test_add_command_question` | Add question command |
| `test_add_command_challenge` | Add challenge command |
| `test_add_command_mcq` | Add MCQ command |
| `test_review_command_all` | Review all types |
| `test_review_command_filtered` | Review with filters |
| `test_list_command` | List command |
| `test_update_command` | Update command |
| `test_delete_command` | Delete command |
| `test_stats_command` | Stats command |
| `test_quick_review_command` | Quick review |
| `test_health_check_command` | Health check |
| `test_export_command` | Export command |
| `test_import_command` | Import command |
| `test_add_testcases_command` | Add testcases |
| `test_invalid_command_args` | Error handling |

---

## 3. Implementation Order

Execute in this sequence for maximum value with minimal dependencies:

```
Week 1: Foundation
├── 1. Setup test infrastructure (conftest.py, pytest config)
├── 2. test_sm2.py (20 tests) - Pure logic, no dependencies
├── 3. test_question.py (8 tests) - Model validation
├── 4. test_challenge.py (10 tests) - Model validation
└── 5. test_mcq.py (15 tests) - Model validation

Week 2: Data Layer
├── 6. test_question_repository.py (20 tests)
├── 7. test_challenge_repository.py (22 tests)
└── 8. test_mcq_repository.py (20 tests)

Week 3: Business Logic
├── 9. test_question_controller.py (12 tests)
├── 10. test_challenge_controller.py (14 tests)
├── 11. test_mcq_controller.py (12 tests)
└── 12. test_export_import_controller.py (12 tests)

Week 4: UI & Integration
├── 13. test_json_schema.py (10 tests)
├── 14. test_*_view.py (24 tests total)
└── 15. test_cli.py (15 tests)
```

---

## 4. Running Tests

### Run All Tests with Coverage
```bash
poetry run pytest
```

### Run Specific Test File
```bash
poetry run pytest tests/unit/models/test_sm2.py -v
```

### Run with Verbose Coverage
```bash
poetry run pytest --cov=src --cov-report=html --cov-report=term-missing
```

### View HTML Coverage Report
```bash
open htmlcov/index.html
```

---

## 5. Coverage Targets by Module

| Module | Target | Rationale |
|--------|--------|-----------|
| `src/models/sm2.py` | 100% | Core algorithm, critical |
| `src/models/*.py` | 95% | Validation logic |
| `src/repositories/*.py` | 90% | Data operations |
| `src/controllers/*.py` | 85% | Orchestration |
| `src/views/*.py` | 75% | UI (harder to test) |
| `src/utils/*.py` | 90% | Utility functions |
| `cli.py` | 80% | Entry point |
| **Overall** | **>85%** | Project goal |

---

## 6. Key Fixtures Summary

```python
# conftest.py

@pytest.fixture
def test_db():
    """In-memory SQLite database."""

@pytest.fixture
def db_manager(test_db):
    """DatabaseManager instance."""

@pytest.fixture
def question_repo(db_manager):
    """QuestionRepository with test DB."""

@pytest.fixture
def challenge_repo(db_manager):
    """ChallengeRepository with test DB."""

@pytest.fixture
def mcq_repo(db_manager):
    """MCQRepository with test DB."""

@pytest.fixture
def sample_question():
    """Sample Question model."""

@pytest.fixture
def sample_challenge():
    """Sample Challenge model."""

@pytest.fixture
def sample_mcq():
    """Sample MCQQuestion model."""

@pytest.fixture
def mock_view(mocker):
    """Mocked view for controller tests."""

@pytest.fixture
def mock_console(mocker):
    """Mocked rich console."""
```

---

## 7. Notes

### Testing Best Practices
- Each test should be independent and isolated
- Use descriptive test names that explain the scenario
- Follow AAA pattern: Arrange, Act, Assert
- Keep tests fast (mock I/O and external dependencies)
- Test edge cases and error conditions

### What NOT to Test
- Third-party library internals (questionary, rich, typer)
- Python built-in functionality
- Simple getters/setters with no logic

### Continuous Integration
Consider adding GitHub Actions workflow:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - run: pip install poetry
      - run: poetry install
      - run: poetry run pytest --cov-fail-under=85
```
