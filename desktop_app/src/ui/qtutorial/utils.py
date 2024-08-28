from PySide6.QtCore import QFile, QIODevice, QTextStream


def load_stylesheet(stylesheet_name: str) -> str:
    file = QFile(stylesheet_name)
    if not file.open(QIODevice.ReadOnly | QIODevice.Text):
        return ""

    stream = QTextStream(file)
    stylesheet = stream.readAll()
    file.close()
    return stylesheet
