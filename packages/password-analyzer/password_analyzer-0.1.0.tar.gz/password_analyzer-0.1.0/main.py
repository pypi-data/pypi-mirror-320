from getpass import getpass

from password_analyzer.password_analyzer import PasswordAnalyzer


def main():
    password = getpass("Your password: ")
    password_analyzer = PasswordAnalyzer(password=password)

    print(password_analyzer.get_password_review())
    print(password_analyzer.suggest_improvements())


if __name__ == "__main__":
    main()
