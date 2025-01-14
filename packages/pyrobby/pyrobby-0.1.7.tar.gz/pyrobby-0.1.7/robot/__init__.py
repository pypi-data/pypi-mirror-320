from .robot import RobotApp
import tkinter as tk

def start():
    """
    Запускает приложение робота.
    Простой способ начать работу с библиотекой.
    
    Пример использования:
    >>> from robot import start
    >>> start()
    """
    root = tk.Tk()
    app = RobotApp(root)
    root.mainloop()

# Экспортируем также основные классы для продвинутого использования
__all__ = ['RobotApp', 'start'] 