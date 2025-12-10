# desktop/styles.py

DARK_THEME = """
QMainWindow {
    background-color: #1e1e1e;
}

QLabel {
    color: #e0e0e0;
    font-size: 14px;
    font-family: 'Segoe UI', sans-serif;
}

QLineEdit, QTextEdit {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #3e3e3e;
    border-radius: 5px;
    padding: 8px;
    font-size: 14px;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #4a90e2;
}

QPushButton {
    background-color: #4a90e2;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #357abd;
}

QPushButton:pressed {
    background-color: #2a629c;
}

QProgressBar {
    border: 1px solid #3e3e3e;
    border-radius: 5px;
    text-align: center;
    color: white;
}

QProgressBar::chunk {
    background-color: #4a90e2;
    width: 20px;
}
"""