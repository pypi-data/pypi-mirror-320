# Password Analyzer

## Overview

**Password Analyzer** is a Python library designed to evaluate the strength of passwords, validate them against a set of customizable rules, and provide actionable feedback to improve password security.

Key features include:
- Validating password length and complexity.
- Checking for weak and prohibited patterns.
- Scoring passwords based on configurable character weights.
- Suggesting improvements for weak passwords.
- Customizable analyzer options.

---

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
  - [Password Strength Review](#password-strength-review)
  - [Password Suggestions](#password-suggestions)
- [Customization](#customization)
- [License](#license)

---

## Installation

> [!NOTE]
> I'm planning to publish **Password Strength Analyzer** on **PyPI**

Clone the repository:
```bash
$ git clone https://github.com/password-strength-analyzer.git .
```

Install dependencies:
```bash
$ pip install -r requirements.txt
```

---

## Usage

### Basic Example
```python
from getpass import getpass

from password_analyzer.password_analyzer import PasswordAnalyzer
password = getpass("Password: ")

password_analyzer = PasswordAnalyzer(password=password)

print(password_analyzer.get_password_review())
```

---

## Features

### Password Strength Review
Generate a detailed review of the password's compliance with configured thresholds:
```python
review = analyzer.get_password_review()
print(review)
```
**Example Output:**
```plaintext
Password: My_Very_Secure@Pssw0rd reaches the 0 threshold and is Good
```

### Password Suggestions
Provide actionable feedback to improve password strength:
```python
suggested_improvements = analyzer.suggest_improvements()
print(suggested_improvements)
```
**Example Output:**
```plaintext
- Increase your password length to be minimum 8 characters long.
- Your password isn't as good as it can be. Strengthen it using special characters like !, $, etc.
```

---

## Customization

### Analyzer Options
Adjust rules for password validation using the `AnalyzerOptions` class:

```python
from password_analyzer.analyzer_options import AnalyzerOptions
from password_analyzer.analyzer import PasswordAnalyzer

options = AnalyzerOptions(
    required_length=12,
    maximum_length=64,
    score_threshold=15,
    prohibited_characters=["!", "#"],
    weak_passwords=["password", "123456"]
)

password = "P@ssw0rd"
analyzer = PasswordAnalyzer(password=password, options=options)
```

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

