import tkinter as tk
import math

# --- 1. Cấu hình Màu sắc và Kích thước ---
COLOR = {
    "WINDOW_BG": "#282c34",  # Nền cửa sổ (Xám đen)
    "DISPLAY_BG": "#ecf0f1",  # Nền màn hình hiển thị (Trắng xám nhạt - Giả LCD)
    "DISPLAY_FG": "#282c34",  # Màu chữ trên màn hình (Đen đậm)

    "NUMBER_BTN_BG": "#3a4049",  # Nút số (Xám đen vừa)
    "FUNC_BTN_BG": "#52637a",  # Nút Hàm Khoa học (Xanh xám)
    "OP_BTN_BG": "#ff9800",  # Nút Toán tử Cơ bản (Cam)

    "AC_BTN_BG": "#e53935",  # Nút AC (Đỏ)
    "EQUAL_BTN_BG": "#4caf50",  # Nút "=" (Xanh lá cây đậm)
    "TEXT_FG": "#FFFFFF",  # Màu chữ chung (Trắng)

    "HISTORY_BG": "#1e2126",  # Nền Khung Lịch sử (Đen nhạt hơn)
    "HISTORY_FG": "#abb2bf",  # Màu chữ Lịch sử (Xám sáng)
    "HISTORY_TOGGLE_BTN": "#3c4046"  # Màu nút mở lịch sử
}

FONT_SIZE = 16
FONT_STYLE = ('Helvetica', FONT_SIZE, 'bold')


# --- 2. Logic Xử lý Máy tính (Calculator Logic) ---

class Calculator:
    def __init__(self, master):
        self.master = master
        master.title("Casio FX-Python - Máy Tính Khoa Học")
        master.config(bg=COLOR["WINDOW_BG"])

        self.history_visible = False
        self.expression = ""
        self.display_text = tk.StringVar()
        self.display_text.set("0")
        self.mode = "DEG"
        self.mode_label = tk.StringVar(value=self.mode)
        self.history = []

        # Khung Máy tính và Lịch sử
        self.calc_frame = tk.Frame(master, bg=COLOR["WINDOW_BG"])
        self.history_frame = tk.Frame(master, bg=COLOR["HISTORY_BG"])

        self.calc_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

        self.create_calc_widgets()
        self.create_history_widgets()
        self.bind_keys()

    def create_calc_widgets(self):
        # Màn hình hiển thị Chế độ (DEG/RAD)
        mode_indicator = tk.Label(
            self.calc_frame,
            textvariable=self.mode_label,
            bg=COLOR["DISPLAY_BG"],
            fg=COLOR["DISPLAY_FG"],
            anchor='w',
            font=('Arial', 10, 'bold'),
            padx=10
        )
        mode_indicator.grid(row=0, column=0, columnspan=5, sticky='new', padx=5, pady=(5, 0))

        # Màn hình hiển thị Kết quả
        display = tk.Label(
            self.calc_frame,
            textvariable=self.display_text,
            bg=COLOR["DISPLAY_BG"],
            fg=COLOR["DISPLAY_FG"],
            anchor='e',
            font=('Arial', 30, 'bold'),
            padx=10,
            pady=10,
            borderwidth=5,
            relief='groove'
        )
        display.grid(row=1, column=0, columnspan=5, sticky='nsew', padx=5, pady=(0, 5))

        for i in range(5):
            self.calc_frame.grid_columnconfigure(i, weight=1)
        self.calc_frame.grid_rowconfigure(0, weight=0)
        self.calc_frame.grid_rowconfigure(1, weight=1)

        self.create_buttons()

    def create_history_widgets(self):
        # Tiêu đề Lịch sử
        history_title = tk.Label(
            self.history_frame,
            text="LỊCH SỬ TÍNH TOÁN",
            bg=COLOR["HISTORY_BG"],
            fg=COLOR["TEXT_FG"],
            font=('Helvetica', 14, 'bold')
        )
        history_title.pack(fill='x', padx=5, pady=5)

        # Text Widget để hiển thị lịch sử
        self.history_display = tk.Text(
            self.history_frame,
            bg=COLOR["HISTORY_BG"],
            fg=COLOR["HISTORY_FG"],
            font=('Consolas', 10),
            state='disabled',
            relief='flat',
            padx=5,
            pady=5
        )
        self.history_display.pack(expand=True, fill='both', padx=5, pady=5)

        # Nút xóa lịch sử
        clear_history_btn = tk.Button(
            self.history_frame,
            text="Xóa Lịch sử",
            bg=COLOR["AC_BTN_BG"],
            fg=COLOR["TEXT_FG"],
            font=('Helvetica', 10, 'bold'),
            command=self.clear_history
        )
        clear_history_btn.pack(fill='x', padx=5, pady=(0, 5))

    def update_history_display(self):
        """Cập nhật nội dung lịch sử"""
        self.history_display.config(state='normal')
        self.history_display.delete('1.0', tk.END)

        for entry in reversed(self.history):
            self.history_display.insert(tk.END, entry + '\n\n')

        self.history_display.config(state='disabled')

    def clear_history(self):
        """Xóa toàn bộ lịch sử"""
        self.history = []
        self.update_history_display()

    def toggle_history(self):
        """Chức năng ẩn/hiện khung lịch sử"""
        if self.history_visible:
            self.history_frame.grid_forget()
            self.master.grid_columnconfigure(0, weight=1)
            self.master.grid_columnconfigure(1, weight=0)
            self.history_visible = False
        else:
            self.history_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
            self.master.grid_columnconfigure(0, weight=2)
            self.master.grid_columnconfigure(1, weight=1)
            self.history_visible = True

    def create_buttons(self):
        # Thiết kế layout nút bấm (ĐÃ VIỆT HÓA & DÙNG SEND_VALUE)
        buttons = [
            ('AC', 2, 0, 1, COLOR["AC_BTN_BG"], False),
            ('Xóa', 2, 1, 1, COLOR["AC_BTN_BG"], False, 'DEL'),
            ('(', 2, 2, 1, COLOR["FUNC_BTN_BG"], False),
            (')', 2, 3, 1, COLOR["FUNC_BTN_BG"], False),
            ('Lịch sử', 2, 4, 1, COLOR["HISTORY_TOGGLE_BTN"], False, 'History'),

            ('sin', 3, 0, 1, COLOR["FUNC_BTN_BG"], True),
            ('cos', 3, 1, 1, COLOR["FUNC_BTN_BG"], True),
            ('tan', 3, 2, 1, COLOR["FUNC_BTN_BG"], True),
            ('log', 3, 3, 1, COLOR["FUNC_BTN_BG"], True),
            ('/', 3, 4, 1, COLOR["OP_BTN_BG"], False),

            ('7', 4, 0, 1, COLOR["NUMBER_BTN_BG"], False),
            ('8', 4, 1, 1, COLOR["NUMBER_BTN_BG"], False),
            ('9', 4, 2, 1, COLOR["NUMBER_BTN_BG"], False),
            ('^', 4, 3, 1, COLOR["FUNC_BTN_BG"], False),
            ('*', 4, 4, 1, COLOR["OP_BTN_BG"], False),

            ('4', 5, 0, 1, COLOR["NUMBER_BTN_BG"], False),
            ('5', 5, 1, 1, COLOR["NUMBER_BTN_BG"], False),
            ('6', 5, 2, 1, COLOR["NUMBER_BTN_BG"], False),
            ('sqrt', 5, 3, 1, COLOR["FUNC_BTN_BG"], True),
            ('-', 5, 4, 1, COLOR["OP_BTN_BG"], False),

            ('1', 6, 0, 1, COLOR["NUMBER_BTN_BG"], False),
            ('2', 6, 1, 1, COLOR["NUMBER_BTN_BG"], False),
            ('3', 6, 2, 1, COLOR["NUMBER_BTN_BG"], False),
            ('\u03c0', 6, 3, 1, COLOR["FUNC_BTN_BG"], False, 'pi'),  # SỬA LỖI: Dùng Unicode cho ký hiệu Pi
            ('+', 6, 4, 1, COLOR["OP_BTN_BG"], False),

            ('0', 7, 0, 2, COLOR["NUMBER_BTN_BG"], False),
            ('.', 7, 2, 1, COLOR["NUMBER_BTN_BG"], False),
            ('e', 7, 3, 1, COLOR["FUNC_BTN_BG"], False),
            ('Chế độ', 7, 4, 1, COLOR["FUNC_BTN_BG"], False, 'MODE'),

            ('=', 8, 4, 1, COLOR["EQUAL_BTN_BG"], False),
        ]

        # Vòng lặp tạo nút
        for btn_data in buttons:
            text = btn_data[0]
            r, c, cs, bg, is_func = btn_data[1:6]
            send_value = btn_data[6] if len(btn_data) == 7 else text

            cmd = None
            if send_value == 'History':
                cmd = self.toggle_history
            elif send_value == 'MODE':
                cmd = self.toggle_mode
            else:
                cmd = lambda t=send_value, f=is_func: self.button_press(t, f)

            btn = tk.Button(
                self.calc_frame,
                text=text,
                padx=10,
                pady=10,
                bg=bg,
                fg=COLOR["TEXT_FG"],
                activebackground=bg,
                activeforeground='white',
                relief='raised',
                bd=4,  # Tăng độ dày viền
                font=FONT_STYLE,
                command=cmd
            )

            # Xử lý nút "=" (rowspan)
            if send_value == '=':
                btn.grid(row=7, column=4, columnspan=1, rowspan=2, sticky='nsew', padx=2, pady=2)
                self.calc_frame.grid_rowconfigure(8, weight=1)
            else:
                btn.grid(row=r, column=c, columnspan=cs, sticky='nsew', padx=2, pady=2)
                self.calc_frame.grid_rowconfigure(r, weight=1)

    # --- LOGIC XỬ LÝ (Giữ nguyên) ---
    def toggle_mode(self):
        if self.mode == "DEG":
            self.mode = "RAD"
        else:
            self.mode = "DEG"
        self.mode_label.set(self.mode)

    def button_press(self, text, is_function):
        if text == 'AC':
            self.expression = ""
            self.display_text.set("0")
        elif text == 'DEL':
            self.expression = self.expression[:-1]
            if not self.expression:
                self.display_text.set("0")
            else:
                self.display_text.set(self.expression)
        elif text == '=':
            self.calculate()
        else:
            if is_function:
                self.expression += f"{text}("
            elif text == '^':
                self.expression += '**'
            elif text == 'pi':
                self.expression += 'math.pi'
            elif text == 'e':
                self.expression += 'math.e'
            else:
                self.expression += text
            self.display_text.set(self.expression)

    def calculate(self):
        original_exp = self.expression
        safe_exp = original_exp.replace('log(', 'math.log10(')
        safe_exp = safe_exp.replace('sqrt(', 'math.sqrt(')

        try:
            final_exp = safe_exp
            trig_funcs = ['sin', 'cos', 'tan']

            # Xử lý lượng giác DEG/RAD
            for func_name in trig_funcs:
                start = 0
                while True:
                    func_index = final_exp.find(f"{func_name}(", start)
                    if func_index == -1: break
                    open_paren = func_index + len(func_name)
                    close_paren = self._find_matching_paren(final_exp, open_paren)
                    if close_paren == -1: raise SyntaxError

                    arg_str = final_exp[open_paren + 1: close_paren]
                    arg_value = eval(arg_str, {"math": math})

                    if self.mode == "DEG":
                        replacement = f"math.{func_name}(math.radians({arg_value}))"
                    else:
                        replacement = f"math.{func_name}({arg_value})"

                    final_exp = final_exp[:func_index] + replacement + final_exp[close_paren + 1:]
                    start = func_index + len(replacement)

            result = str(eval(final_exp, {"math": math}))

            # Lưu lịch sử
            history_entry = f"{original_exp} =\n{result}"
            self.history.append(history_entry)
            self.update_history_display()

            self.display_text.set(result)
            self.expression = result

        except ZeroDivisionError:
            self.display_text.set("Lỗi: Chia 0")
            self.expression = ""
        except (SyntaxError, NameError) as e:
            self.display_text.set("Lỗi cú pháp")
            self.expression = ""
        except Exception as e:
            self.display_text.set("Lỗi")
            self.expression = ""

    def _find_matching_paren(self, text, start_index):
        count = 1
        for i in range(start_index + 1, len(text)):
            if text[i] == '(':
                count += 1
            elif text[i] == ')':
                count -= 1

            if count == 0:
                return i
        return -1

    def bind_keys(self):
        self.key_map = {
            '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
            '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
            '.': '.',
            '+': '+', '-': '-', '*': '*', '/': '/',
            '(': '(', ')': ')',
            '<Return>': '=',
            '<KP_Enter>': '=',
            '=': '=',
            '<BackSpace>': 'DEL',
            'c': 'AC',
            'C': 'AC',
            'h': 'History',
        }
        self.master.bind_all('<Key>', self.key_press_handler)

    def key_press_handler(self, event):
        key = event.keysym
        char = event.char

        # Xử lý phím tắt History
        if char == 'h' or char == 'H':
            self.toggle_history()
            return

        if key in self.key_map:
            mapped_value = self.key_map[key]
            self.button_press(mapped_value, False)

        elif char in self.key_map:
            mapped_value = self.key_map[char]
            self.button_press(mapped_value, False)


# --- 3. Khởi chạy Ứng dụng ---
if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("400x450")
    root.resizable(True, True)
    app = Calculator(root)
    root.mainloop()