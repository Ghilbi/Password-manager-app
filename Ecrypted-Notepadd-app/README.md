# Secure Password Manager

A modern encrypted notepad application to securely store your passwords and sensitive information.

## Features

- Strong AES encryption for your password data
- Modern UI with smooth animations
- Password visibility toggle
- Create and manage multiple password entries
- Securely store usernames, passwords and additional notes

## Requirements

- Python 3.6 or higher
- PyQt6
- cryptography

## Installation

1. Clone this repository or download the source code
2. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

1. Run the application:

```
python main.py
```

2. Create a new password file by entering a master password
3. Add password entries by clicking the "Add" button
4. View, edit or delete entries as needed
5. Use the "Lock" button to secure your passwords when you're done

## Security Notes

- Your password file is encrypted using AES encryption
- The master password is never stored in the application
- Always remember your master password as it cannot be recovered

## License

This project is open source and available under the MIT License. 