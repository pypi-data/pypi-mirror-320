import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import time
from PIL import Image, ImageTk
import sys
import io
import threading
import json  # Импортируем библиотеку для работы с JSON
import re  # Импортируем библиотеку для работы с регулярными выражениями
from . import tasks  # Импортируем файл с заданиями из текущего пакета
import queue  # Импортируем модуль queue для очереди
import os

# В начале файла добавьте:
import os

# Определите путь к директории с иконками
ICONS_DIR = os.path.join(os.path.dirname(__file__), 'icons')

class ToolTip:
    """Класс для создания подсказок для виджетов."""
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        """Показать подсказку."""
        if self.tip_window or not self.text:
            return
        x, y, _cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        """Скрыть подсказку."""
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

class Robot:
    """Класс, представляющий робота на игровом поле."""
    
    def __init__(self, canvas, x, y, cell_size, offset, app):
        """Инициализация робота."""
        self.canvas = canvas
        self.x = x
        self.y = y
        self.pos_x = x
        self.pos_y = y
        self.cell_size = cell_size
        self.offset = offset
        self.app = app
        self.grid_size_n = app.grid_size_n
        self.grid_size_m = app.grid_size_m
        self.is_moving = False
        self.direction = 0
        
        # Добавляем словарь для кэширования изображений
        self.cached_images = {}
        
        # Загружаем изображение робота
        try:
            self.original_image = Image.open(os.path.join(ICONS_DIR, 'robot.png'))
            # Создаем и сохраняем PhotoImage
            self.photo_image = self.create_scaled_image(cell_size)
            # Создаем изображение на холсте
            self.robot = self.canvas.create_image(
                self._calculate_screen_x(),
                self._calculate_screen_y(),
                image=self.photo_image,
                tags="robot"
            )
            # Явно поднимаем робота над другими элементами
            self.canvas.tag_raise(self.robot)
        except Exception as e:
            print(f"Error loading robot image: {e}")
            # Создаем круг вместо изображения
            size = cell_size * 0.8
            x = self._calculate_screen_x()
            y = self._calculate_screen_y()
            self.robot = self.canvas.create_oval(
                x - size/2, y - size/2,
                x + size/2, y + size/2,
                fill="blue",
                tags="robot"
            )
            # Явно поднимаем робота над другими элементами
            self.canvas.tag_raise(self.robot)

    def create_scaled_image(self, cell_size):
        """Создание масштабированного изображения робота."""
        try:
            target_size = int(cell_size * 0.8)
            
            if not hasattr(self, 'original_image'):
                robot_path = os.path.join(ICONS_DIR, 'robot.png')  # Используем правильный путь
                self.original_image = Image.open(robot_path)
                
            orig_width, orig_height = self.original_image.size
            scale = min(target_size / orig_width, target_size / orig_height)
            new_width = int(orig_width * scale)
            new_height = int(orig_height * scale)
            
            if new_width <= 0 or new_height <= 0:
                raise ValueError(f"Invalid scaled dimensions: {new_width}x{new_height}")
            
            scaled_image = self.original_image.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS
            )
            
            photo = ImageTk.PhotoImage(scaled_image)
            self._current_photo = photo
            return photo
            
        except Exception as e:
            print(f"Error in create_scaled_image: {str(e)}")
            return None

    def _calculate_screen_x(self):
        """Вычисление экранной координаты X."""
        return self.x * self.cell_size + self.offset + self.cell_size / 2

    def _calculate_screen_y(self):
        """Вычисление экранной координаты Y."""
        return self.y * self.cell_size + self.offset + self.cell_size / 2

    def get_cached_image(self, angle, cell_size):
        """Получение кэшированного изображения с заданным углом и размером."""
        try:
            key = (angle, cell_size)
            
            if key in self.cached_images:
                return self.cached_images[key]
            
            if not hasattr(self, 'original_image'):
                robot_path = os.path.join(ICONS_DIR, 'robot.png')  # Используем правильный путь
                self.original_image = Image.open(robot_path)
                
            target_size = int(cell_size * 0.8)
            orig_width, orig_height = self.original_image.size
            scale = min(target_size / orig_width, target_size / orig_height)
            new_width = int(orig_width * scale)
            new_height = int(orig_height * scale)
            
            if new_width <= 0 or new_height <= 0:
                raise ValueError(f"Invalid scaled dimensions: {new_width}x{new_height}")
            
            scaled_image = self.original_image.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS
            )
            
            if angle != 0:
                scaled_image = scaled_image.rotate(-angle, expand=True)
            
            photo = ImageTk.PhotoImage(scaled_image)
            self.cached_images[key] = photo
            return photo
            
        except Exception as e:
            print(f"Error in get_cached_image: {str(e)}")
            return None

    def update_image(self, cell_size):
        """Обновление изображения робота."""
        self.cell_size = cell_size
        try:
            # Создаем новое масштабированное изображение
            robot_path = os.path.join(ICONS_DIR, 'robot.png')  # Используем правильный путь
            self.original_image = Image.open(robot_path)
            self.photo_image = self.create_scaled_image(cell_size)
            # Обновляем изображение на холсте
            self.canvas.itemconfig(self.robot, image=self.photo_image)
            # Обновляем позицию
            self.canvas.coords(
                self.robot,
                self._calculate_screen_x(),
                self._calculate_screen_y()
            )
            # Поднимаем робота над другими элементами
            self.canvas.tag_raise(self.robot)
        except Exception as e:
            print(f"Error updating robot image: {e}")
            # Если не удалось обновить изображение, создаем круг
            size = cell_size * 0.8
            x = self._calculate_screen_x()
            y = self._calculate_screen_y()
            self.canvas.delete(self.robot)
            self.robot = self.canvas.create_oval(
                x - size/2, y - size/2,
                x + size/2, y + size/2,
                fill="blue",
                tags="robot"
            )
            # Поднимаем робота над другими элементами
            self.canvas.tag_raise(self.robot)

    def rotate_image(self, angle):
        """Поворот изображения робота."""
        self.current_image = self.get_cached_image(angle, self.cell_size)  # Сохраняем ссылку
        try:
            self.canvas.itemconfig(self.robot, image=self.current_image)
            self.canvas.tag_raise(self.robot)  # Поднимаем робота над остальными элементами
        except tk.TclError:
            # Если изображение потеряно, создаем новое
            self.robot = self.canvas.create_image(
                self._calculate_screen_x(),
                self._calculate_screen_y(),
                image=self.current_image
            )
            self.canvas.tag_raise(self.robot)  # Поднимаем робота над остальными элементами

    def move(self, dx, dy, angle):
        """Перемещение робота."""
        if self.is_moving:
            return
            
        new_x = self.x + dx
        new_y = self.y + dy

        if not self._is_valid_move(new_x, new_y, angle):
            return

        self.rotate_image(angle)
        self.is_moving = True
        self._animate_movement(dx, dy, 0)
        
        # Ждем завершения анимации
        while self.is_moving:
            try:
                self.canvas.update()
                # Проверяем, что изображение все еще существует
                self.canvas.itemcget(self.robot, 'image')
                time.sleep(0.01)
            except tk.TclError:
                # Если изображение потеряно, восстанавливаем его
                self.update_image(self.cell_size)
                self.canvas.coords(
                    self.robot,
                    self._calculate_screen_x(),
                    self._calculate_screen_y()
                )

    def _animate_movement(self, dx, dy, step):
        """Анимация движения робота."""
        if not self.is_moving:
            return
            
        try:
            if step >= 20:  # Всего 20 шагов анимации
                self.x += dx
                self.y += dy
                self.pos_x = self.x
                self.pos_y = self.y
                self.canvas.coords(
                    self.robot,
                    self._calculate_screen_x(),
                    self._calculate_screen_y()
                )
                self.is_moving = False
                return
            
            steps = 20
            dx_step = dx * self.cell_size / steps
            dy_step = dy * self.cell_size / steps
            
            self.canvas.coords(
                self.robot,
                self._calculate_screen_x() + dx_step * step,
                self._calculate_screen_y() + dy_step * step
            )
            
            # Проверяем, что изображение существует
            self.canvas.itemcget(self.robot, 'image')
            
            delay = int(self.app.sleep_time * 1000 / steps)
            self.canvas.tag_raise(self.robot)
            self.canvas.after(max(1, delay), lambda: self._animate_movement(dx, dy, step + 1))
            
        except tk.TclError:
            # Если изображение потеряно, восстанавливаем его
            self.update_image(self.cell_size)
            self._animate_movement(dx, dy, step)

    def _is_valid_move(self, new_x, new_y, angle):
        """Проверка возможности движения."""
        if not (0 <= new_x < self.grid_size_n and 0 <= new_y < self.grid_size_m):
            self._show_error("Вы врезались в стену")
            self.app.running = False  # Останавливаем выполнение программы
            raise Exception("Выполнение остановлено: выход за пределы поля")

        if self._check_wall_collision(new_x, new_y, angle):
            return False

        return True

    def _check_wall_collision(self, new_x, new_y, angle):
        """Проверка столкновения со стенами."""
        current_pos = self.pos()
        new_pos = new_y * self.grid_size_n + new_x + 1

        wall_checks = {
            -90: ('left', 'right'),
            90: ('right', 'left'),
            0: ('up', 'down'),
            180: ('down', 'up')
        }

        if angle in wall_checks:
            current_wall, target_wall = wall_checks[angle]
            if (current_pos in self.app.wall[current_wall] or 
                new_pos in self.app.wall[target_wall]):
                self._show_error("Вы врезались в стену")
                self.app.running = False  # Останавливаем выполнение программы
                raise Exception("Выполнение остановлено: столкновение со стеной")

        return False

    def _show_error(self, message):
        """Отображение сообщения об ошибке."""
        messagebox.showerror("Ошибка", message)

    def left(self):
        """Движение влево."""
        if not self.app.running:
            return
        if self.is_moving:
            return
        try:
            current_pos = self.pos()
            if self.pos_x > 0 and current_pos not in self.app.wall['left']:
                self.move(-1, 0, -90)  # Используем метод move вместо прямого изменения координат
            else:
                self._show_error("Робот врезался в стену")
                self.app.running = False  # Останавливаем выполнение программы
                raise Exception("Робот врезался в стену")
        except Exception:
            pass

    def right(self):
        """Движение вправо."""
        if not self.app.running:
            return
        if self.is_moving:
            return
        try:
            current_pos = self.pos()
            if self.pos_x < self.grid_size_n - 1 and current_pos not in self.app.wall['right']:
                self.move(1, 0, 90)  # Используем метод move вместо прямого изменения координат
            else:
                self._show_error("Робот врезался в стену")
                self.app.running = False  # Останавливаем выполнение программы
                raise Exception("Робот врезался в стену")
        except Exception:
            pass

    def up(self):
        """Движение вверх."""
        if not self.app.running:
            return
        if self.is_moving:
            return
        try:
            current_pos = self.pos()
            if self.pos_y > 0 and current_pos not in self.app.wall['up']:
                self.move(0, -1, 0)  # Используем метод move вместо прямого изменения координат
            else:
                self._show_error("Робот врезался в стену")
                self.app.running = False  # Останавливаем выполнение программы
                raise Exception("Робот врезался в стену")
        except Exception:
            pass

    def down(self):
        """Движение вниз."""
        if not self.app.running:
            return
        if self.is_moving:
            return
        try:
            current_pos = self.pos()
            if self.pos_y < self.grid_size_m - 1 and current_pos not in self.app.wall['down']:
                self.move(0, 1, 180)  # Используем метод move вместо прямого изменения координат
            else:
                self._show_error("Робот врезался в стену")
                self.app.running = False  # Останавливаем выполнение программы
                raise Exception("Робот врезался в стену")
        except Exception:
            pass

    def reset_position(self):
        """Возвращает робота в начальную позицию."""
        # Сохраняем начальную позицию при первой установке
        if not hasattr(self, 'start_x'):
            self.start_x = self.x
            self.start_y = self.y
        
        # Возвращаем робота в начальную позицию
        self.x = self.start_x
        self.y = self.start_y
        self.pos_x = self.start_x
        self.pos_y = self.start_y
        
        # Обновляем положение робота на canvas
        x = self._calculate_screen_x()
        y = self._calculate_screen_y()
        self.canvas.coords(self.robot, x, y)
        
        # Сбрасываем поворот
        self.direction = 0
        self.rotate_image(0)
        
        # Поднимаем робота над другими элементами
        self.canvas.tag_raise(self.robot)

    def fillcell(self):
        """Закрашивание текущей клетки."""
        self.app.filled_cells.append(self.pos())
        self.canvas.create_rectangle(
            self.x * self.cell_size + self.offset,
            self.y * self.cell_size + self.offset,
            (self.x + 1) * self.cell_size + self.offset,
            (self.y + 1) * self.cell_size + self.offset,
            fill="green",
            outline="black"
        )
        self.canvas.tag_raise(self.robot)

    def update_position(self, x, y):
        """Обновление позиции робота."""
        self.x = x
        self.y = y
        self.canvas.coords(
            self.robot,
            self._calculate_screen_x(),
            self._calculate_screen_y()
        )

    def pos(self):
        """Возвращает номер текущей ячейки."""
        return self.pos_y * self.grid_size_n + self.pos_x + 1

    def goto(self, X, Y=None):
        """Перемещение робота в указанную клетку.
    
        Args:
            X: Если Y=None, то X - номер ячейки.
                Если Y указан, то X - номер строки (от 1).
            Y: Номер столбца (от 1). Если не указан, используется X как номер ячейки.
        """
        try:
            if Y is not None:  # Если переданы два аргумента (строка, столбец)
                # Преобразуем координаты в номер ячейки
                # Вычитаем 1, так как нумерация с 1, а индексы с 0
                row = X - 1
                col = Y - 1
                if 0 <= row < self.grid_size_m and 0 <= col < self.grid_size_n:
                    self.x = col
                    self.y = row
                    self.canvas.coords(
                        self.robot,
                        self._calculate_screen_x(),
                        self._calculate_screen_y()
                    )
                else:
                    self._show_error("Недопустимые координаты")
            else:  # Если передан один аргумент (номер ячейки)
                new_y = (X - 1) // self.grid_size_n
                new_x = (X - 1) % self.grid_size_n
                if 0 <= new_x < self.grid_size_n and 0 <= new_y < self.grid_size_m:
                    self.x = new_x
                    self.y = new_y
                    self.canvas.coords(
                        self.robot,
                        self._calculate_screen_x(),
                        self._calculate_screen_y()
                    )
                else:
                    self._show_error("Недопустимая ячейка")
        except Exception as e:
            self._show_error(f"Ошибка при перемещении: {str(e)}")

    def start_pos(self, *args):
        """
        Устанавливает начальную позицию робота.
        Можно передать либо номер ячейки x, либо координаты (m, n).
        """
        try:
            if len(args) == 1:
                # Если передан один аргумент - это номер ячейки
                x = args[0]
                if not (1 <= x <= self.grid_size_m * self.grid_size_n):
                    raise ValueError(f"Invalid cell number: {x}")
                new_y = (x - 1) // self.grid_size_n
                new_x = (x - 1) % self.grid_size_n
            elif len(args) == 2:
                # Если переданы два аргумента - это координаты m, n
                m, n = args
                if not (1 <= m <= self.grid_size_m and 1 <= n <= self.grid_size_n):
                    raise ValueError(f"Invalid coordinates: m={m}, n={n}")
                new_y = m - 1
                new_x = n - 1
            else:
                raise ValueError("Invalid number of arguments")

            self.pos_x = new_x
            self.pos_y = new_y
            self.x = self.pos_x
            self.y = self.pos_y
            self.canvas.coords(
                self.robot,
                self._calculate_screen_x(),
                self._calculate_screen_y()
            )
            
        except Exception as e:
            self._show_error("Недопустимая ячейка")

    def cellispainted(self):
        """Проверка, закрашена ли текущая клетка."""
        return self.pos() in self.app.filled_cells
    
    def cellisfree(self):
        """Проверка, закрашена ли текущая клетка."""
        return not self.pos() in self.app.filled_cells

    def end_position(self):
        """Проверка, находится ли робот в конечной позиции."""
        return self.pos() == self.app.end_position

class RobotApp:

    def __init__(self, root):
        self.root = root
        self.running = False
        self.program_running = False
        self.sleep_time = 0.5  # Добавляем атрибут sleep_time с значением по умолчанию
        
        # Создаем основное окно
        self.root.title("Robot Control")
        self.root.geometry("800x700")
        self.drag_data = None  # Initialize drag_data
        self.selected_task = None  # Variable to store the selected task
        self.task_input = None  # Variable to store the input value
        self.saved_environment = {}  # Initialize saved_environment

        # Инициализация структуры задачника
        self.task = {
            'algo': [tasks.algo_task_1, tasks.algo_task_2, tasks.algo_task_3, tasks.algo_task_4, 
                     tasks.algo_task_5, tasks.algo_task_6, tasks.algo_task_7, tasks.algo_task_8, 
                     tasks.algo_task_9, tasks.algo_task_10],
            'for': [tasks.for_task_1, tasks.for_task_2, tasks.for_task_3, tasks.for_task_4,
                    tasks.for_task_5, tasks.for_task_6, tasks.for_task_7, tasks.for_task_8,
                    tasks.for_task_9, tasks.for_task_10],
            'if': [tasks.if_task_1, tasks.if_task_2, tasks.if_task_3, tasks.if_task_4,
                   tasks.if_task_5, tasks.if_task_6, tasks.if_task_7, tasks.if_task_8,
                   tasks.if_task_9, tasks.if_task_10],
            'cif': [tasks.cif_task_1, tasks.cif_task_2, tasks.cif_task_3, tasks.cif_task_4,
                    tasks.cif_task_5, tasks.cif_task_6, tasks.cif_task_7, tasks.cif_task_8,
                    tasks.cif_task_9, tasks.cif_task_10],
            'while': [tasks.while_task_1, tasks.while_task_2, tasks.while_task_3, tasks.while_task_4,
                      tasks.while_task_5, tasks.while_task_6, tasks.while_task_7, tasks.while_task_8,
                      tasks.while_task_9, tasks.while_task_10]
        }

        # Toolbar
        self.toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # В методе __init__ класса RobotApp, заменяем создание кнопки new_tab_button:
        try:
            # Загружаем и масштабируем иконку для новой вкладки
            new_tab_icon = Image.open(os.path.join(ICONS_DIR, 'new_tab.png'))
            new_tab_icon = new_tab_icon.resize((25, 25), Image.Resampling.LANCZOS)  # Меняем на 25x25
            self.new_tab_photo = ImageTk.PhotoImage(new_tab_icon)
            
            # Создаем кнопку с иконкой
            self.new_tab_button = tk.Button(
                self.toolbar, 
                image=self.new_tab_photo,
                command=self.add_new_tab,
                width=30,
                height=30,
                bg="SystemButtonFace"
            )
            ToolTip(self.new_tab_button, "Создать новую вкладку")
        except Exception as e:
            # Если не удалось загрузить иконку, создаем кнопку с текстом
            print(f"Error loading new tab icon: {e}")
            self.new_tab_button = tk.Button(self.toolbar, text="Новая вкладка", command=self.add_new_tab)

        self.new_tab_button.pack(side=tk.LEFT, padx=2, pady=2)

        # В методе __init__ класса RobotApp, заменяем создание кнопки close_tab_button:
        try:
            # Загружаем и масштабируем иконку для закрытия вкладки
            close_tab_icon = Image.open(os.path.join(ICONS_DIR, 'close_tab.png'))
            close_tab_icon = close_tab_icon.resize((25, 25), Image.Resampling.LANCZOS)  # Меняем на 25x25
            self.close_tab_photo = ImageTk.PhotoImage(close_tab_icon)
            
            # Создаем кнопку с иконкой
            self.close_tab_button = tk.Button(
                self.toolbar, 
                image=self.close_tab_photo,
                command=self.close_current_tab,
                width=30,
                height=30,
                bg="SystemButtonFace"
            )
            ToolTip(self.close_tab_button, "Закрыть текущую вкладку")
        except Exception as e:
            # Если не удалось загрузить иконку, создаем кнопку с текстом
            print(f"Error loading close tab icon: {e}")
            self.close_tab_button = tk.Button(self.toolbar, text="Закрыть вкладку", command=self.close_current_tab)

        self.close_tab_button.pack(side=tk.LEFT, padx=2, pady=2)

        # В методе __init__ класса RobotApp, заменяем создание кнопки save_button:
        try:
            # Загружаем и масштабируем иконку для сохранения
            save_icon = Image.open(os.path.join(ICONS_DIR, 'save.png'))
            save_icon = save_icon.resize((25, 25), Image.Resampling.LANCZOS)  # Меняем на 25x25
            self.save_photo = ImageTk.PhotoImage(save_icon)
            
            # Создаем кнопку с иконкой
            self.save_button = tk.Button(
                self.toolbar, 
                image=self.save_photo,
                command=self.save_file,
                width=30,
                height=30,
                bg="SystemButtonFace"
            )
            ToolTip(self.save_button, "Сохранить файл")
        except Exception as e:
            # Если не удалось загрузить иконку, создаем кнопку с текстом
            print(f"Error loading save icon: {e}")
            self.save_button = tk.Button(self.toolbar, text="Сохранить", command=self.save_file)

        self.save_button.pack(side=tk.LEFT, padx=2, pady=2)

        try:
            # Загружаем и масштабируем иконку для открытия файла
            open_icon = Image.open(os.path.join(ICONS_DIR, 'open.png'))
            open_icon = open_icon.resize((25, 25), Image.Resampling.LANCZOS)  # Меняем на 25x25
            self.open_photo = ImageTk.PhotoImage(open_icon)
            
            # Создаем кнопку с иконкой
            self.open_button = tk.Button(
                self.toolbar, 
                image=self.open_photo,
                command=self.open_file,
                width=30,
                height=30,
                bg="SystemButtonFace"
            )
            ToolTip(self.open_button, "Открыть файл")
        except Exception as e:
            # Если не удалось загрузить иконку, создаем кнопку с текстом
            print(f"Error loading open icon: {e}")
            self.open_button = tk.Button(self.toolbar, text="Открыть", command=self.open_file)

        self.open_button.pack(side=tk.LEFT, padx=2, pady=2)

        # В методе __init__ класса RobotApp, заменяем создание кнопки run_button:
        try:
            # Загружаем и масштабируем иконку для запуска
            start_icon = Image.open(os.path.join(ICONS_DIR, 'start.png'))
            start_icon = start_icon.resize((25, 25), Image.Resampling.LANCZOS)  # Меняем на 25x25
            self.start_photo = ImageTk.PhotoImage(start_icon)
            
            # Создаем кнопку с иконкой
            self.run_button = tk.Button(
                self.toolbar, 
                image=self.start_photo,
                command=self.run_code,
                width=30,
                height=30,
                bg="SystemButtonFace"
            )
            ToolTip(self.run_button, "Запустить код")
        except Exception as e:
            # Если не удалось загрузить иконку, возвращаемся к варианту с символом
            print(f"Error loading start icon: {e}")
            self.run_button = tk.Button(
                self.toolbar, 
                text="▶",
                command=self.run_code,
                bg="SystemButtonFace",
                fg="green",
                width=2,
                height=1,
                font=("Arial", 19),
                relief="flat",
                borderwidth=0
            )

        self.run_button.pack(side=tk.LEFT, padx=0, pady=0)

        # В методе __init__ класса RobotApp, заменяем создание кнопки stop_button:
        try:
            # Загружаем и масштабируем иконку для остановки
            stop_icon = Image.open(os.path.join(ICONS_DIR, 'end.png'))
            stop_icon = stop_icon.resize((25, 25), Image.Resampling.LANCZOS)  # Меняем на 25x25
            self.stop_photo = ImageTk.PhotoImage(stop_icon)
            
            # Создаем кнопку с иконкой
            self.stop_button = tk.Button(
                self.toolbar, 
                image=self.stop_photo,
                command=self.stop_code,
                width=30,
                height=30,
                bg="SystemButtonFace"
            )
            ToolTip(self.stop_button, "Остановить выполнение")
        except Exception as e:
            # Если не удалось загрузить иконку, возвращаемся к варианту с символом
            print(f"Error loading stop icon: {e}")
            self.stop_button = tk.Button(
                self.toolbar, 
                text="■",
                command=self.stop_code,
                bg="SystemButtonFace",
                fg="red",
                width=2,
                height=1,
                font=("Arial", 19),
                relief="flat",
                borderwidth=0
            )

        self.stop_button.pack(side=tk.LEFT, padx=0, pady=0)
         # Добавляем кнопку Отменить
        try:
            # Загружаем и масштабируем иконку
            return_icon = Image.open(os.path.join(ICONS_DIR, 'return.png'))
            return_icon = return_icon.resize((25, 25), Image.Resampling.LANCZOS)  # Меняем на 25x25
            self.return_photo = ImageTk.PhotoImage(return_icon)
            
            # Создаем кнопку с иконкой
            self.undo_button = tk.Button(
                self.toolbar, 
                image=self.return_photo,
                command=self.undo_last_action,
                width=30,
                height=30
            )
            ToolTip(self.undo_button, "Отменить последнее действие")
        except Exception as e:
            # Если не удалось загрузить иконку, создаем кнопку с текстом
            print(f"Error loading return icon: {e}")
            self.undo_button = tk.Button(self.toolbar, text="Отменить", command=self.undo_last_action)

        self.undo_button.pack(side=tk.LEFT, padx=2, pady=2)

        # Добавляем кнопку Восстановить
        try:
            # Загружаем и масштабируем иконку для восстановления
            restore_icon = Image.open(os.path.join(ICONS_DIR, 'restore.png'))
            restore_icon = restore_icon.resize((25, 25), Image.Resampling.LANCZOS)  # Меняем на 25x25
            self.restore_photo = ImageTk.PhotoImage(restore_icon)
            
            # Создаем кнопку с иконкой
            self.redo_button = tk.Button(
                self.toolbar, 
                image=self.restore_photo,
                command=self.redo_last_action,
                width=30,
                height=30
            )
            ToolTip(self.redo_button, "Повторить последнее действие")
        except Exception as e:
            # Если не удалось загрузить иконку, создаем кнопку с текстом
            print(f"Error loading restore icon: {e}")
            self.redo_button = tk.Button(self.toolbar, text="Восстановить", command=self.redo_last_action)

        self.redo_button.pack(side=tk.LEFT, padx=2, pady=2)

        # В методе __init__ класса RobotApp, заменяем создание кнопки reset_task_button:
        try:
            # Загружаем и масштабируем иконку для сброса задания
            reset_icon = Image.open(os.path.join(ICONS_DIR, 'reset.png'))
            reset_icon = reset_icon.resize((25, 25), Image.Resampling.LANCZOS)  # Меняем на 25x25
            self.reset_photo = ImageTk.PhotoImage(reset_icon)
            
            # Создаем кнопку с иконкой
            self.reset_task_button = tk.Button(
                self.toolbar, 
                image=self.reset_photo,
                command=self.reset_current_task,
                width=30,
                height=30,
                bg="SystemButtonFace"
            )
            ToolTip(self.reset_task_button, "Сбросить текущее задание")
        except Exception as e:
            # Если не удалось загрузить иконку, создаем кнопку с текстом
            print(f"Error loading reset icon: {e}")
            self.reset_task_button = tk.Button(self.toolbar, text="Сбросить задание", command=self.reset_current_task)

        self.reset_task_button.pack(side=tk.LEFT, padx=2, pady=2)

        # В методе __init__ класса RobotApp, заменяем создание кнопки remote_button:
        try:
            # Загружаем и масштабируем иконку для пульта управления
            remote_icon = Image.open(os.path.join(ICONS_DIR, 'remote-control.png'))
            remote_icon = remote_icon.resize((25, 25), Image.Resampling.LANCZOS)  # Меняем на 25x25
            self.remote_photo = ImageTk.PhotoImage(remote_icon)
            
            # Создаем кнопку с иконкой
            self.remote_button = tk.Button(
                self.toolbar, 
                image=self.remote_photo,
                command=self.open_remote_control,
                width=30,
                height=30,
                bg="SystemButtonFace"
            )
            ToolTip(self.remote_button, "Открыть пульт управления")
        except Exception as e:
            # Если не удалось загрузить иконку, создаем кнопку с текстом
            print(f"Error loading remote control icon: {e}")
            self.remote_button = tk.Button(self.toolbar, text="Пульт", command=self.open_remote_control)

        self.remote_button.pack(side=tk.LEFT, padx=2, pady=2)

       

        # Label to display the selected task
        self.selected_task_label = tk.Label(self.toolbar, text="Выбранное задание: None")
        self.selected_task_label.pack(side=tk.LEFT, padx=10, pady=2)

        # Create a menu bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Create a File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Файл", menu=self.file_menu)
        self.file_menu.add_command(label="Открыть", command=self.open_file)
        self.file_menu.add_command(label="Сохранить", command=self.save_file)

        # Create an Environment menu
        self.environment_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Окружение", menu=self.environment_menu)

        self.environment_menu.add_command(label="Сохранить", command=self.save_environment_to_file)
        self.environment_menu.add_command(label="Загрузить", command=self.load_environment_from_file)
        self.environment_menu.add_separator()  # Добавляем разделитель
        self.environment_menu.add_command(label="Изменить", command=self.open_environment_editor)

        # Create a Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Помощь", menu=self.help_menu)
        self.help_menu.add_command(label="СПРАВКА", command=self.show_help)

        # Create a Tasks menu
        self.tasks_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Задания", menu=self.tasks_menu)
        self.tasks_menu.add_command(label="algo", command=lambda: self.show_task_window("algo"))
        self.tasks_menu.add_command(label="for", command=lambda: self.show_task_window("for"))
        self.tasks_menu.add_command(label="if", command=lambda: self.show_task_window("if"))
        self.tasks_menu.add_command(label="cif", command=lambda: self.show_task_window("cif"))
        self.tasks_menu.add_command(label="while", command=lambda: self.show_task_window("while"))

        # Create a Font menu
        self.font_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Шрифт", menu=self.font_menu)
        self.font_menu.add_command(label="Выбрать размер шрифта", command=self.choose_font_size)

        # Main frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.text_container = tk.Frame(self.frame)
        self.text_container.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Notebook for code tabs
        self.notebook = ttk.Notebook(self.text_container, width=40, height=20)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.output_label = tk.Label(self.text_container, text="Output:")
        self.output_label.pack(anchor="w", pady=5)

        self.output_text = tk.Text(self.text_container, width=40, height=10, state=tk.DISABLED)
        self.output_text.pack(side=tk.BOTTOM, fill=tk.BOTH)

        # Create a container frame for canvas
        self.canvas_container = tk.Frame(self.frame)
        self.canvas_container.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Create canvas and scale
        self.canvas = tk.Canvas(self.canvas_container, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Создаем фрейм для скорости и статуса
        speed_frame = tk.Frame(self.canvas_container)
        speed_frame.grid(row=1, column=0, sticky="ew", pady=5)
        speed_frame.grid_columnconfigure(1, weight=1)  # Разрешаем второму столбцу растягиваться

        # Добавляем надпись "ЗАДАНИЕ"
        

        # Добавляем метку для отображения причин невыполнения задания
        self.task_message_label = tk.Label(speed_frame, text="", fg="red")
        self.task_message_label.grid(row=1, column=0, columnspan=3, pady=(0, 5))

        # Метка "Скорость:"
        tk.Label(speed_frame, text="Скорость:").grid(row=2, column=0, padx=(5,0))

        # Ползунок скорости
        self.speed_scale = ttk.Scale(speed_frame, from_=1, to=100, orient=tk.HORIZONTAL,
                                   command=self.update_speed)
        self.speed_scale.set(80)  # Изменено с 50 на 80
        self.speed_scale.grid(row=2, column=1, padx=5, sticky="ew")

        # Метка статуса (справа от ползунка)
        self.task_status_label = tk.Label(speed_frame, text="Статус: Задание не выбрано")
        self.task_status_label.grid(row=2, column=2, padx=5)

        # ... rest of initialization code ...

        # Configure grid weights
        self.canvas_container.grid_rowconfigure(0, weight=90)
        self.canvas_container.grid_rowconfigure(1, weight=10)
        self.canvas_container.grid_columnconfigure(0, weight=1)

        # Initialize robot and grid
        self.grid_size_m = 5
        self.grid_size_n = 5
        self.cell_size = 60
        self.offset = 20

        # Инициализация массива массивов wall
        self.wall = {
            'left': [],
            'right': [],
            'up': [],
            'down': []
        }

        # Инициализация массива filled_cells
        self.filled_cells = []

        self.cells_to_fill = []

        # Инициализация конечной позиции
        self.end_position = None
        self.end_position_marker = None

        # Initialize the robot before creating the grid
        self.robot = Robot(self.canvas, 0, 0, self.cell_size, self.offset, self)
        self.create_grid()

        # Add initial tab
        self.add_new_tab()

        # Bind the resize event to the on_resize function
        self.root.bind("<Configure>", self.on_resize)

        # Bind the F5 key to the run_code function
        self.root.bind("<F5>", lambda event: self.run_code())

        # Создаем список доступных функций
        self.available_functions = [
            'up()', 'down()', 'left()', 'right()', 'move()', 
            'fillcell()', 'pos()', 'goto()', 'start_pos()','field()',
            'wallfromleft()','wallfromright()','wallfromup()','wallfromdown()',
            'freefromleft()','freefromright()','freefromup()','freefromdown()',
            'cellispainted()','cellisfree()','add_wall()','mark_cell_to_fill()',
            'add_end_position()','task()'
        ]
        
        # Создаем окно подсказок
        self.suggestion_box = tk.Listbox(
            self.root,
            height=5,
            selectmode=tk.SINGLE,
            font=('Courier', 10)
        )
        
        # Привязываем обработчики событий для окна подсказок
        self.suggestion_box.bind('<Double-Button-1>', self.handle_suggestion_click)
        self.suggestion_box.bind('<Return>', self.insert_suggestion)
        self.suggestion_box.bind('<Motion>', self.handle_suggestion_hover)
        
        # Скрываем окно подсказок изначально
        self.suggestion_box.place_forget()

        # Добавляем глобальные привязки клавиш, независимые от раскладки
        self.setup_global_bindings()

        # Создаем контекстное меню для вкладок
        self.tab_context_menu = tk.Menu(self.root, tearoff=0)
        self.tab_context_menu.add_command(label="Закрыть", command=lambda: self.close_tab(self.right_clicked_tab))
        self.tab_context_menu.add_command(label="Закрыть все, кроме текущего", command=self.close_other_tabs)
        self.tab_context_menu.add_command(label="Сохранить", command=self.save_file, accelerator="CTRL+S")
        self.tab_context_menu.add_command(label="Сделать активным", command=lambda: self.notebook.select(self.right_clicked_tab))
        
        # Привязываем событие правого клика к вкладкам
        self.notebook.bind("<Button-3>", self.show_tab_context_menu)
        self.right_clicked_tab = None

        # Добавляем атрибуты для хранения информации о текущем задании
        self.current_task_type = None
        self.current_task_num = None

        # В методе __init__ класса RobotApp, добавляем создание кнопки open_button:
       

    def setup_global_bindings(self):
        """Настройка глобальных горячих клавиш."""
        # Отмена (Ctrl+Z)
        self.root.bind_all('<Control-z>', lambda e: self.undo_last_action())
        self.root.bind_all('<Control-Z>', lambda e: self.undo_last_action())
        
        # Восстановление (Ctrl+Shift+Z)
        self.root.bind_all('<Control-Shift-z>', lambda e: self.redo_last_action())
        self.root.bind_all('<Control-Shift-Z>', lambda e: self.redo_last_action())
        
        # Вставка (Ctrl+V)
        self.root.bind_all('<Control-v>', lambda e: self.paste_text())
        self.root.bind_all('<Control-V>', lambda e: self.paste_text())
        
        # Вырезать (Ctrl+X)
        self.root.bind_all('<Control-x>', lambda e: self.cut_text())
        self.root.bind_all('<Control-X>', lambda e: self.cut_text())
        
        # Выделить всё (Ctrl+A)
        self.root.bind_all('<Control-a>', lambda e: self.select_all())
        self.root.bind_all('<Control-A>', lambda e: self.select_all())
        
        # Сохранить (Ctrl+S)
        self.root.bind_all('<Control-s>', lambda e: self.save_file())
        self.root.bind_all('<Control-S>', lambda e: self.save_file())

    def paste_text(self, event=None):
        """Обработчик вставки текста."""
        try:
            text_widget = self.get_current_text_widget()
            if text_widget:
                text_widget.event_generate('<<Paste>>')
            return "break"
        except Exception as e:
            print(f"Error in paste_text: {str(e)}")

    def cut_text(self, event=None):
        """Обработчик вырезания текста."""
        try:
            text_widget = self.get_current_text_widget()
            if text_widget:
                text_widget.event_generate('<<Cut>>')
            return "break"
        except Exception as e:
            print(f"Error in cut_text: {str(e)}")

    def select_all(self, event=None):
        """Обработчик выделения всего текста."""
        try:
            text_widget = self.get_current_text_widget()
            if text_widget:
                text_widget.tag_add('sel', '1.0', 'end')
            return "break"
        except Exception as e:
            print(f"Error in select_all: {str(e)}")

    def add_wall(self, direction, *args):
        """
        Добавляет стену.
        direction: 'left', 'right', 'up', 'down'
        Можно передать либо номер ячейки x, либо координаты (m, n).
        """
        try:
            if len(args) == 1:
                # Если передан один аргумент - это номер ячейки
                x = args[0]
                if not (1 <= x <= self.grid_size_m * self.grid_size_n):
                    raise ValueError(f"Invalid cell number: {x}")
                cell = x
            elif len(args) == 2:
                # Если переданы два аргумента - это координаты m, n
                m, n = args
                if not (1 <= m <= self.grid_size_m and 1 <= n <= self.grid_size_n):
                    raise ValueError(f"Invalid coordinates: m={m}, n={n}")
                cell = (m - 1) * self.grid_size_n + n
            else:
                raise ValueError("Invalid number of arguments")

            if direction in self.wall:
                if cell not in self.wall[direction]:
                    self.wall[direction].append(cell)
                    self.draw_walls()
            else:
                raise ValueError(f"Invalid direction: {direction}")
                
        except Exception as e:
            print(f"Error in add_wall: {str(e)}")

    def clear_walls(self):
        self.wall = {
            'left': [],
            'right': [],
            'up': [],
            'down': []
        }
        self.draw_walls()

    def add_end_position(self, *args):
        """Добавляет маркер конечной позиции."""
        try:
            if len(args) == 1:
                x = args[0]
                if not (1 <= x <= self.grid_size_m * self.grid_size_n):
                    raise ValueError(f"Invalid cell number: {x}")
                self.end_position = x
            elif len(args) == 2:
                m, n = args
                if not (1 <= m <= self.grid_size_m and 1 <= n <= self.grid_size_n):
                    raise ValueError(f"Invalid coordinates: m={m}, n={n}")
                self.end_position = (m - 1) * self.grid_size_n + n
            else:
                raise ValueError("Invalid number of arguments")

            # Перерисовываем все маркеры в правильном порядке
            self.draw_cells_to_fill()  # Сначала маркеры для закраски
            self.draw_end_position_marker()  # Затем маркер конечной позиции
            self.canvas.tag_raise(self.robot.robot)  # Робот всегда сверху
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Недопустимая позиция: {str(e)}")
        # Показываем окно окружения при добавлении конечной позиции
        

    def draw_end_position_marker(self):
        """Отрисовка маркера конечной позиции."""
        if self.end_position is not None:
            x = (self.end_position - 1) % self.grid_size_n
            y = (self.end_position - 1) // self.grid_size_n
            marker_size = self.cell_size * 0.125  # Уменьшаем размер в 2 раза (было 0.25)
            
            # Вычисляем координаты для левого верхнего угла клетки
            marker_x = x * self.cell_size + self.offset + marker_size  # Добавляем небольшой отступ
            marker_y = y * self.cell_size + self.offset + marker_size  # Добавляем небольшой отступ
            
            # Рисуем черный квадрат для конечной позиции
            self.canvas.create_rectangle(
                marker_x, marker_y,
                marker_x + marker_size, marker_y + marker_size,
                fill="black", tags="marker"
            )

    def reset_field(self):
        self.clear_walls()
        self.clear_filled_cells()
        self.canvas.delete("cell_to_fill")
        self.filled_cells = []
        self.end_position = None
        self.robot.reset_position()
        self.create_grid()
        self.canvas.tag_raise(self.robot)

    def field(self, m, n):
        """Устанавливает размер поля m x n."""
        try:
            # Сохраняем новые размеры
            self.grid_size_m = m
            self.grid_size_n = n
            
            # Очищаем все стены и другие параметры
            self.wall = {
                'left': [],
                'right': [],
                'up': [],
                'down': []
            }
            self.filled_cells = []
            self.cells_to_fill = []
            self.end_position = None
            
            # Очищаем canvas
            for item in self.canvas.find_all():
                if item != self.robot.robot:
                    self.canvas.delete(item)
            
            # Пересчитываем размер ячейки
            container_width = self.canvas_container.winfo_width()
            container_height = self.canvas_container.winfo_height()
            available_width = container_width - (2 * self.offset) - 40
            available_height = container_height - (2 * self.offset) - 40 - 30
            
            if available_width > 0 and available_height > 0:
                self.cell_size = min(
                    available_width / n,
                    available_height / m
                )
                self.cell_size = max(20, self.cell_size)  # Минимальный размер 20 пикселей
            
            # Обновляем размер canvas
            total_width = (n * self.cell_size) + (2 * self.offset) + 40
            total_height = (m * self.cell_size) + (2 * self.offset) + 40
            self.canvas.configure(width=total_width, height=total_height)
            
            # Создаем базовую сетку с границами
            self.create_grid()
            
            # Обновляем размер и позицию робота
            self.robot.cell_size = self.cell_size
            self.robot.update_image(self.cell_size)
            self.canvas.coords(
                self.robot.robot,
                self.robot._calculate_screen_x(),
                self.robot._calculate_screen_y()
            )
            self.canvas.tag_raise(self.robot.robot)
            
            # Принудительно обновляем canvas
            self.canvas.update_idletasks()
            
        except Exception as e:
            print(f"Error in field: {str(e)}")

    def create_grid_dialog(self):
        def create_grid():
            try:
                m = int(m_entry.get())
                n = int(n_entry.get())
                if m > 0 and n > 0:
                    self.field(m, n)
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Grid dimensions must be positive integers.")
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please enter positive integers.")

        dialog = tk.Toplevel(self.root)
        dialog.title("Create Grid")

        tk.Label(dialog, text="Rows (m):").pack(padx=10, pady=5)
        m_entry = tk.Entry(dialog)
        m_entry.pack(padx=10, pady=5)

        tk.Label(dialog, text="Columns (n):").pack(padx=10, pady=5)
        n_entry = tk.Entry(dialog)
        n_entry.pack(padx=10, pady=5)

        create_button = tk.Button(dialog, text="Create", command=create_grid)
        create_button.pack(padx=10, pady=10)

    def on_resize(self, event):
        """Обработчик изменения размера окна."""
        try:
            # Проверяем, что событие пришло от главного окна
            if event.widget == self.root:
                # Добавляем небольшую задержку для стабилизации размеров
                self.root.after_cancel(self._resize_job) if hasattr(self, '_resize_job') else None
                self._resize_job = self.root.after(100, lambda: self._do_resize())
                
        except Exception as e:
            print(f"Error in on_resize: {str(e)}")

    def _do_resize(self):
        """Выполняет фактическое масштабирование."""
        try:
            # Получаем размеры контейнера canvas
            container_width = self.canvas_container.winfo_width()
            container_height = self.canvas_container.winfo_height()
            
            # Вычитаем отступы и место под элементы управления
            available_width = container_width - (2 * self.offset) - 40  # 40 для номеров строк/столбцов
            available_height = container_height - (2 * self.offset) - 40 - 30  # 30 для панели скорости
            
            # Проверяем корректность размеров
            if available_width <= 0 or available_height <= 0:
                return
                
            # Вычисляем оптимальный размер ячейки
            new_cell_size = min(
                available_width / self.grid_size_n,
                available_height / self.grid_size_m
            )
            
            # Устанавливаем минимальный размер ячейки
            new_cell_size = max(20, new_cell_size)  # Минимальный размер 20 пикселей
            
            # Если размер существенно изменился, обновляем
            if abs(new_cell_size - self.cell_size) > 1:
                self.cell_size = new_cell_size
                self.robot.cell_size = new_cell_size
                
                # Конфигурируем canvas под новый размер
                total_width = (self.grid_size_n * new_cell_size) + (2 * self.offset) + 40
                total_height = (self.grid_size_m * new_cell_size) + (2 * self.offset) + 40
                
                self.canvas.configure(width=total_width, height=total_height)
                
                # Перерисовываем все элементы
                self.redraw_field()
                
                # Обновляем и поднимаем робота
                self.robot.update_image(new_cell_size)
                self.canvas.tag_raise(self.robot.robot)
                
                # Принудительно обновляем canvas
                self.canvas.update_idletasks()
                
        except Exception as e:
            print(f"Error in _do_resize: {str(e)}")

    def redraw_field(self):
        """Полная перерисовка поля и всех элементов."""
        try:
            # Сохраняем текущие координаты робота
            robot_x = self.robot.x
            robot_y = self.robot.y
            
            # Удаляем робота с canvas временно
            self.canvas.delete(self.robot.robot)
            
            # Очищаем canvas от всех остальных элементов
            self.canvas.delete("all")
            
            # Вычисляем общие размеры сетки
            grid_width = self.grid_size_n * self.cell_size
            grid_height = self.grid_size_m * self.cell_size
            
            # Проверяем, что размеры сетки корректны
            if grid_width <= 0 or grid_height <= 0:
                raise ValueError(f"Invalid grid dimensions: {grid_width}x{grid_height}")
            
            # Рисуем все элементы в правильном порядке
            self.create_grid()  # Сначала сетка
            self.draw_walls()   # Затем стены
            
            # Перерисовываем закрашенные клетки
            for cell in self.filled_cells:
                x = (cell - 1) % self.grid_size_n
                y = (cell - 1) // self.grid_size_n
                self.canvas.create_rectangle(
                    x * self.cell_size + self.offset,
                    y * self.cell_size + self.offset,
                    (x + 1) * self.cell_size + self.offset,
                    (y + 1) * self.cell_size + self.offset,
                    fill="green",
                    outline="black"
                )
            
            # Перерисовываем клетки для закраски
            self.draw_cells_to_fill()
            
            # Перерисовываем маркер конечной позиции
            self.draw_end_position_marker()
            
            # В самом конце создаем робота заново
            self.robot.x = robot_x
            self.robot.y = robot_y
            self.robot.robot = self.canvas.create_image(
                self.robot._calculate_screen_x(),
                self.robot._calculate_screen_y(),
                image=self.robot.photo_image,
                tags="robot"
            )
            
            # Обновляем canvas
            self.canvas.update()
            
        except Exception as e:
            print(f"Error in redraw_field: {str(e)}")

    def create_grid(self):
        """Создание базовой сетки."""
        try:
            # Сохраняем текущие стены
            current_walls = dict(self.wall)
            
            # Очищаем существующие стены
            self.wall = {
                'left': [],
                'right': [],
                'up': [],
                'down': []
            }
            
            # Добавляем внешние границы
            for i in range(1, self.grid_size_m * self.grid_size_n + 1):
                # Левая граница поля
                if (i - 1) % self.grid_size_n == 0:
                    self.wall['left'].append(i)
                
                # Правая граница поля
                if i % self.grid_size_n == 0:
                    self.wall['right'].append(i)
                
                # Верхняя граница поля
                if i <= self.grid_size_n:
                    self.wall['up'].append(i)
                
                # Нижняя граница поля
                if i > self.grid_size_n * (self.grid_size_m - 1):
                    self.wall['down'].append(i)

            # Восстанавливаем сохраненные стены
            for direction in ['left', 'right', 'up', 'down']:
                self.wall[direction].extend(x for x in current_walls[direction] 
                                          if x not in self.wall[direction])

            # Добавляем подписи для столбцов (сверху)
            for i in range(self.grid_size_n):
                self.canvas.create_text(
                    self.offset + i * self.cell_size + self.cell_size/2,
                    self.offset/2,
                    text=str(i + 1),
                    font=('Arial', 12, 'bold')
                )

            # Добавляем подписи для строк (слева)
            for i in range(self.grid_size_m):
                self.canvas.create_text(
                    self.offset/2,
                    self.offset + i * self.cell_size + self.cell_size/2,
                    text=str(i + 1),
                    font=('Arial', 12, 'bold')
                )

            # Рисуем сетку
            for i in range(self.grid_size_m + 1):
                y = i * self.cell_size + self.offset
                self.canvas.create_line(
                    self.offset, y,
                    self.grid_size_n * self.cell_size + self.offset, y,
                    fill="grey" if i not in (0, self.grid_size_m) else "black",
                    width=1 if i not in (0, self.grid_size_m) else 3,
                    tags="grid"
                )
            
            for j in range(self.grid_size_n + 1):
                x = j * self.cell_size + self.offset
                self.canvas.create_line(
                    x, self.offset,
                    x, self.grid_size_m * self.cell_size + self.offset,
                    fill="grey" if j not in (0, self.grid_size_n) else "black",
                    width=1 if j not in (0, self.grid_size_n) else 3,
                    tags="grid"
                )
                
        except Exception as e:
            print(f"Error in create_grid: {str(e)}")

    def draw_walls(self):
        """Отрисовка стен."""
        try:
            border_width = 3
            for direction, cells in self.wall.items():
                for cell in cells:
                    x = (cell - 1) % self.grid_size_n
                    y = (cell - 1) // self.grid_size_n
                    if direction == 'left':
                        self.canvas.create_line(
                            x * self.cell_size + self.offset, y * self.cell_size + self.offset,
                            x * self.cell_size + self.offset, (y + 1) * self.cell_size + self.offset,
                            fill="black", width=border_width, tags="wall"
                        )
                    elif direction == 'right':
                        self.canvas.create_line(
                            (x + 1) * self.cell_size + self.offset, y * self.cell_size + self.offset,
                            (x + 1) * self.cell_size + self.offset, (y + 1) * self.cell_size + self.offset,
                            fill="black", width=border_width, tags="wall"
                        )
                    elif direction == 'up':
                        self.canvas.create_line(
                            x * self.cell_size + self.offset, y * self.cell_size + self.offset,
                            (x + 1) * self.cell_size + self.offset, y * self.cell_size + self.offset,
                            fill="black", width=border_width, tags="wall"
                        )
                    elif direction == 'down':
                        self.canvas.create_line(
                            x * self.cell_size + self.offset, (y + 1) * self.cell_size + self.offset,
                            (x + 1) * self.cell_size + self.offset, (y + 1) * self.cell_size + self.offset,
                            fill="black", width=border_width, tags="wall"
                        )
                    
        except Exception as e:
            print(f"Error in draw_walls: {str(e)}")

    def draw_cells_to_fill(self):
        """Отрисовка маркеров для клеток, которые нужно закрасить."""
        try:
            # Удаляем старые маркеры для закраски
            self.canvas.delete("cell_to_fill")
            
            for cell in self.cells_to_fill:
                if isinstance(cell, int):
                    x = (cell - 1) % self.grid_size_n
                    y = (cell - 1) // self.grid_size_n
                    marker_size = self.cell_size * 0.25
                    marker_x = x * self.cell_size + self.offset + (self.cell_size - marker_size) / 2
                    marker_y = y * self.cell_size + self.offset + (self.cell_size - marker_size) / 2
                    
                    # Рисуем зеленый квадрат для клетки, которую нужно закрасить
                    self.canvas.create_rectangle(
                        marker_x, marker_y,
                        marker_x + marker_size, marker_y + marker_size,
                        fill="green", tags="cell_to_fill"
                    )
            
            # Поднимаем маркер конечной позиции над маркерами для закраски
            self.canvas.tag_raise("end_marker")
            # Поднимаем робота над всеми маркерами
            self.canvas.tag_raise(self.robot.robot)
            
        except Exception as e:
            print(f"Error in draw_cells_to_fill: {str(e)}")

    def draw_end_position_marker(self):
        """Отрисовка маркера конечной позиции."""
        if self.end_position is not None:
            # Удаляем старый маркер конечной позиции
            self.canvas.delete("end_marker")
            
            x = (self.end_position - 1) % self.grid_size_n
            y = (self.end_position - 1) // self.grid_size_n
            marker_size = self.cell_size * 0.125
            
            # Вычисляем координаты для левого верхнего угла клетки
            marker_x = x * self.cell_size + self.offset + marker_size
            marker_y = y * self.cell_size + self.offset + marker_size
            
            # Рисуем черный квадрат для конечной позиции
            self.canvas.create_rectangle(
                marker_x, marker_y,
                marker_x + marker_size, marker_y + marker_size,
                fill="black", tags="end_marker"
            )
            
            # Поднимаем маркер конечной позиции над маркерами для закраски
            self.canvas.tag_raise("end_marker")
            # Поднимаем робота над всеми маркерами
            self.canvas.tag_raise(self.robot.robot)

    def add_new_tab(self):
        """Добавляет новую вкладку с текстовым полем."""
        frame = tk.Frame(self.notebook)
        text_widget = tk.Text(frame, wrap=tk.WORD, undo=True, maxundo=-1, autoseparators=True)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Привязываем обработчики событий
        text_widget.bind('<KeyPress>', self.on_key_press)
        text_widget.bind('<KeyRelease>', self.on_key_release)
        text_widget.bind('<<Paste>>', self.handle_paste)
        text_widget.bind('<KeyRelease>', self.on_text_change)
        text_widget.bind('<<Paste>>', self.handle_paste)  # Добавляем обработчик вставки
        
        # Добавляем вкладку
        tab_name = f"Notepad {len(self.notebook.tabs()) + 1}"
        self.notebook.add(frame, text=tab_name)
        self.notebook.select(frame)
        
        return text_widget

    def handle_paste(self, event):
        """Обработчик вставки текста."""
        try:
            event.widget.delete("sel.first", "sel.last")
        except tk.TclError:
            pass  # Нет выделенного текста
        event.widget.insert("insert", event.widget.clipboard_get())
        return "break"  # Предотвращаем стандартную обработку вставки

    def on_key_press(self, event):
        """Обработчик нажатия клавиш."""
        try:
            widget = event.widget
            # Создаем точку отмены после каждого символа
            widget.after(1, lambda: widget.edit_separator())
        except Exception as e:
            print(f"Error in on_key_press: {str(e)}")

    def undo_last_action(self, event=None):
        """Отменяет последнее действие в активном текстовом поле."""
        try:
            text_widget = self.get_current_text_widget()
            if text_widget:
                text_widget.edit_undo()
                text_widget.edit_separator()  # Создаем новую точку отмены
            return "break"
        except tk.TclError:
            pass  # Игнорируем ошибку, если нет действий для отмены

    def redo_last_action(self, event=None):
        """Восстанавливает последнее отмененное действие в активном текстовом поле."""
        try:
            text_widget = self.get_current_text_widget()
            if text_widget:
                text_widget.edit_redo()
                text_widget.edit_separator()  # Создаем новую точку отмены
            return "break"
        except tk.TclError:
            pass  # Игнорием ошибку, если нет действий для восстановления

    def get_current_text_widget(self):
        """Получает текущий активный текстовый виджет."""
        try:
            current_tab = self.notebook.select()
            if current_tab:
                frame = self.notebook.nametowidget(current_tab)
                for widget in frame.winfo_children():
                    if isinstance(widget, tk.Text):
                        return widget
        except Exception as e:
            print(f"Error getting current text widget: {str(e)}")
        return None

    def show_tab_context_menu(self, event):
        """Показывает контекстное меню при клике правой кнопкой мыши на вкладку."""
        try:
            clicked_tab = self.notebook.tk.call(self.notebook._w, "identify", "tab", event.x, event.y)
            if clicked_tab is not None:
                self.right_clicked_tab = self.notebook.tabs()[int(clicked_tab)]
                self.tab_context_menu.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"Error showing context menu: {e}")

    def close_tab(self, tab):
        """Закрывает указанную вкладку."""
        if len(self.notebook.tabs()) > 1:  # Проверяем, что это не последняя вкладка
            self.notebook.forget(tab)
        else:
            messagebox.showwarning("Warning", "Cannot close the last tab.")

    def close_other_tabs(self):
        """Закрывает все вкладки, кроме текущей."""
        current_tab = self.notebook.select()
        tabs_to_close = [tab for tab in self.notebook.tabs() if tab != current_tab]
        
        if tabs_to_close:
            for tab in tabs_to_close:
                self.notebook.forget(tab)

    def open_file(self):
        """Открывает файл и создает новую вкладку с его содержимым."""
        file_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py"), ("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            # Получаем имя файла из полного пути
            file_name = file_path.split('/')[-1]
            
            # Создаем новую вкладку
            frame = tk.Frame(self.notebook)
            code_input = tk.Text(frame, wrap=tk.WORD)
            code_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Привязываем обработчики событий для подсветки синтаксиса
            code_input.bind('<KeyRelease>', self.highlight_syntax)
            code_input.bind('<KeyRelease-Return>', self.highlight_syntax)
            code_input.bind('<KeyRelease-BackSpace>', self.highlight_syntax)
            code_input.bind('<KeyRelease-Delete>', self.highlight_syntax)
            code_input.bind('<KeyRelease-space>', self.highlight_syntax)
            
            # Читаем содержимое файла
            with open(file_path, "r", encoding='utf-8') as file:
                content = file.read()
                code_input.delete("1.0", tk.END)
                code_input.insert(tk.END, content)
            
            # Добавляем вкладку с именем файла
            self.notebook.add(frame, text=file_name)
            self.notebook.select(frame)
            
            # Применяем подсветку синтаксиса к загруженному содержимому
            self.highlight_syntax(None)

    def save_file(self):
        """Сохраняет содержимое текущей вкладки в файл."""
        try:
            current_tab = self.notebook.select()
            if not current_tab:
                return
                
            # Получаем текущее имя вкладки
            current_tab_name = self.notebook.tab(current_tab, "text")
            
            # Если это новый файл (имя начинается с "Notepad"), используем диалог сохранения
            if current_tab_name.startswith("Notepad"):
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".py",
                    filetypes=[("Python files", "*.py"), ("Text files", "*.txt"), ("All files", "*.*")]
                )
            else:
                # Для уже существующих файлов используем текущее имя
                file_path = current_tab_name
                
            if file_path:
                text_widget = self.get_current_text_widget()
                if text_widget:
                    with open(file_path, "w", encoding='utf-8') as file:
                        file.write(text_widget.get("1.0", tk.END))
                    
                    # Обновляем имя вкладки на имя файла
                    file_name = file_path.split('/')[-1]
                    tab_id = self.notebook.index(current_tab)
                    self.notebook.tab(tab_id, text=file_name)
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении файла: {str(e)}")

    def clear_filled_cells(self):
        """Очищает все закрашенные клетки."""
        for cell in self.filled_cells:
            x = (cell - 1) % self.grid_size_n
            y = (cell - 1) // self.grid_size_n
            self.canvas.create_rectangle(
                x * self.cell_size + self.offset,
                y * self.cell_size + self.offset,
                (x + 1) * self.cell_size + self.offset,
                (y + 1) * self.cell_size + self.offset,
                fill="white", outline="black"
            )
        self.filled_cells = []

    def run_code(self):
        """Запускает код из текущей вкладки."""
        try:
            # Скрываем подсказки при запуске кода
            self.suggestion_box.place_forget()
            
            # Получаем текущий текстовый виджет
            current_tab = self.notebook.select()
            if not current_tab:
                return
            
            text_widget = self.notebook.nametowidget(current_tab).winfo_children()[0]
            code = text_widget.get("1.0", tk.END).strip()
            
            # Останавливаем предыдущее выполнение
            self.running = False
            if hasattr(self, 'program_thread') and self.program_thread.is_alive():
                self.program_thread.join(timeout=1.0)
            
            # Очищаем вывод
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete(1.0, tk.END)
            self.output_text.config(state=tk.DISABLED)

            # Сбрасываем позицию робота в начальную точку
            self.robot.reset_position()
            
            # Очищаем закрашенные клетки
            self.filled_cells = []
            # Перерисовываем все клетки как белые
            self.clear_grid()
            
            # Перерисовываем сетку
            self.create_grid()
            
            # Перерисовываем робота
            self.robot.update_image(self.cell_size)
            self.canvas.coords(
                self.robot.robot,
                self.robot._calculate_screen_x(),
                self.robot._calculate_screen_y()
            )
            self.canvas.tag_raise(self.robot.robot)
            
            # Если есть сохраненное задание, перезагружаем его
            if self.current_task_type and self.current_task_num:
                self.reload_current_task()
                self.task_status_label.config(text=f"Статус: Задание {self.current_task_type}{self.current_task_num}", fg="blue")
            else:
                self.task_status_label.config(text="Статус: Задание не выбрано", fg="black")

            # Если есть конечная точка, показываем окно окружения
            if self.end_position is not None:
                self.show_environment_window()

            # Получаем код из текстового поля
            code = text_widget.get(1.0, tk.END)

            # Устанавливаем флаг выполнения
            self.running = True

            self.root.update()  # Обновляем интерфейс немедленно
            
            # Создаем новый поток для выполнения кода
            self.program_thread = threading.Thread(target=self.execute_code, args=(code,))
            self.program_thread.daemon = True
            self.program_thread.start()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при запуске кода: {str(e)}")
            self.running = False
            self.task_status_label.config(text="Статус: Ошибка", fg="red")

    def reload_current_task(self):
        """Перезагружает текущее задание."""
        try:
            if hasattr(self, 'current_task_type') and hasattr(self, 'current_task_num'):
                self.filled_cells = []
                self.cells_to_fill = []
                self.wall = {'up': [], 'down': [], 'left': [], 'right': []}
                self.end_position = None
                
                for item in self.canvas.find_all():
                    if item != self.robot.robot:
                        self.canvas.delete(item)
                
                self.create_grid()
                
                if self.current_task_type == "custom":
                    if hasattr(self, 'saved_environment'):
                        self.load_environment_from_memory()
                else:
                    task_func_name = f"{self.current_task_type}_task_{self.current_task_num}"
                    task_func = getattr(tasks, task_func_name)
                    task_func(self, self.current_task_num)
                
                self.canvas.update()
                self.canvas.tag_raise(self.robot.robot)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при перезагрузке задания: {str(e)}")

    def clear_grid(self):
        """Очищает сетку от закрашенных клеток."""
        # Удаляем все прямоугольники с canvas, кроме базовой сетки
        for item in self.canvas.find_all():
            if self.canvas.type(item) == "rectangle" and "grid" not in self.canvas.gettags(item):
                self.canvas.delete(item)
        
        # Очищаем список закрашенных клеток
        self.filled_cells = []
        
        # Поднимаем робота наверх
        self.canvas.tag_raise(self.robot.robot)

    def execute_code(self, code):
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        try:
            # Получаем текущий текстовый виджет
            text_widget = self.get_current_text_widget()
            if text_widget:
                text_widget.tag_remove("error", "1.0", "end")
            
            # Создаем очередь для обмена данными между потоками
            input_queue = queue.Queue()
            
            def custom_input(prompt=''):
                def show_dialog():
                    result = simpledialog.askstring("Input", prompt if prompt else "Введите значение:", parent=self.root)
                    input_queue.put(result)
                
                # Запускаем диалог в главном потоке
                self.root.after(0, show_dialog)
                # Ждем результат
                result = input_queue.get()
                if result is None:
                    raise ValueError("Ввод отменен")
                return result
            
            # Создаем глобальные функции для управления роботом
            globals_dict = {
                'left': self.robot.left,
                'right': self.robot.right,
                'up': self.robot.up,
                'down': self.robot.down,
                'move': self.robot.move,
                'fillcell': self.robot.fillcell,
                'pos': self.robot.pos,
                'goto': self.robot.goto,
                'start_pos': self.robot.start_pos,
                'task': self.task_function,
                'freefromleft': self.freefromleft,
                'freefromright': self.freefromright,
                'freefromup': self.freefromup,
                'freefromdown': self.freefromdown,
                'wallfromleft': self.wallfromleft,
                'wallfromright': self.wallfromright,
                'wallfromup': self.wallfromup,
                'wallfromdown': self.wallfromdown,
                'cellispainted': self.robot.cellispainted,
                'cellisfree': self.robot.cellisfree,
                'add_wall': self.add_wall,
                'mark_cell_to_fill': self.mark_cell_to_fill,
                'add_end_position': self.add_end_position,
                'input': custom_input
            }
            
            # Пытаемся выполнить код с новыми глобальными функциями
            exec(code, globals_dict)
            
            output = sys.stdout.getvalue()
            error = sys.stderr.getvalue()
            
            if error:
                # Остальной код обработки ошибок остается без изменений
                error_line = None
                for line in error.split('\n'):
                    if "line" in line:
                        try:
                            error_line = int(line.split("line")[1].split()[0])
                            break
                        except (IndexError, ValueError):
                            continue
                
                if error_line is not None and text_widget:
                    start = f"{error_line}.0"
                    end = f"{error_line}.end"
                    text_widget.tag_add("error", start, end)
                    text_widget.tag_config("error", background="pink", foreground="red")
                    
                    error_message = f"Ошибка в строке {error_line}: {error.split(':', 2)[-1].strip()}"
                else:
                    error_message = error
                
                self.show_output(error_message, "red")
                self.task_status_label.config(
                    text="Статус: Ошибка выполнения",
                    fg="red"
                )
            else:
                if text_widget:
                    text_widget.tag_remove("error", "1.0", "end")
                self.show_output(output, "black")
                
                if self.end_position is not None:
                    if self.end_position and self.robot.pos() != self.end_position:
                        self.task_status_label.config(
                            text="Статус: Робот не в конечной точке",
                            fg="red"
                        )
                    elif self.cells_to_fill and not all(cell in self.filled_cells for cell in self.cells_to_fill):
                        self.task_status_label.config(
                            text="Статус: Не все требуемые клетки закрашены",
                            fg="red"
                        )
                    elif not self.running:
                        self.task_status_label.config(
                            text="Статус: Выполнение остановлено",
                            fg="red"
                        )
                    else:
                        self.task_status_label.config(
                            text="Статус: Задание выполнено успешно",
                            fg="green"
                        )
                    self.check_task()
                
        except Exception as e:
            error_message = str(e)
            error_line = 1
            if "line" in error_message:
                try:
                    error_line = int(error_message.split("line")[1].split()[0])
                except (IndexError, ValueError):
                    pass
            
            if text_widget:
                start = f"{error_line}.0"
                end = f"{error_line}.end"
                text_widget.tag_add("error", start, end)
                text_widget.tag_config("error", background="pink", foreground="red")
            
            if isinstance(e, NameError):
                var_name = str(e).split("'")[1]
                error_message = f"Ошибка в строке {error_line}: Переменная или функция '{var_name}' не определена"
            else:
                error_message = f"Ошибка в строке {error_line}: {str(e)}"
            
            self.show_output(error_message, "red")
            self.task_status_label.config(
                text="Статус: Ошибка выполнения",
                fg="red"
            )
            
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            self.running = False
            # Убираем обновление статуса здесь

    def get_input(self, prompt='', input_type=str, default=None):
        result = None
        if input_type == int:
            result = simpledialog.askinteger("Input", prompt, initialvalue=default)
        elif input_type == float:
            result = simpledialog.askfloat("Input", prompt, initialvalue=default)
        else:
            result = simpledialog.askstring("Input", prompt, initialvalue=default)

        if result is None:
            return default

        return result

    def task_function(self, task_str):
        """Функция для вызова задания из кода."""
        try:
            # Находим все цифры в строке и объединяем их в число
            task_number = int(''.join(filter(str.isdigit, task_str)))
            # Получаем тип задания, убирая все цифры из строки
            task_type = ''.join(filter(str.isalpha, task_str))
            
            if task_type in self.task and 1 <= task_number <= len(self.task[task_type]):
                # Отключаем обновление canvas на время загрузки
                self.canvas.config(state='disabled')
                
                # Сохраняем информацию о текущем задании
                self.current_task_type = task_type
                self.current_task_num = task_number
                
                # Очищаем текущее задание без принудительного обновления
                self.clear_task(update=False)
                
                # Вызываем функцию задания (с учетом индексации с 0)
                task_func = self.task[task_type][task_number - 1]
                task_func(self, task_number)
                
                # Обновляем метки статуса
                status_text = f"Статус: Задание {task_type}{task_number}"
                self.selected_task_label.config(text=f"Выбранное задание: {task_type}{task_number}")
                self.task_status_label.config(text=status_text, fg="black")
                
                # Включаем обновление canvas и принудительно обновляем один раз
                self.canvas.config(state='normal')
                self.canvas.update_idletasks()
                
            else:
                messagebox.showerror("Error", f"Task {task_str} not found.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading task: {str(e)}")

    def clear_task(self, update=True):
        """Полная очистка поля и сброс всех параметров задания."""
        try:
            # Очищаем все списки и параметры
            self.filled_cells = []
            self.cells_to_fill = []  # Важно очистить список клеток для закрашивания
            self.wall = {
                'left': [],
                'right': [],
                'up': [],
                'down': []
            }
            self.end_position = None
            
            # Удаляем все объекты с canvas, кроме робота
            for item in self.canvas.find_all():
                if item != self.robot.robot:
                    self.canvas.delete(item)
            
            # Сбрасываем позицию робота
            self.robot.reset_position()
            
            # Перерисовываем базовую сетку
            self.create_grid()
            
            # Поднимаем робота над остальными элементами
            self.canvas.tag_raise(self.robot.robot)
            
            # Обновляем canvas только если требуется
            if update:
                self.canvas.update()
            
        except Exception as e:
            print(f"Error in clear_task: {str(e)}")

    def show_task_window(self, task_type):
        """Показывает окно выбора задания."""
        task_window = tk.Toplevel(self.root)
        task_window.title(f"Выберите задание {task_type}")
        task_window.geometry("300x150")  # Уменьшаем ширину окна
        task_window.transient(self.root)  # Делаем окно модальным
        task_window.grab_set()  # Захватываем фокус

        # Создаем фрейм для кнопок
        button_frame = tk.Frame(task_window)
        button_frame.pack(expand=True, pady=10)

        # Создаем кнопки в два ряда с уменьшенной шириной
        for i in range(10):  # Для заданий 1-10
            row = 1 if i >= 5 else 0  # Определяем ряд (0 или 1)
            col = i % 5  # Определяем колонку (0-4)
            
            btn = tk.Button(
                button_frame,
                text=str(i+1),
                width=5,  # Уменьшаем ширину кнопок в 2 раза (было 10)
                command=lambda t=task_type, x=i+1: self.select_and_close_task(t, x, task_window)
            )
            btn.grid(row=row, column=col, padx=5, pady=5)

    def select_and_close_task(self, task_type, task_num, window):
        """Выбирает задание и закрывает окно выбора."""
        self.task_function(f"{task_type}{task_num}")
        window.destroy()

    def select_task_and_close(self, task_type, task_num, window):
        """Выбирает задание и закрывает окно выбора."""
        try:
            # Обновляем статусы до закрытия окна
            status_text = f"Статус: Задание {task_type}{task_num}"
            self.selected_task_label.config(text=f"Selected Task: {task_type}{task_num}")
            self.task_status_label.config(text=status_text, fg="black")
            
            # Закрываем окно выбора задания
            window.destroy()
            
            # Вызываем метод загрузки задания
            self.select_task(task_type, task_num)
            
            # Принудительно обновляем интерфейс
            self.root.update()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при выборе задания: {str(e)}")

    def select_task(self, task_type, task_num):
        """Выбирает и сохраняет текущее задание."""
        try:
            # Сохраняем информацию о текущем задании
            self.current_task_type = task_type
            self.current_task_num = task_num
            
            # Формируем текст статуса
            status_text = f"Статус: Задание {task_type}{task_num}"
            
            # Обновляем обе метки статуса
            self.selected_task_label.config(text=f"Selected Task: {task_type}{task_num}")
            self.task_status_label.config(text=status_text, fg="black")
            
            # Загружаем задание
            self.reload_current_task()
            
            # Явно обновляем изображение робота и его позицию
            self.robot.update_image(self.cell_size)
            self.canvas.coords(
                self.robot.robot,
                self.robot._calculate_screen_x(),
                self.robot._calculate_screen_y()
            )
            self.canvas.tag_raise(self.robot.robot)  # Поднимаем робота над остальными элементами
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при выборе задания: {str(e)}")

    def show_output(self, output, color):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, output)
        self.output_text.config(state=tk.DISABLED, fg=color)

    def highlight_error_line(self, error):
        error_line = int(error.split("line ")[1].split()[0])
        self.code_input.tag_add("error", f"{error_line}.0", f"{error_line}.end")
        self.code_input.tag_config("error", background="red")

    def show_help(self):
        """Показать справку."""
        try:
            help_window = tk.Toplevel(self.root)
            help_window.title("Справка")

            # Получаем размеры и позицию основного окна
            main_window_height = self.root.winfo_height()
            main_window_x = self.root.winfo_x()
            main_window_y = self.root.winfo_y()

            # Устанавливаем размеры окна справки
            help_window.geometry(f"500x{main_window_height}")

            # Создаем текстовый виджет с полосой прокрутки
            text_frame = tk.Frame(help_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            scrollbar = tk.Scrollbar(text_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            help_text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
            help_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            scrollbar.config(command=help_text.yview)

            # Обновленный текст справки
            help_content = """СПРАВКА ПО КОМАНДАМ РОБОТА

1. Базовые команды перемещения:
   - up() - перемещение на одну клетку вверх
   - down() - перемещение на одну клетку вниз
   - left() - перемещение на одну клетку влево
   - right() - перемещение на одну клетку вправо

2. Команды определения положения:
   - pos() - возвращает номер текущей клетки
   - goto(x) - перемещение в клетку с номером x
   - goto(m, n) - перемещение в клетку в строке m и столбце n
   - start_pos(x) - установка начальной позиции в клетку x
   - start_pos(x,y) - установка начальной позиции в клетку x,y
   - add_end_position(x) - установка конечной позиции в клетку x
   - add_end_position(m,n) - установка конечной позиции в клетку m,n


3. Команды работы с клетками:
   - fillcell() - закрасить текущую клетку
   - cellispainted() - проверить, закрашена ли текущая клетка
   - cellisfree() - проверить, свободна ли текущая клетка
   - mark_cell_to_fill(x) - отметить клетку x для закрашивания
   - add_wall('направление',x) - добавить стену в клетку x
   - add_wall('направление',m,n) - добавить стену в клетку m,n
   - field(m,n) - создать поле m на n клеток

4. Команды проверки стен:
   - wallfromleft() - проверить наличие стены слева
   - wallfromright() - проверить наличие стены справа
   - wallfromup() - проверить наличие стены сверху
   - wallfromdown() - проверить наличие стены снизу

5. Команды проверки свободного пространства:
   - freefromleft() - проверить отсутствие стены слева
   - freefromright() - проверить отсутствие стены справа
   - freefromup() - проверить отсутствие стены сверху
   - freefromdown() - проверить отсутствие стены снизу

6. Управление выполнением:
   - F5 - запуск программы
   - Кнопка "Stop" - остановка выполнения

7. Работа с кодом:
   - Ctrl+Z - отменить последнее действие
   - Ctrl+Shift+Z - повторить отмененное действие
   - Ctrl+S - сохранить файл
"""

            help_text.insert(tk.END, help_content)
            help_text.config(state=tk.DISABLED)  # Делаем текст только для чтения

            # Позиционируем окно справки слева от основного окна
            help_window.update_idletasks()
            x = main_window_x - help_window.winfo_width()
            y = main_window_y
            help_window.geometry(f"+{x}+{y}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при открытии справки: {str(e)}")


    def stop_code(self):
        """Останавливает выполнение кода."""
        self.running = False

    def open_remote_control(self):
        remote_window = tk.Toplevel(self.root)
        remote_window.title("Пульт управления роботом")
        remote_window.geometry("200x200")
        button_frame = tk.Frame(remote_window)
        button_frame.pack(expand=True, fill=tk.BOTH)

        # Create buttons for controlling the robot
        up_button = tk.Button(button_frame, text="↑", command=lambda: self.execute_and_append("up"), bg="grey", fg="white", font=("Arial", 16))
        up_button.grid(row=0, column=1, pady=10)

        left_button = tk.Button(button_frame, text="←", command=lambda: self.execute_and_append("left"), bg="grey", fg="white", font=("Arial", 16))
        left_button.grid(row=1, column=0, padx=10)

        fill_button = tk.Button(button_frame, text="FILL", command=lambda: self.execute_and_append("fillcell"), bg="green", fg="white", font=("Arial", 16))
        fill_button.grid(row=1, column=1, pady=10, padx=10)

        right_button = tk.Button(button_frame, text="→", command=lambda: self.execute_and_append("right"), bg="grey", fg="white", font=("Arial", 16))
        right_button.grid(row=1, column=2, padx=10)

        down_button = tk.Button(button_frame, text="↓", command=lambda: self.execute_and_append("down"), bg="grey", fg="white", font=("Arial", 16))
        down_button.grid(row=2, column=1, pady=10)

    def execute_and_append(self, command):
        """Выполняет команду робота с пульта управления."""
        if not self.robot.is_moving:  # Проверяем, что робот не двигается
            try:
                # Сохраняем стартовую позицию
                start_x = self.robot.start_x if hasattr(self.robot, 'start_x') else self.robot.pos_x
                start_y = self.robot.start_y if hasattr(self.robot, 'start_y') else self.robot.pos_y
                
                # Временно включаем running для выполнения команды
                self.running = True
                
                # Оптимизация: Кэшируем метод
                robot_command = getattr(self.robot, command)
                robot_command()
                
                # Оптимизация: Формируем строку без конкатенации
                self.append_command("{}()".format(command))
                
                # Восстанавливаем стартовую позицию
                self.robot.start_x = start_x
                self.robot.start_y = start_y
                
            except Exception as e:
                print(f"Ошибка при выполнении команды: {e}")
            finally:
                # Выключаем running только если не выполняется программа
                if not self.program_running:
                    self.running = False

    def append_command(self, command):
        """Добавляет команду в активный редактор с мгновенной подсветкой."""
        active_code_input = self.get_active_code_input()
        if not active_code_input:
            return
            
        # Оптимизация: Кэшируем теги и операции
        if not hasattr(self, '_function_tag_configured'):
            active_code_input.tag_configure("function", foreground="blue")
            self._function_tag_configured = True
        
        # Оптимизация: Используем более эффективный способ вставки
        insert_pos = active_code_input.index(tk.END)
        active_code_input.insert(tk.END, command + "\n")
        
        # Оптимизация: Избегаем преобразования строк
        line_start = float(insert_pos) - 1.0
        line_end = float(insert_pos)
        active_code_input.tag_add("function", f"{line_start:.1f}", f"{line_end:.1f}")
        
        # Оптимизация: Группируем обновления
        active_code_input.update_idletasks()

    def choose_font_size(self):
        """Открывает диалоговое окно для выбора размера шрифта."""
        font_size = simpledialog.askinteger("Выбор размера шрифта", "Введите размер шрифта:")
        if font_size:
            self.change_font_size(font_size)

    def change_font_size(self, font_size):
        """Изменяет размер шрифта в активном Notepad."""
        active_code_input = self.get_active_code_input()
        current_font = active_code_input.cget("font")
        if current_font:
            font_family = current_font.split(' ')[0]
            new_font = (font_family, font_size)
            active_code_input.config(font=new_font)

    def highlight_functions(self, text_widget):
        """Подсветка функций в тексте."""
        # Оптимизация: Кэшируем список функций
        if not hasattr(self, '_cached_functions'):
            self._cached_functions = [
                'up', 'down', 'left', 'right', 'move', 'fillcell',
                'pos', 'goto', 'start_pos', 'field', 'wallfromleft',
                'wallfromright', 'wallfromup', 'wallfromdown',
                'freefromleft', 'freefromright', 'freefromup', 'freefromdown',
                'cellispainted', 'cellisfree','add_wall','mark_cell_to_fill','start_pos',
                'add_end_position','if','while','for','foreach','else','elseif','endif',
                'task'
            ]
        
        # Удаляем старую подсветку
        text_widget.tag_remove("function", "1.0", "end")
        
        # Оптимизация: Кэшируем настройку тега
        if not hasattr(self, '_function_tag_configured'):
            text_widget.tag_configure("function", foreground="blue")
            self._function_tag_configured = True
        
        # Оптимизация: Получаем весь текст за один раз
        content = text_widget.get("1.0", "end")
        
        # Оптимизация: Используем регулярные выражения для поиска
        import re
        pattern = r'\b(' + '|'.join(map(re.escape, self._cached_functions)) + r')\b'
        
        for match in re.finditer(pattern, content):
            start_idx = match.start()
            end_idx = match.end()
            
            # Преобразуем индексы в формат Tkinter
            start_line = content.count('\n', 0, start_idx) + 1
            start_char = start_idx - content.rfind('\n', 0, start_idx) - 1
            if start_char < 0:
                start_char = start_idx
                
            end_line = content.count('\n', 0, end_idx) + 1
            end_char = end_idx - content.rfind('\n', 0, end_idx) - 1
            if end_char < 0:
                end_char = end_idx
            
            # Добавляем тег
            text_widget.tag_add('function', f'{start_line}.{start_char}', f'{end_line}.{end_char}')

    def wallfromleft(self):
        x = self.robot.pos()
        y = x - 1
        if x in self.wall['left']:
            return True
        return y in self.wall['right']
         

    def wallfromright(self):
        x = self.robot.pos()
        y = x + 1
        if x in self.wall['right']:
            return True
        return y in self.wall['left']

    def wallfromdown(self):
        x = self.robot.pos()
        y = x + self.grid_size_n
        if x in self.wall['down']:
            return True
        return y in self.wall['up']

    def wallfromup(self):
        x = self.robot.pos()
        y = x - self.grid_size_n
        if x in self.wall['up']:
            return True
        return y in self.wall['down']

    def freefromleft(self):
        return not self.wallfromleft()

    def freefromright(self):
        return not self.wallfromright()

    def freefromdown(self):
        return not self.wallfromdown()

    def freefromup(self):
        return not self.wallfromup()

    def save_environment_to_memory(self):
        self.saved_environment = {
            'robot_start_pos': (self.robot.pos_x, self.robot.pos_y),
            'filled_cells': self.filled_cells,
            'walls': self.wall,
            'grid_size': (self.grid_size_m, self.grid_size_n),
            'end_position': self.end_position,
            'cells_to_fill': self.cells_to_fill
        }
    def clear_environment(self):
        # Сброс позиции робота
        self.robot.pos_x = 0
        self.robot.pos_y = 0
        self.robot.reset_position()

        # Очистка закрашенных клеток
        self.filled_cells = []

        # Очистка стен
        self.wall = {
            'left': [],
            'right': [],
            'up': [],
            'down': []
        }

        # Сброс размера сетки
        self.grid_size_m = 5
        self.grid_size_n = 5

        # Сброс конечной позиции
        self.end_position = None

        # Очистка клеток для закраски
        self.cells_to_fill = []

        # Пересоздание сетки
        self.create_grid()

        # Обновление робота и маркеров
        self.robot.update_image(self.cell_size)
        self.robot.update_position(self.robot.pos_x, self.robot.pos_y)
        self.draw_end_position_marker()
        
        # Поднимаем робота наверх через canvas
        self.canvas.tag_raise(self.robot.robot)  # Изменено с robot.tag_raise на canvas.tag_raise

        # Сброс сохраненного окружения
        self.saved_environment = {}

    def load_environment_from_memory(self):
        if hasattr(self, 'saved_environment'):
            environment = self.saved_environment
            self.robot.pos_x, self.robot.pos_y = environment.get('robot_start_pos', (self.robot.pos_x, self.robot.pos_y))
            self.filled_cells = environment.get('filled_cells', [])
            self.wall = environment.get('walls', {
                'left': [],
                'right': [],
                'up': [],
                'down': []
            })
            self.grid_size_m, self.grid_size_n = environment.get('grid_size', (self.grid_size_m, self.grid_size_n))
            self.end_position = environment.get('end_position', None)
            self.cells_to_fill = environment.get('cells_to_fill', [])
            self.create_grid()
            self.robot.reset_position()
            self.draw_walls()
            self.draw_cells_to_fill()
            self.draw_end_position_marker()

    def save_environment_to_file(self):
        self.save_environment_to_memory()
        file_path = filedialog.asksaveasfilename(defaultextension=".env",
                                                 filetypes=[("Environment files", "*.env"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                json.dump(self.saved_environment, file)
            messagebox.showinfo("Сохранение", "Окружение сохранено в файл.")
        self.clear_environment()

    def load_environment_from_file(self):
        """Загружает окружение из файла."""
        file_path = filedialog.askopenfilename(filetypes=[("Environment files", "*.env"), ("All files", "*.*")])
        if file_path:
            try:
                # Сначала загружаем данные из файла
                with open(file_path, "r") as file:
                    file_content = file.read().strip()
                    if not file_content:
                        raise ValueError("The file is empty.")
                    self.saved_environment = json.loads(file_content)
                
                # Сохраняем идентификатор робота
                robot_id = self.robot.robot
                
                # Удаляем все элементы с canvas, кроме робота
                for item in self.canvas.find_all():
                    if item != robot_id:
                        self.canvas.delete(item)
                
                # Очищаем все структуры данных
                self.filled_cells = []
                self.cells_to_fill = []
                self.wall = {'up': [], 'down': [], 'left': [], 'right': []}
                self.end_position = None
                
                # Создаем базовую сетку
                self.create_grid()
                
                # Теперь загружаем новое окружение
                self.load_environment_from_memory()
                
                # Обновляем позицию робота и поднимаем его над остальными элементами
                self.robot.update_image(self.cell_size)
                self.canvas.coords(
                    self.robot.robot,
                    self.robot._calculate_screen_x(),
                    self.robot._calculate_screen_y()
                )
                self.canvas.tag_raise(self.robot.robot)
                
                # Устанавливаем текущее задание как "загруженное из файла"
                self.current_task_type = "custom"
                self.current_task_num = 1
                
                # Обновляем метки статуса
                self.selected_task_label.config(text="Selected Task: Loaded from file")
                self.task_status_label.config(text="Статус: Загружено из файла", fg="blue")
                
                messagebox.showinfo("Загрузка", "Окружение загружено из файла.")
                
            except json.JSONDecodeError:
                messagebox.showerror("Ошибка", "Файл содержит некорректные данные JSON.")
            except ValueError as ve:
                messagebox.showerror("Ошибка", str(ve))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла ошибка при загрузке окружения: {e}")

    def mark_cell_to_fill(self, *args):
        """
        Отмечает клетки, которые нужно закрасить.
        Принимает либо номер клетки, либо координаты (m, n).
        """
        try:
            if len(args) == 1:
                # Если передан один аргумент - это номер клетки
                cell_number = args[0]
                if isinstance(cell_number, int):
                    if cell_number not in self.cells_to_fill:
                        self.cells_to_fill.append(cell_number)
                        self.draw_cells_to_fill()
            elif len(args) == 2:
                # Если переданы два аргумента - это координаты m и n
                m, n = args
                if isinstance(m, int) and isinstance(n, int):
                    # Преобразуем координаты в номер клетки
                    cell_number = (m - 1) * self.grid_size_n + n
                    if cell_number not in self.cells_to_fill:
                        self.cells_to_fill.append(cell_number)
                        self.draw_cells_to_fill()
            else:
                raise ValueError("Неверное количество аргументов")
            
        except Exception as e:
            print(f"Error in mark_cell_to_fill: {str(e)}")

    def draw_cells_to_fill(self):
        """Отрисовка маркеров для клеток, которые нужно закрасить."""
        try:
            # Удаляем старые маркеры для закраски
            self.canvas.delete("cell_to_fill")
            
            for cell in self.cells_to_fill:
                if isinstance(cell, int):
                    x = (cell - 1) % self.grid_size_n
                    y = (cell - 1) // self.grid_size_n
                    marker_size = self.cell_size * 0.25
                    marker_x = x * self.cell_size + self.offset + (self.cell_size - marker_size) / 2
                    marker_y = y * self.cell_size + self.offset + (self.cell_size - marker_size) / 2
                    
                    # Рисуем зеленый квадрат для клетки, которую нужно закрасить
                    self.canvas.create_rectangle(
                        marker_x, marker_y,
                        marker_x + marker_size, marker_y + marker_size,
                        fill="green", tags="cell_to_fill"
                    )
            
            # Поднимаем маркер конечной позиции над маркерами для закраски
            self.canvas.tag_raise("end_marker")
            # Поднимаем робота над всеми маркерами
            self.canvas.tag_raise(self.robot.robot)
            
        except Exception as e:
            print(f"Error in draw_cells_to_fill: {str(e)}")

    def draw_end_position_marker(self):
        """Отрисовка маркера конечной позиции."""
        if self.end_position is not None:
            # Удаляем старый маркер конечной позиции
            self.canvas.delete("end_marker")
            
            x = (self.end_position - 1) % self.grid_size_n
            y = (self.end_position - 1) // self.grid_size_n
            marker_size = self.cell_size * 0.125
            
            # Вычисляем координаты для левого верхнего угла клетки
            marker_x = x * self.cell_size + self.offset + marker_size
            marker_y = y * self.cell_size + self.offset + marker_size
            
            # Рисуем черный квадрат для конечной позиции
            self.canvas.create_rectangle(
                marker_x, marker_y,
                marker_x + marker_size, marker_y + marker_size,
                fill="black", tags="end_marker"
            )
            
            # Поднимаем маркер конечной позиции над маркерами для закраски
            self.canvas.tag_raise("end_marker")
            # Поднимаем робота над всеми маркерами
            self.canvas.tag_raise(self.robot.robot)

    def check_task(self):
        """Проверяет выполнение задания."""
        try:
            in_end_position = self.robot.end_position()
            all_required_filled = all(cell in self.filled_cells for cell in self.cells_to_fill)
            no_extra_cells = all(cell in self.cells_to_fill for cell in self.filled_cells)
            
            if in_end_position and all_required_filled and no_extra_cells:
                self.task_status_label.config(
                    text="Статус: Задание выполнено!", 
                    fg="green"
                )
                self.task_message_label.config(text="")
                return True
            else:
                # Формируем список причин невыполнения
                reasons = []
                if not in_end_position:
                    reasons.append("- Робот не достиг конечной позиции")
                if not all_required_filled:
                    reasons.append("- Не все клетки закрашены")
                if not no_extra_cells:
                    reasons.append("- Есть лишние закрашенные клетки")
                
                # Формируем сообщение с переносами строк
                message = "Задание не выполнено:\n" + "\n".join(reasons)
                self.task_message_label.config(text=message, fg="red", justify=tk.LEFT)
                self.task_status_label.config(text="Статус: Задание не выполнено", fg="red")
                return False
                
        except Exception as e:
            error_message = f"Ошибка при проверке задания: {str(e)}"
            self.task_message_label.config(text=error_message, fg="red")
            self.task_status_label.config(text="Статус: Ошибка проверки", fg="red")
            return False

    def open_environment_editor(self):
        """Открывает окно редактирования окружения."""
        editor_window = tk.Toplevel(self.root)
        editor_window.title("Редактор окружения")
        editor_window.geometry("600x600")

        # Создаем canvas для редактора
        editor_canvas = tk.Canvas(editor_window, bg='white')
        editor_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Загружаем изображение робота
        try:
            robot_image = tk.PhotoImage(file=os.path.join(ICONS_DIR, 'robot.png'))
            scaled_size = int(self.cell_size * 0.8)
            robot_image = robot_image.subsample(
                max(1, int(robot_image.width() / scaled_size)),
                max(1, int(robot_image.height() / scaled_size))
            )
        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")
            robot_image = None

        # Копируем текущие параметры, используя стартовую позицию робота
        editor_data = {
            'grid_size_m': self.grid_size_m,
            'grid_size_n': self.grid_size_n,
            'cell_size': self.cell_size,
            'offset': self.offset,
            'walls': dict(self.wall),
            'filled_cells': list(self.cells_to_fill),
            'robot_pos': [self.robot.pos_x, self.robot.pos_y],  # Используем текущую позицию
            'end_position': self.end_position,
            'drag_data': {'x': 0, 'y': 0, 'dragging': False},
            'robot_image': robot_image
        }

        def get_cell_from_coords(x, y):
            """Получает индексы ячейки по координатам клика."""
            cell_x = int((x - editor_data['offset']) // editor_data['cell_size'])
            cell_y = int((y - editor_data['offset']) // editor_data['cell_size'])
            
            if (0 <= cell_x < editor_data['grid_size_n'] and 
                0 <= cell_y < editor_data['grid_size_m']):
                return cell_x, cell_y
            return None

        def get_cell_number(x, y):
            """Преобразует координаты ячейки в номер ячейки."""
            return y * editor_data['grid_size_n'] + x + 1

        def get_wall_at_click(event):
            """Определяет, есть ли стена в точке клика."""
            try:
                # Получаем координаты с учетом отступа для номеров
                x = event.x - editor_data['offset_x']
                y = event.y - editor_data['offset_y']
                
                # Получаем индексы ячейки
                cell_x = int(x // editor_data['cell_size'])
                cell_y = int(y // editor_data['cell_size'])
                
                # Проверяем границы поля
                if not (0 <= cell_x < editor_data['grid_size_n'] and 
                        0 <= cell_y < editor_data['grid_size_m']):
                    return None, None

                # Вычисляем относительные координаты внутри ячейки
                rel_x = x % editor_data['cell_size']
                rel_y = y % editor_data['cell_size']
                
                # Определяем область клика (граница = 5 пикселей)
                border_size = 5
                cell_number = cell_y * editor_data['grid_size_n'] + cell_x + 1

                # Проверяем левую границу
                if rel_x < border_size:
                    return 'left', cell_number
                # Проверяем правую границу
                elif rel_x > editor_data['cell_size'] - border_size:
                    # Для правой границы используем номер текущей ячейки
                    return 'right', cell_number
                # Проверяем верхнюю границу
                elif rel_y < border_size:
                    return 'up', cell_number
                # Проверяем нижнюю границу
                elif rel_y > editor_data['cell_size'] - border_size:
                    # Для нижней границы используем номер текущей ячейки
                    return 'down', cell_number
                
                return None, None
                
            except Exception as e:
                print(f"Error in get_wall_at_click: {str(e)}")
                return None, None

        def handle_click(event):
            """Обработка клика мыши."""
            try:
                # Если кликнули по роботу - начинаем перетаскивание
                if "robot" in editor_canvas.gettags("current"):
                    start_drag(event)
                    return

                # Проверяем, попал ли клик на границу ячейки
                wall_type, cell_number = get_wall_at_click(event)
                
                if wall_type:
                    # Если стена уже есть - удаляем её
                    if cell_number in editor_data['walls'][wall_type]:
                        editor_data['walls'][wall_type].remove(cell_number)
                    # Если стены нет - добавляем
                    else:
                        editor_data['walls'][wall_type].append(cell_number)
                    draw_editor_grid()
                    return

                # Получаем координаты с учетом отступа
                x = event.x - editor_data['offset_x']
                y = event.y - editor_data['offset_y']
                
                # Получаем индексы ячейки
                cell_x = int(x // editor_data['cell_size'])
                cell_y = int(y // editor_data['cell_size'])
                
                # Проверяем, что клик был внутри поля
                if (0 <= cell_x < editor_data['grid_size_n'] and 
                    0 <= cell_y < editor_data['grid_size_m']):
                    
                    cell_number = cell_y * editor_data['grid_size_n'] + cell_x + 1

                    # Левая кнопка мыши - управление ячейками для закраски
                    if event.num == 1:
                        if cell_number in editor_data['filled_cells']:
                            editor_data['filled_cells'].remove(cell_number)
                        else:
                            # Убираем конечную позицию, если она была в этой ячейке
                            if cell_number == editor_data['end_position']:
                                editor_data['end_position'] = None
                            editor_data['filled_cells'].append(cell_number)
                    
                    # Правая кнопка мыши - управление конечной позицией
                    elif event.num == 3:
                        if cell_number == editor_data['end_position']:
                            editor_data['end_position'] = None
                        else:
                            # Убираем ячейку из списка для закраски, если она там была
                            if cell_number in editor_data['filled_cells']:
                                editor_data['filled_cells'].remove(cell_number)
                            editor_data['end_position'] = cell_number

                    draw_editor_grid()
                    
            except Exception as e:
                print(f"Error in handle_click: {str(e)}")

        def start_drag(event):
            """Начало перетаскивания робота."""
            if "robot" in editor_canvas.gettags("current"):
                editor_data['drag_data'].update({
                    'x': event.x,
                    'y': event.y,
                    'dragging': True
                })

        def drag(event):
            """Перетаскивание робота."""
            if editor_data['drag_data']['dragging']:
                # Получаем координаты с учетом отступов
                x = event.x - editor_data['offset_x']
                y = event.y - editor_data['offset_y']
                
                # Вычисляем индексы ячейки
                cell_x = int(x // editor_data['cell_size'])
                cell_y = int(y // editor_data['cell_size'])
                
                # Проверяем границы поля
                if (0 <= cell_x < editor_data['grid_size_n'] and 
                    0 <= cell_y < editor_data['grid_size_m']):
                    
                    # Обновляем позицию робота
                    editor_data['robot_pos'] = [cell_x, cell_y]
                    
                    # Перерисовываем сетку для обновления всех элементов
                    draw_editor_grid()

        def stop_drag(event):
            """Окончание перетаскивания робота."""
            if editor_data['drag_data']['dragging']:
                # Получаем координаты с учетом отступов
                x = event.x - editor_data['offset_x']
                y = event.y - editor_data['offset_y']
                
                # Вычисляем индексы ячейки
                cell_x = int(x // editor_data['cell_size'])
                cell_y = int(y // editor_data['cell_size'])
                
                # Ограничиваем координаты границами поля
                cell_x = max(0, min(cell_x, editor_data['grid_size_n'] - 1))
                cell_y = max(0, min(cell_y, editor_data['grid_size_m'] - 1))
                
                # Обновляем позицию робота
                editor_data['robot_pos'] = [cell_x, cell_y]
                
                # Перерисовываем сетку для обновления всех элементов
                draw_editor_grid()
                editor_data['drag_data']['dragging'] = False

        def draw_editor_grid():
            """Отрисовывает сетку редактора."""
            try:
                # Очищаем canvas
                editor_canvas.delete("all")
                
                # Получаем размеры canvas
                canvas_width = editor_canvas.winfo_width()
                canvas_height = editor_canvas.winfo_height()
                
                # Вычисляем размер ячейки на основе размеров canvas и сетки
                cell_size_w = (canvas_width - 80) / editor_data['grid_size_n']
                cell_size_h = (canvas_height - 80) / editor_data['grid_size_m']
                editor_data['cell_size'] = min(cell_size_w, cell_size_h)
                
                # Вычисляем отступы для центрирования сетки
                total_grid_width = editor_data['cell_size'] * editor_data['grid_size_n']
                total_grid_height = editor_data['cell_size'] * editor_data['grid_size_m']
                editor_data['offset_x'] = (canvas_width - total_grid_width) / 2
                editor_data['offset_y'] = (canvas_height - total_grid_height) / 2

                # Рисуем цифры для столбцов (сверху)
                for j in range(editor_data['grid_size_n']):
                    x = j * editor_data['cell_size'] + editor_data['offset_x'] + editor_data['cell_size']/2
                    y = editor_data['offset_y'] - 20
                    editor_canvas.create_text(x, y, text=str(j+1), font=('Arial', 10))

                # Рисуем цифры для строк (слева)
                for i in range(editor_data['grid_size_m']):
                    x = editor_data['offset_x'] - 20
                    y = i * editor_data['cell_size'] + editor_data['offset_y'] + editor_data['cell_size']/2
                    editor_canvas.create_text(x, y, text=str(i+1), font=('Arial', 10))
                
                # Рисуем сетку
                for i in range(editor_data['grid_size_m']):
                    for j in range(editor_data['grid_size_n']):
                        x1 = j * editor_data['cell_size'] + editor_data['offset_x']
                        y1 = i * editor_data['cell_size'] + editor_data['offset_y']
                        x2 = x1 + editor_data['cell_size']
                        y2 = y1 + editor_data['cell_size']
                        
                        # Рисуем ячейку
                        editor_canvas.create_rectangle(
                            x1, y1, x2, y2,
                            outline="grey",
                            width=1
                        )
                        
                        # Если ячейка помечена для закраски, рисуем маленький зеленый квадрат по центру
                        cell_number = i * editor_data['grid_size_n'] + j + 1
                        if cell_number in editor_data['filled_cells']:
                            marker_size = editor_data['cell_size'] * 0.25  # Размер маркера - 25% от размера ячейки
                            marker_x = x1 + (editor_data['cell_size'] - marker_size) / 2
                            marker_y = y1 + (editor_data['cell_size'] - marker_size) / 2
                            editor_canvas.create_rectangle(
                                marker_x, marker_y,
                                marker_x + marker_size, marker_y + marker_size,
                                fill="green",
                                outline="green"
                            )

                # Рисуем внешнюю границу поля
                editor_canvas.create_rectangle(
                    editor_data['offset_x'],
                    editor_data['offset_y'],
                    editor_data['offset_x'] + editor_data['cell_size'] * editor_data['grid_size_n'],
                    editor_data['offset_y'] + editor_data['cell_size'] * editor_data['grid_size_m'],
                    outline="black",
                    width=2
                )
                
                # Рисуем стены
                for direction in editor_data['walls']:
                    for cell in editor_data['walls'][direction]:
                        x = (cell - 1) % editor_data['grid_size_n']
                        y = (cell - 1) // editor_data['grid_size_n']
                        
                        if direction == 'left':
                            editor_canvas.create_line(
                                x * editor_data['cell_size'] + editor_data['offset_x'],
                                y * editor_data['cell_size'] + editor_data['offset_y'],
                                x * editor_data['cell_size'] + editor_data['offset_x'],
                                (y + 1) * editor_data['cell_size'] + editor_data['offset_y'],
                                fill="black", width=3
                            )
                        elif direction == 'right':
                            editor_canvas.create_line(
                                (x + 1) * editor_data['cell_size'] + editor_data['offset_x'],
                                y * editor_data['cell_size'] + editor_data['offset_y'],
                                (x + 1) * editor_data['cell_size'] + editor_data['offset_x'],
                                (y + 1) * editor_data['cell_size'] + editor_data['offset_y'],
                                fill="black", width=3
                            )
                        elif direction == 'up':
                            editor_canvas.create_line(
                                x * editor_data['cell_size'] + editor_data['offset_x'],
                                y * editor_data['cell_size'] + editor_data['offset_y'],
                                (x + 1) * editor_data['cell_size'] + editor_data['offset_x'],
                                y * editor_data['cell_size'] + editor_data['offset_y'],
                                fill="black", width=3
                            )
                        elif direction == 'down':
                            editor_canvas.create_line(
                                x * editor_data['cell_size'] + editor_data['offset_x'],
                                (y + 1) * editor_data['cell_size'] + editor_data['offset_y'],
                                (x + 1) * editor_data['cell_size'] + editor_data['offset_x'],
                                (y + 1) * editor_data['cell_size'] + editor_data['offset_y'],
                                fill="black", width=3
                            )
                
                # Рисуем конечную позицию
                if editor_data['end_position']:
                    x = (editor_data['end_position'] - 1) % editor_data['grid_size_n']
                    y = (editor_data['end_position'] - 1) // editor_data['grid_size_n']
                    marker_size = editor_data['cell_size'] * 0.2
                    
                    editor_canvas.create_rectangle(
                        x * editor_data['cell_size'] + editor_data['offset_x'] + editor_data['cell_size']/2 - marker_size/2,
                        y * editor_data['cell_size'] + editor_data['offset_y'] + editor_data['cell_size']/2 - marker_size/2,
                        x * editor_data['cell_size'] + editor_data['offset_x'] + editor_data['cell_size']/2 + marker_size/2,
                        y * editor_data['cell_size'] + editor_data['offset_y'] + editor_data['cell_size']/2 + marker_size/2,
                        fill="black"
                    )
                
                # Рисуем робота
                if editor_data['robot_image']:
                    editor_canvas.create_image(
                        editor_data['robot_pos'][0] * editor_data['cell_size'] + editor_data['offset_x'] + editor_data['cell_size']/2,
                        editor_data['robot_pos'][1] * editor_data['cell_size'] + editor_data['offset_y'] + editor_data['cell_size']/2,
                        image=editor_data['robot_image'],
                        tags="robot"
                    )
                
            except Exception as e:
                print(f"Error in draw_editor_grid: {str(e)}")

        def calculate_cell_size():
            """Вычисляет оптимальный размер ячейки."""
            canvas_width = editor_canvas.winfo_width()
            canvas_height = editor_canvas.winfo_height()
            
            # Учитываем отступы и место для номеров строк/столбцов
            total_offset = editor_data['offset'] + 40
            available_width = canvas_width - 2 * total_offset
            available_height = canvas_height - 2 * total_offset
            
            # Вычисляем размер ячейки
            cell_width = available_width / editor_data['grid_size_n']
            cell_height = available_height / editor_data['grid_size_m']
            
            # Возвращаем минимальный размер для сохранения пропорций
            return min(cell_width, cell_height)

        def update_grid_size(dimension, value):
            """Обновляет размер сетки."""
            try:
                value = int(float(value))
                old_m = editor_data['grid_size_m']
                old_n = editor_data['grid_size_n']
                
                if dimension == 'rows':
                    editor_data['grid_size_m'] = value
                else:
                    editor_data['grid_size_n'] = value

                # Очищаем старые границы поля
                for direction in editor_data['walls']:
                    editor_data['walls'][direction] = [
                        cell for cell in editor_data['walls'][direction]
                        if (direction in ['left', 'right'] and cell % old_n != 1 and cell % old_n != 0) or
                        (direction in ['up', 'down'] and cell <= (old_m - 1) * old_n)
                    ]
                
                # Очищаем маркеры за пределами нового поля
                editor_data['filled_cells'] = [
                    cell for cell in editor_data['filled_cells']
                    if cell <= editor_data['grid_size_m'] * editor_data['grid_size_n']
                ]
                
                if editor_data['end_position'] and editor_data['end_position'] > editor_data['grid_size_m'] * editor_data['grid_size_n']:
                    editor_data['end_position'] = None
                
                # Проверяем позицию робота
                max_x = editor_data['grid_size_n'] - 1
                max_y = editor_data['grid_size_m'] - 1
                editor_data['robot_pos'][0] = min(editor_data['robot_pos'][0], max_x)
                editor_data['robot_pos'][1] = min(editor_data['robot_pos'][1], max_y)
                
                # Обновляем размер ячейки
                canvas_width = editor_canvas.winfo_width()
                canvas_height = editor_canvas.winfo_height()
                cell_size_w = (canvas_width - 80) / editor_data['grid_size_n']
                cell_size_h = (canvas_height - 80) / editor_data['grid_size_m']
                editor_data['cell_size'] = min(cell_size_w, cell_size_h)
                
                # Обновляем размер изображения робота
                if editor_data['robot_image']:
                    # Загружаем оригинальное изображение заново
                    try:
                        
                        robot_image_path = os.path.join(ICONS_DIR, 'robot.png')
                        original_image= tk.PhotoImage(file=robot_image_path)
                        # Вычисляем новый размер для робота (80% от размера ячейки)
                        scaled_size = int(editor_data['cell_size'] * 0.8)
                        # Вычисляем коэффициент масштабирования
                        scale_factor = max(1, int(original_image.width() / scaled_size))
                        # Создаем новое масштабированное изображение
                        editor_data['robot_image'] = original_image.subsample(scale_factor, scale_factor)
                    except Exception as e:
                        print(f"Error updating robot image: {str(e)}")
                
                # Перерисовываем сетку
                draw_editor_grid()
                
            except ValueError as e:
                print(f"Error in update_grid_size: {str(e)}")

        def on_window_resize(event):
            """Обработчик изменения размера окна."""
            if event.widget == editor_canvas:
                # Обновляем размер ячейки
                editor_data['cell_size'] = calculate_cell_size()
                
                # Обновляем размер изображения робота
                if editor_data['robot_image']:
                    scaled_size = int(editor_data['cell_size'] * 0.8)
                    editor_data['robot_image'] = editor_data['robot_image'].subsample(
                        max(1, int(editor_data['robot_image'].width() / scaled_size)),
                        max(1, int(editor_data['robot_image'].height() / scaled_size))
                    )
                
                # Перерисовываем сетку
                draw_editor_grid()

        # Обновляем привязки событий
        editor_canvas.bind("<Button-1>", handle_click)
        editor_canvas.bind("<B1-Motion>", drag)
        editor_canvas.bind("<ButtonRelease-1>", stop_drag)

        # Кнопки управления
        control_frame = ttk.Frame(editor_window)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(control_frame, text="Применить", 
                  command=lambda: self.apply_editor_changes(editor_data) or editor_window.destroy()).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Отмена", 
                  command=editor_window.destroy).pack(side=tk.LEFT, padx=5)

        # Ползунки для изменения размера поля
        grid_size_frame = ttk.Frame(editor_window)
        grid_size_frame.pack(fill=tk.X, padx=10, pady=5)

        # Фрейм для строк
        rows_frame = ttk.Frame(grid_size_frame)
        rows_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Label(rows_frame, text="Строки:").pack(side=tk.TOP)
        
        # Фрейм для шкалы и значений строк
        rows_scale_frame = ttk.Frame(rows_frame)
        rows_scale_frame.pack(fill=tk.X)
        
        rows_min_label = ttk.Label(rows_scale_frame, text="1")
        rows_min_label.pack(side=tk.LEFT)
        
        rows_value_label = ttk.Label(rows_scale_frame, text=str(editor_data['grid_size_m']))
        rows_value_label.pack(side=tk.TOP)
        
        def update_rows(value):
            rows_value_label.config(text=str(int(float(value))))
            update_grid_size('rows', value)
        
        rows_scale = ttk.Scale(rows_scale_frame, from_=1, to=20, orient=tk.HORIZONTAL, 
                              command=update_rows)
        rows_scale.set(editor_data['grid_size_m'])
        rows_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        rows_max_label = ttk.Label(rows_scale_frame, text="20")
        rows_max_label.pack(side=tk.LEFT)

        # Фрейм для столбцов
        cols_frame = ttk.Frame(grid_size_frame)
        cols_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Label(cols_frame, text="Столбцы:").pack(side=tk.TOP)
        
        # Фрейм для шкалы и значений столбцов
        cols_scale_frame = ttk.Frame(cols_frame)
        cols_scale_frame.pack(fill=tk.X)
        
        cols_min_label = ttk.Label(cols_scale_frame, text="1")
        cols_min_label.pack(side=tk.LEFT)
        
        cols_value_label = ttk.Label(cols_scale_frame, text=str(editor_data['grid_size_n']))
        cols_value_label.pack(side=tk.TOP)
        
        def update_cols(value):
            cols_value_label.config(text=str(int(float(value))))
            update_grid_size('cols', value)
        
        cols_scale = ttk.Scale(cols_scale_frame, from_=1, to=20, orient=tk.HORIZONTAL, 
                              command=update_cols)
        cols_scale.set(editor_data['grid_size_n'])
        cols_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        cols_max_label = ttk.Label(cols_scale_frame, text="20")
        cols_max_label.pack(side=tk.LEFT)

        # Отрисовываем начальное состояние
        draw_editor_grid()

        # Добавляем обработчик правой кнопки мыши
        editor_canvas.bind("<Button-3>", handle_click)

        # Привязки для изменения размера окна
        editor_window.bind("<Configure>", on_window_resize)
        editor_canvas.bind("<Configure>", on_window_resize)

    def apply_editor_changes(self, editor_data):
        """Применяет изменения из редактора окружения."""
        try:
            # Сохраняем идентификатор робота перед очисткой
            robot_id = self.robot.robot
            
            # Сохраняем текущие изменения
            self.grid_size_m = editor_data['grid_size_m']
            self.grid_size_n = editor_data['grid_size_n']
            
            # Обновляем размеры сетки для робота
            self.robot.grid_size_m = self.grid_size_m
            self.robot.grid_size_n = self.grid_size_n
            
            # Создаем глубокую копию словаря стен
            self.wall = {
                'left': editor_data['walls']['left'][:],
                'right': editor_data['walls']['right'][:],
                'up': editor_data['walls']['up'][:],
                'down': editor_data['walls']['down'][:]
            }
            self.cells_to_fill = editor_data['filled_cells'][:]
            
            # Обновляем позицию робота
            self.robot.pos_x, self.robot.pos_y = editor_data['robot_pos']
            self.robot.start_x = self.robot.pos_x
            self.robot.start_y = self.robot.pos_y
            self.robot.goto(self.robot.pos())
            self.end_position = editor_data['end_position']
            
            # Удаляем все элементы с canvas, кроме робота
            for item in self.canvas.find_all():
                if item != robot_id:
                    self.canvas.delete(item)
            
            # Перерисовываем элементы в правильном порядке
            self.create_grid()
            self.draw_walls()
            self.draw_cells_to_fill()
            self.draw_end_position_marker()
            
            # Обновляем изображение и положение робота
            self.robot.update_image(self.cell_size)
            self.canvas.coords(
                self.robot.robot,
                self.robot._calculate_screen_x(),
                self.robot._calculate_screen_y()
            )
            
            # Убеждаемся, что робот видим и находится поверх других элементов
            self.canvas.itemconfig(self.robot.robot, state='normal')
            self.canvas.tag_raise(self.robot.robot)
            
            # Сохраняем окружение в память
            self.save_environment_to_memory()
            
            # Устанавливаем тип задания как пользовательское
            self.current_task_type = "custom"
            self.current_task_num = 1
            
            # Обновляем статус
            self.task_status_label.config(text="Статус: Пользовательское окружение", fg="blue")
            
            # Принудительно обновляем canvas
            self.canvas.update()
            
        except Exception as e:
            print(f"Error in apply_editor_changes: {str(e)}")
            messagebox.showerror("Ошибка", f"Ошибка при применении изменений: {str(e)}")

    def close_current_tab(self):
        """Закрывает текущую вкладку."""
        current_tab = self.notebook.select()
        if current_tab:
            if len(self.notebook.tabs()) > 1:  # Проверяем, что это не последняя вкладка
                self.notebook.forget(current_tab)
            else:
                messagebox.showwarning("Warning", "Cannot close the last tab.")

    def on_text_change(self, event=None):
        """Обработчик изменения текста."""
        try:
            text_widget = event.widget
            if not text_widget:
                return

            # Добавляем подсветку функций при каждом изменении текста
            self.highlight_functions(text_widget)

            # Получаем текущую позицию курсора
            cursor_pos = text_widget.index(tk.INSERT)
            bbox = text_widget.bbox(cursor_pos)
            
            if not bbox:
                self.suggestion_box.place_forget()
                return

            # Получаем текущую строку
            current_line = text_widget.get("insert linestart", "insert")
            
            # Проверяем, нужно ли показывать подсказки
            matching_functions = [f for f in self.available_functions 
                                if f.startswith(current_line.strip())]
            
            if matching_functions and current_line.strip():
                # Очищаем и обновляем список подсказок
                self.suggestion_box.delete(0, tk.END)
                for func in matching_functions:
                    self.suggestion_box.insert(tk.END, func)
                
                # Позиционируем окно подсказок прямо под текущей строкой
                x = text_widget.winfo_x() + bbox[0]
                y = text_widget.winfo_y() + bbox[1] + bbox[3]
                
                # Преобразуем координаты относительно главного окна
                x = text_widget.winfo_rootx() - self.root.winfo_rootx() + bbox[0]
                y = text_widget.winfo_rooty() - self.root.winfo_rooty() + bbox[1] + bbox[3]
                
                self.suggestion_box.place(x=x, y=y)
            else:
                self.suggestion_box.place_forget()
            
        except Exception as e:
            print(f"Error in on_text_change: {str(e)}")

    def get_active_code_input(self):
        """Получает текущий активный текстовый виджет."""
        current_tab = self.notebook.select()
        if current_tab:
            return self.notebook.nametowidget(current_tab).winfo_children()[0]
        return None

    def handle_suggestion_click(self, event):
        """Обработчик клика по подсказке."""
        self.insert_suggestion(None)

    def handle_suggestion_hover(self, event):
        """Обработчик наведения на подсказку."""
        index = self.suggestion_box.nearest(event.y)
        self.suggestion_box.selection_clear(0, tk.END)
        self.suggestion_box.selection_set(index)

    def insert_suggestion(self, event):
        """Вставляет выбранную подсказку."""
        if self.suggestion_box.winfo_viewable():
            code_input = self.get_active_code_input()
            selection = self.suggestion_box.get(self.suggestion_box.curselection())
            if selection:
                # Удаляем текущее слово
                text = code_input.get("insert linestart", "insert")
                words = text.split()
                if words:
                    current_word = words[-1]
                    code_input.delete("insert-%dc" % len(current_word), "insert")
                
                # Вставляем выбранную подсказку
                code_input.insert("insert", selection)
                
                # Сразу применяем подсветку
                self.highlight_functions(code_input)
                
                self.hide_suggestions()
            return 'break'  # Предотвращаем стандартное поведение Tab

    def show_suggestions(self, event):
        """Показывает подсказки для автодополнения."""
        code_input = event.widget
        text = code_input.get("insert linestart", "insert")
        words = text.split()
        
        if words:
            current_word = words[-1]
            suggestions = [f for f in self.available_functions if f.startswith(current_word)]
            
            if suggestions:
                self.suggestion_box.delete(0, tk.END)
                for suggestion in suggestions:
                    self.suggestion_box.insert(tk.END, suggestion)
                
                # Позиционируем окно подсказок
                x, y, _, _ = code_input.bbox("insert")
                x = x + code_input.winfo_rootx()
                y = y + code_input.winfo_rooty() + 20
                
                self.suggestion_box.place(x=x, y=y)
                self.suggestion_box.selection_set(0)
                return
        
        self.hide_suggestions()

    def hide_suggestions(self, event=None):
        """Скрывает окно подсказок."""
        self.suggestion_box.place_forget()

    def show_environment_window(self):
        """Создает или показывает окно с результатом выполнения задания."""
        # Если окно уже существует, закрываем его
        if hasattr(self, 'env_window') and self.env_window.winfo_exists():
            self.env_window.destroy()

        # Создаем новое окно
        self.env_window = tk.Toplevel(self.root)
        self.env_window.title("Результат выполнения задания")
        
        # Создаем canvas для отображения окружения
        self.env_canvas = tk.Canvas(self.env_window, bg='white')
        self.env_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Позиционируем окно справа от основного окна и на том же уровне по вертикали
        main_window_x = self.root.winfo_x()
        main_window_y = self.root.winfo_y()
        main_window_height = self.root.winfo_height()
        
        # Вычисляем позицию для окна результата
        result_window_x = main_window_x + self.root.winfo_width() + 10  # 10 пикселей отступ между окнами
        result_window_y = main_window_y + (main_window_height - 300) // 2  # Центрируем по вертикали
        
        self.env_window.geometry(f"300x300+{result_window_x}+{result_window_y}")

        # Устанавливаем минимальный размер окна
        self.env_window.minsize(200, 200)

        # Копируем параметры из основного окна
        self.env_cell_size = self.cell_size
        self.env_offset = self.offset

        def update_environment():
            if self.env_window.winfo_exists():
                if self.end_position is None:
                    self.hide_environment_window()
                    return
                
                self.env_canvas.delete("all")
                
                # Рисуем сетку
                for i in range(self.grid_size_m):
                    for j in range(self.grid_size_n):
                        self.env_canvas.create_rectangle(
                            j * self.env_cell_size + self.env_offset,
                            i * self.env_cell_size + self.env_offset,
                            (j + 1) * self.env_cell_size + self.env_offset,
                            (i + 1) * self.env_cell_size + self.env_offset,
                            outline="grey",
                            width=1
                        )

                # Рисуем стены
                for direction, cells in self.wall.items():
                    for cell in cells:
                        x = (cell - 1) % self.grid_size_n
                        y = (cell - 1) // self.grid_size_n
                        if direction == 'left':
                            self.env_canvas.create_line(
                                x * self.env_cell_size + self.env_offset,
                                y * self.env_cell_size + self.env_offset,
                                x * self.env_cell_size + self.env_offset,
                                (y + 1) * self.env_cell_size + self.env_offset,
                                fill="black", width=3
                            )
                        elif direction == 'right':
                            self.env_canvas.create_line(
                                (x + 1) * self.env_cell_size + self.env_offset,
                                y * self.env_cell_size + self.env_offset,
                                (x + 1) * self.env_cell_size + self.env_offset,
                                (y + 1) * self.env_cell_size + self.env_offset,
                                fill="black", width=3
                            )
                        elif direction == 'up':
                            self.env_canvas.create_line(
                                x * self.env_cell_size + self.env_offset,
                                y * self.env_cell_size + self.env_offset,
                                (x + 1) * self.env_cell_size + self.env_offset,
                                y * self.env_cell_size + self.env_offset,
                                fill="black", width=3
                            )
                        elif direction == 'down':
                            self.env_canvas.create_line(
                                x * self.env_cell_size + self.env_offset,
                                (y + 1) * self.env_cell_size + self.env_offset,
                                (x + 1) * self.env_cell_size + self.env_offset,
                                (y + 1) * self.env_cell_size + self.env_offset,
                                fill="black", width=3
                            )

                # Рисуем все клетки, которые должны быть закрашены, как закрашенные
                for cell in self.cells_to_fill:
                    x = (cell - 1) % self.grid_size_n
                    y = (cell - 1) // self.grid_size_n
                    self.env_canvas.create_rectangle(
                        x * self.env_cell_size + self.env_offset,
                        y * self.env_cell_size + self.env_offset,
                        (x + 1) * self.env_cell_size + self.env_offset,
                        (y + 1) * self.env_cell_size + self.env_offset,
                        fill="lightgreen"
                    )

                # Рисуем робота в конечной позиции
                if self.end_position:
                    x = (self.end_position - 1) % self.grid_size_n
                    y = (self.end_position - 1) // self.grid_size_n
                    try:
                        robot_image_path = os.path.join(ICONS_DIR, 'robot.png')
                        robot_image = tk.PhotoImage(file=robot_image_path)
                        scaled_size = int(self.env_cell_size * 0.8)
                        robot_image = robot_image.subsample(
                            max(1, int(robot_image.width() / scaled_size)),
                            max(1, int(robot_image.height() / scaled_size))
                        )
                        self.env_canvas.create_image(
                            x * self.env_cell_size + self.env_offset + self.env_cell_size/2,
                            y * self.env_cell_size + self.env_offset + self.env_cell_size/2,
                            image=robot_image
                        )
                        self.env_robot_image = robot_image
                    except Exception as e:
                        print(f"Error updating robot image: {e}")
                        robot_size = self.env_cell_size * 0.4
                        self.env_canvas.create_oval(
                            x * self.env_cell_size + self.env_offset + self.env_cell_size/2 - robot_size,
                            y * self.env_cell_size + self.env_offset + self.env_cell_size/2 - robot_size,
                            x * self.env_cell_size + self.env_offset + self.env_cell_size/2 + robot_size,
                            y * self.env_cell_size + self.env_offset + self.env_cell_size/2 + robot_size,
                            fill="blue"
                        )

                # Планируем следующее обновление
                self.env_window.after(100, update_environment)

        # Запускаем обновление окружения
        update_environment()

        # Обработчик изменения размера окна
        def on_resize(event):
            width = self.env_canvas.winfo_width()
            height = self.env_canvas.winfo_height()
            cell_size_w = (width - 2 * self.env_offset) / self.grid_size_n
            cell_size_h = (height - 2 * self.env_offset) / self.grid_size_m
            self.env_cell_size = min(cell_size_w, cell_size_h)
            
            # Сохраняем ссылку на масштабированное изображение
            if not hasattr(self, 'env_scaled_robot_image'):
                self.env_scaled_robot_image = None
            
            try:
                robot_image_path = os.path.join(ICONS_DIR, 'robot.png')
                original_image = tk.PhotoImage(file=robot_image_path)
                scaled_size = int(self.env_cell_size * 0.8)
                self.env_scaled_robot_image = original_image.subsample(
                    max(1, int(original_image.width() / scaled_size)),
                    max(1, int(original_image.height() / scaled_size))
                )
            except Exception as e:
                print(f"Error scaling robot image: {e}")
                self.env_scaled_robot_image = None

        # Привязываем обработчик изменения размера
        self.env_canvas.bind('<Configure>', on_resize)

    def hide_environment_window(self):
        """Скрывает окно окружения."""
        if hasattr(self, 'env_window') and self.env_window.winfo_exists():
            self.env_window.withdraw()

    def check_task_completion(self):
        """Проверяет выполнение задания."""
        if not self.end_position:
            return False
            
        # Проверяем, находится ли робот в конечной позиции
        robot_in_end_position = self.robot.pos() == self.end_position
        
        # Проверяем, все ли нужные клетки закрашены
        all_cells_filled = all(cell in self.filled_cells for cell in self.cells_to_fill)
        
        return robot_in_end_position and all_cells_filled

    def on_key_press(self, event):
        """Обработчик нажатия клавиш."""
        try:
            widget = event.widget
            # Создаем точку отмены после каждого символа
            widget.after(1, lambda: widget.edit_separator())
        except Exception as e:
            print(f"Error in on_key_press: {str(e)}")

    def on_key_release(self, event):
        """Обработчик отпускания клавиш."""
        try:
            text_widget = event.widget
            if not isinstance(text_widget, tk.Text):
                return
            
            # Получаем текущую позицию курсора
            cursor_pos = text_widget.index(tk.INSERT)
            line_start = cursor_pos.split('.')[0] + '.0'
            
            # Получаем текущую строку до курсора
            current_line = text_widget.get(line_start, cursor_pos)
            
            # Получаем последнее слово, разбивая по пробелу
            if ' ' in current_line:
                last_word = current_line.split(' ')[-1]
            else:
                last_word = current_line
                
            # Очищаем слово от лишних пробелов
            last_word = last_word.strip()
            
            if last_word:
                # Проверяем, является ли последнее слово полной функцией
                if any(last_word == f + "()" for f in self.available_functions):
                    self.suggestion_box.place_forget()
                    return
                
                # Убираем возможные скобки для проверки на частичное совпадение
                base_word = last_word.rstrip('()')
                suggestions = [f for f in self.available_functions if f.startswith(base_word)]
                
                if suggestions:
                    bbox = text_widget.bbox(cursor_pos)
                    if bbox:
                        x, y, _, height = bbox
                        x = x + text_widget.winfo_rootx()
                        y = y + text_widget.winfo_rooty() + height
                        
                        self.suggestion_box.delete(0, tk.END)
                        for suggestion in suggestions:
                            self.suggestion_box.insert(tk.END, suggestion)
                        
                        self.suggestion_box.place(x=x, y=y)
                else:
                    self.suggestion_box.place_forget()
            else:
                self.suggestion_box.place_forget()
                
        except Exception as e:
            print(f"Error in on_key_release: {str(e)}")

    def on_paste(self, event):
        """Обработчик вставки текста."""
        try:
            widget = event.widget
            widget.edit_separator()  # Точка отмены перед вставкой
            widget.after(1, lambda: widget.edit_separator())  # Точка отмены после вставки
        except Exception as e:
            print(f"Error in on_paste: {str(e)}")

    def update_speed(self, value):
        """Обновляет значение sleep_time на основе положения ползунка."""
        try:
            speed = float(value)
            if speed <= 1:
                self.sleep_time = 2.0  # Очень медленно (не меняем)
            elif speed >= 100:
                self.sleep_time = 0.01  # Очень быстро (не меняем)
            else:
                # Экспоненциальное изменение скорости
                self.sleep_time = 2.0 * (100 - speed) / 100
        except (ValueError, ZeroDivisionError):
            self.sleep_time = 0.2  # Значение по умолчанию

    def create_control_panel(self):
        """Создает панель управления."""
        control_frame = tk.Frame(self.canvas_container)
        control_frame.grid(row=2, column=0, sticky="ew", pady=5)

        # Создаем кнопки управления
        btn_up = tk.Button(control_frame, text="↑", width=3, command=self.control_up)
        btn_down = tk.Button(control_frame, text="↓", width=3, command=self.control_down)
        btn_left = tk.Button(control_frame, text="←", width=3, command=self.control_left)
        btn_right = tk.Button(control_frame, text="→", width=3, command=self.control_right)

        # Размещаем кнопки
        btn_up.grid(row=0, column=1, pady=2)
        btn_left.grid(row=1, column=0, padx=2)
        btn_down.grid(row=1, column=1)
        btn_right.grid(row=1, column=2, padx=2)

    def control_up(self):
        """Обработчик нажатия кнопки вверх."""
        if not self.robot.is_moving:
            self.running = True
            self.robot.up()

    def control_down(self):
        """Обработчик нажатия кнопки вниз."""
        if not self.robot.is_moving:
            self.running = True
            self.robot.down()

    def control_left(self):
        """Обработчик нажатия кнопки влево."""
        if not self.robot.is_moving:
            self.running = True
            self.robot.left()

    def control_right(self):
        """Обработчик нажатия кнопки вправо."""
        if not self.robot.is_moving:
            self.running = True
            self.robot.right()

    

    def highlight_syntax(self, event=None):
        """Подсветка синтаксиса в текстовом редакторе."""
        # Получаем текущий текстовый виджет
        text_widget = event.widget if event else self.get_current_text_widget()
        if not text_widget:
            return

        # Сохраняем текущую позицию курсора
        cursor_pos = text_widget.index(tk.INSERT)

        # Список функций робота
        robot_functions = ['left', 'right', 'up', 'down', 'move', 
                          'fillcell', 'pos', 'goto', 'start_pos']

        # Получаем текущую строку
        current_line = text_widget.get("insert linestart", "insert lineend")
        line_number = str(text_widget.index(tk.INSERT)).split('.')[0]

        # Удаляем подсветку только для текущей строки
        text_widget.tag_remove('function', f"{line_number}.0", f"{line_number}.end")

        # Проверяем каждую функцию в текущей строке
        for func in robot_functions:
            start_idx = 0
            while True:
                idx = current_line.find(func, start_idx)
                if idx == -1:
                    break

                # Проверяем, что после функции идут скобки
                after_func = current_line[idx + len(func):].lstrip()
                if after_func.startswith('('):
                    # Добавляем подсветку
                    start = f"{line_number}.{idx}"
                    end = f"{line_number}.{idx + len(func)}"
                    text_widget.tag_add('function', start, end)

                start_idx = idx + 1

        # Восстанавливаем позицию курсора
        text_widget.mark_set(tk.INSERT, cursor_pos)

    def create_new_tab(self):
        """Создает новую вкладку с текстовым редактором."""
        frame = tk.Frame(self.notebook)
        code_input = tk.Text(frame, wrap=tk.WORD)
        code_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Настраиваем тег для функций
        code_input.tag_configure('function', foreground='blue')
        
        # Добавляем тег для подсветки ошибок
        code_input.tag_configure("error", background="pink", foreground="red")
        
        # Привязываем обработчики событий
        code_input.bind('<Key>', self.on_key_event)
        code_input.bind('<KeyRelease>', self.on_key_event)
        code_input.bind('<Tab>', self.handle_tab)
        
        # Добавляем вкладку
        self.notebook.add(frame, text=f"Notepad {len(self.notebook.tabs()) + 1}")
        self.notebook.select(frame)
        
        return code_input

    def on_key_event(self, event):
        """Обработчик событий клавиатуры."""
        if not hasattr(self, 'robot_functions'):
            self.robot_functions = ['left', 'right', 'up', 'down', 'move', 
                                  'fillcell', 'pos', 'goto', 'start_pos']
        
        text_widget = event.widget
        
        # Получаем текущую строку
        current_line = text_widget.get("insert linestart", "insert lineend")
        line_number = text_widget.index(tk.INSERT).split('.')[0]
        
        # Удаляем старую подсветку в текущей строке
        text_widget.tag_remove('function', f"{line_number}.0", f"{line_number}.end")
        
        # Проверяем каждую функцию
        for func in self.robot_functions:
            start = 0
            while True:
                pos = current_line.find(func, start)
                if pos == -1:
                    break
                
                # Проверяем, есть ли скобка после функции
                after_func = current_line[pos + len(func):].lstrip()
                if after_func.startswith('('):
                    # Добавляем подсветку
                    text_widget.tag_add('function', 
                                      f"{line_number}.{pos}", 
                                      f"{line_number}.{pos + len(func)}")
                start = pos + 1

    def handle_tab(self, event):
        """Обработчик нажатия Tab."""
        text_widget = event.widget
        
        # Получаем текущее слово
        current_pos = text_widget.index(tk.INSERT)
        line_start = current_pos.split('.')[0] + '.0'
        current_line = text_widget.get(line_start, current_pos)
        word = current_line.split()[-1] if current_line.split() else ''
        
        # Если слово является началом функции робота
        matches = [func for func in self.robot_functions if func.startswith(word)]
        if matches:
            # Удаляем текущее слово
            text_widget.delete(f"{current_pos} - {len(word)}c", current_pos)
            # Вставляем полное имя функции
            text_widget.insert(tk.INSERT, matches[0] + '()')
            # Добавляем подсветку
            text_widget.tag_add('function',
                              f"{current_pos} - {len(word)}c",
                              f"{current_pos} + {len(matches[0])}c")
            # Перемещаем курсор между скобками
            text_widget.mark_set(tk.INSERT, f"{current_pos} + {len(matches[0]) + 1}c")
            return 'break'
        return None

    def check_text_changes(self, text_widget):
        """Проверяет изменения в тексте и обновляет подсветку."""
        try:
            current_content = text_widget.get('1.0', 'end-1c')
            
            # Если содержимое изменилось
            if not hasattr(text_widget, 'last_content') or current_content != text_widget.last_content:
                text_widget.last_content = current_content
                self.update_highlighting(text_widget)
                
            # Планируем следующую проверку
            text_widget.trace_id = text_widget.after(100, lambda: self.check_text_changes(text_widget))
        except Exception as e:
            print(f"Error in check_text_changes: {str(e)}")

    def update_highlighting(self, text_widget):
        """Обновляет подсветку синтаксиса."""
        try:
            # Удаляем старую подсветку
            text_widget.tag_remove('function', '1.0', 'end')
            
            # Получаем текст
            content = text_widget.get('1.0', 'end-1c')
            
            # Список функций робота
            robot_functions = ['left', 'right', 'up', 'down', 'move', 
                             'fillcell', 'pos', 'goto', 'start_pos']
            
            # Создаем шаблон регулярного выражения для поиска функций
            pattern = '|'.join(r'\b' + re.escape(func) + r'\s*\(' for func in robot_functions)
            
            # Ищем все совпадения
            for match in re.finditer(pattern, content):
                start_idx = match.start()
                # Находим конец имени функции (до пробела или скобки)
                end_idx = start_idx
                while end_idx < len(content) and content[end_idx] not in [' ', '(']:
                    end_idx += 1
                    
                # Преобразуем индексы в формат Tkinter
                start_line = content.count('\n', 0, start_idx) + 1
                start_char = start_idx - content.rfind('\n', 0, start_idx) - 1
                if start_char < 0:
                    start_char = start_idx
                    
                end_line = content.count('\n', 0, end_idx) + 1
                end_char = end_idx - content.rfind('\n', 0, end_idx) - 1
                if end_char < 0:
                    end_char = end_idx
                    
                # Добавляем тег подсветки
                text_widget.tag_add('function', 
                                  f'{start_line}.{start_char}', 
                                  f'{end_line}.{end_char}')
                
        except Exception as e:
            print(f"Error in update_highlighting: {str(e)}")

    def on_modified(self, event):
        """Обработчик изменения текста."""
        widget = event.widget
        if widget:
            widget.edit_modified(False)  # Сбрасываем флаг модификации
            self.schedule_highlight(event)

    def clear_filled_cells_visual(self):
        """Очищает визуальное отображение закрашенных клеток."""
        for cell in range(1, self.grid_size_m * self.grid_size_n + 1):
            x = (cell - 1) % self.grid_size_n
            y = (cell - 1) // self.grid_size_n
            self.canvas.create_rectangle(
                x * self.cell_size + self.offset,
                y * self.cell_size + self.offset,
                (x + 1) * self.cell_size + self.offset,
                (y + 1) * self.cell_size + self.offset,
                fill="white",
                outline="grey",
                width=1
            )

    def reset_current_task(self):
        """Полностью сбрасывает поле к начальным настройкам."""
        try:
            # Сбрасываем размер поля к стандартному
            self.grid_size_m = 5
            self.grid_size_n = 5
            self.robot.grid_size_m = 5
            self.robot.grid_size_n = 5

            # Сбрасываем позицию робота
            self.robot.x = 0
            self.robot.y = 0
            self.robot.pos_x = 0
            self.robot.pos_y = 0
            if hasattr(self.robot, 'start_x'):
                delattr(self.robot, 'start_x')
            if hasattr(self.robot, 'start_y'):
                delattr(self.robot, 'start_y')

            # Очищаем все состояния
            self.filled_cells = []
            self.cells_to_fill = []
            self.wall = {'up': [], 'down': [], 'left': [], 'right': []}
            self.end_position = None
            
            # Сбрасываем текущее задание
            self.current_task_type = None
            self.current_task_num = None
            self.program_running = False
            self.running = False
            

            # Очищаем canvas
            for item in self.canvas.find_all():
                if item != self.robot.robot:
                    self.canvas.delete(item)

            # Перерисовываем базовую сетку
            self.create_grid()

            # Обновляем робота
            self.robot.update_image(self.cell_size)
            self.robot.update_position(0, 0)
            self.canvas.tag_raise(self.robot.robot)

            # Очищаем сообщение об ошибке
            self.task_message_label.config(text="")

            # Обновляем статус без проверки атрибутов
            self.task_status_label.config(text="Статус: Поле сброшено", fg="black")
            self.selected_task_label.config(text="Selected Task: None")

            # Обновляем canvas
            self.canvas.update()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сбросе поля: {str(e)}")

    def draw_environment_grid(self):
        """Отрисовка сетки в окне результата."""
        try:
            # Получаем размеры canvas
            canvas_width = self.env_canvas.winfo_width()
            canvas_height = self.env_canvas.winfo_height()
            
            # Вычисляем размер ячейки
            cell_size = min((canvas_width - 20) / self.grid_size_n, 
                           (canvas_height - 20) / self.grid_size_m)
            
            # Вычисляем отступы для центрирования сетки
            offset_x = (canvas_width - cell_size * self.grid_size_n) / 2
            offset_y = (canvas_height - cell_size * self.grid_size_m) / 2
            
            # Рисуем заполненные клетки
            for i in range(self.grid_size_m):
                for j in range(self.grid_size_n):
                    cell_number = i * self.grid_size_n + j + 1
                    x1 = offset_x + j * cell_size
                    y1 = offset_y + i * cell_size
                    x2 = x1 + cell_size
                    y2 = y1 + cell_size
                    
                    # Рисуем базовую клетку
                    self.env_canvas.create_rectangle(x1, y1, x2, y2, outline='black')
                    
                    # Если клетка закрашена
                    if cell_number in self.filled_cells:
                        self.env_canvas.create_rectangle(x1, y1, x2, y2, fill='green')
                    
                    # Если это конечная позиция и клетка для закраски
                    if cell_number == self.end_position and cell_number in self.cells_to_fill:
                        # Рисуем прямоугольник, разделенный по диагонали
                        self.env_canvas.create_polygon(
                            x1, y1,  # Верхний левый
                            x2, y1,  # Верхний правый
                            x2, y2,  # Нижний правый
                            fill='green'
                        )
                        self.env_canvas.create_polygon(
                            x1, y1,  # Верхний левый
                            x1, y2,  # Нижний левый
                            x2, y2,  # Нижний правый
                            fill='black'
                        )
                    # Если это только конечная позиция
                    elif cell_number == self.end_position:
                        self.env_canvas.create_rectangle(x1, y1, x2, y2, fill='black')
                    # Если это только клетка для закраски
                    elif cell_number in self.cells_to_fill:
                        self.env_canvas.create_rectangle(x1, y1, x2, y2, fill='green')
            
            # Рисуем сетку поверх заполненных клеток
            for i in range(self.grid_size_m + 1):
                y = offset_y + i * cell_size
                self.env_canvas.create_line(
                    offset_x, y,
                    offset_x + self.grid_size_n * cell_size, y,
                    fill='black'
                )
            
            for j in range(self.grid_size_n + 1):
                x = offset_x + j * cell_size
                self.env_canvas.create_line(
                    x, offset_y,
                    x, offset_y + self.grid_size_m * cell_size,
                    fill='black'
                )
                
        except Exception as e:
            print(f"Error in draw_environment_grid: {str(e)}")

    def load_task(self, task_type, task_num):
        """Загружает задание указанного типа и номера."""
        try:
            # Сбрасываем текущее состояние
            self.clear_task()
            
            # Обновляем метки
            if task_type == "for":  # Изменено с "circle" на "for"
                task_name = f"For {task_num}"  # Изменено с "Circle" на "For"
            else:
                task_name = f"{task_type.capitalize()} {task_num}"
            
            self.selected_task_label.config(text=f"Selected Task: {task_name}")
            self.task_status_label.config(text=f"Статус: Загружено задание {task_name}", fg="blue")
            
            # Загружаем конфигурацию задания
            if task_type == "for":  # Изменено с "circle" на "for"
                self.load_circle_task(task_num)  # Имя метода можно оставить прежним
            elif task_type == "if":
                self.load_if_task(task_num)
            elif task_type == "while":
                self.load_while_task(task_num)
            
            self.current_task_type = task_type
            self.current_task_num = task_num
            
            # Обновляем canvas
            self.canvas.update()
            
        except Exception as e:
            print(f"Error in load_task: {str(e)}")
            messagebox.showerror("Ошибка", f"Ошибка при загрузке задания: {str(e)}")

    def create_menu(self):
        """Создает меню приложения."""
        try:
            menubar = tk.Menu(self.root)
            self.root.config(menu=menubar)
            
            # Меню "Файл"
            file_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Файл", menu=file_menu)
            file_menu.add_command(label="Новая вкладка", command=self.create_new_tab)
            file_menu.add_command(label="Закрыть вкладку", command=self.close_current_tab)
            file_menu.add_separator()
            file_menu.add_command(label="Сохранить", command=self.save_file)
            file_menu.add_command(label="Открыть", command=self.open_file)
            file_menu.add_separator()
            file_menu.add_command(label="Выход", command=self.root.quit)
            
            # Меню "Задания"
            tasks_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Задания", menu=tasks_menu)
            
            # Подменю для каждого типа заданий
            for_menu = tk.Menu(tasks_menu, tearoff=0)  # Изменено с circle_menu на for_menu
            if_menu = tk.Menu(tasks_menu, tearoff=0)
            while_menu = tk.Menu(tasks_menu, tearoff=0)
            
            tasks_menu.add_cascade(label="For", menu=for_menu)  # Изменено с "Circle" на "For"
            tasks_menu.add_cascade(label="If", menu=if_menu)
            tasks_menu.add_cascade(label="While", menu=while_menu)
            
            # Добавляем задания в подменю
            for i in range(1, 11):
                for_menu.add_command(  # Изменено с circle_menu на for_menu
                    label=f"For {i}",  # Изменено с "Circle" на "For"
                    command=lambda x=i: self.load_task("for", x)  # Изменено с "circle" на "for"
                )
                if_menu.add_command(
                    label=f"If {i}",
                    command=lambda x=i: self.load_task("if", x)
                )
                while_menu.add_command(
                    label=f"While {i}",
                    command=lambda x=i: self.load_task("while", x)
                )
            
            # Меню "Инструменты"
            tools_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Инструменты", menu=tools_menu)
            tools_menu.add_command(label="Редактор окружения", command=self.open_environment_editor)
            tools_menu.add_command(label="Выбрать размер шрифта", command=self.choose_font_size)
            tools_menu.add_command(label="Справка", command=self.show_help)
            tools_menu.add_separator()
            tools_menu.add_command(label="Сохранить окружение", command=self.save_environment_to_file)
            tools_menu.add_command(label="Загрузить окружение", command=self.load_environment_from_file)
            tools_menu.add_command(label="Сбросить задание", command=self.reset_current_task)
            
        except Exception as e:
            print(f"Error in create_menu: {str(e)}")
            messagebox.showerror("Ошибка", f"Ошибка при создании меню: {str(e)}")

def start():
    root = tk.Tk()
    app = RobotApp(root)
    root.mainloop()

if __name__ == "__main__":
    start()
