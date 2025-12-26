import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.metrics import dp
from datetime import datetime
import os  # Dùng để quản lý đường dẫn database


# --- 1. Lớp Quản lý Cơ sở Dữ liệu (SQLite) ---

class DatabaseManager:
    def __init__(self, db_name='tracker_data.db'):
        # Đảm bảo database được tạo ở thư mục hiện hành
        self.db_path = os.path.join(os.getcwd(), db_name)
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_table()

    def connect(self):
        """Thiết lập kết nối đến SQLite"""
        if self.conn is None:
            try:
                self.conn = sqlite3.connect(self.db_path)
                self.cursor = self.conn.cursor()
            except sqlite3.Error as e:
                print(f"Lỗi kết nối database: {e}")

    def create_table(self):
        """Tạo bảng TasksAndNotes nếu chưa tồn tại"""
        self.connect()
        try:
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS TasksAndNotes
                                (
                                    id
                                    INTEGER
                                    PRIMARY
                                    KEY
                                    AUTOINCREMENT,
                                    tieu_de
                                    TEXT
                                    NOT
                                    NULL,
                                    mo_ta
                                    TEXT,
                                    loai
                                    TEXT
                                    NOT
                                    NULL, -- CôngViec, CaNhan, GiaDinh, GhiChu
                                    ngay_den_han
                                    TEXT, -- Dùng cho Công việc/Cá nhân/Gia đình
                                    muc_uu_tien
                                    TEXT,
                                    trang_thai
                                    TEXT, -- ChuaLam, HoanThanh
                                    ngay_tao
                                    TEXT
                                )
                                """)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Lỗi khi tạo bảng: {e}")

    def add_item(self, tieu_de, loai, mo_ta="", ngay_den_han="", muc_uu_tien="Thap", trang_thai="ChuaLam"):
        """Thêm công việc hoặc ghi chú mới"""
        self.connect()
        ngay_tao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.cursor.execute(
                "INSERT INTO TasksAndNotes (tieu_de, mo_ta, loai, ngay_den_han, muc_uu_tien, trang_thai, ngay_tao) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (tieu_de, mo_ta, loai, ngay_den_han, muc_uu_tien, trang_thai, ngay_tao)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Lỗi khi thêm item: {e}")
            return False

    def get_items_by_loai(self, loai):
        """Lấy tất cả công việc/ghi chú theo loại (loai)"""
        self.connect()
        try:
            self.cursor.execute("SELECT * FROM TasksAndNotes WHERE loai = ? ORDER BY ngay_den_han, muc_uu_tien DESC",
                                (loai,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Lỗi khi truy vấn item: {e}")
            return []

    def update_status(self, item_id, trang_thai):
        """Cập nhật trạng thái (Hoàn thành/Chưa làm)"""
        self.connect()
        try:
            self.cursor.execute("UPDATE TasksAndNotes SET trang_thai = ? WHERE id = ?", (trang_thai, item_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Lỗi khi cập nhật trạng thái: {e}")
            return False

    def delete_item(self, item_id):
        """Xóa một item"""
        self.connect()
        try:
            self.cursor.execute("DELETE FROM TasksAndNotes WHERE id = ?", (item_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Lỗi khi xóa item: {e}")
            return False


# --- 2. Lớp Widget cho từng Item (Công việc/Ghi chú) ---

class TaskItem(BoxLayout):
    def __init__(self, item_data, manager, callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(50)
        self.padding = dp(5)
        self.spacing = dp(10)

        self.item_id, title, desc, loai, due_date, priority, status, _ = item_data
        self.manager = manager
        self.callback = callback
        self.loai = loai

        # Thiết lập màu nền dựa trên trạng thái (Chưa làm: Trắng, Hoàn thành: Xanh nhạt)
        bg_color = [1, 1, 1, 1] if status == 'ChuaLam' else [0.8, 1, 0.8, 1]
        self.canvas.before.clear()
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*bg_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Label Tiêu đề + Ngày đến hạn/Mô tả
        detail_text = f"[{priority}] {title}"
        if loai != 'GhiChu' and due_date:
            detail_text += f" (Hạn: {due_date})"
        elif loai == 'GhiChu' and desc:
            detail_text += f" - {desc[:30]}..."

        self.add_widget(Label(text=detail_text, size_hint_x=0.6,
                              halign='left', valign='middle',
                              text_size=(self.width * 0.6, self.height),
                              color=(0, 0, 0, 1)))

        # Nút trạng thái (Chỉ cho Công việc/Cá nhân/Gia đình)
        if loai != 'GhiChu':
            status_btn_text = '✔️' if status == 'ChuaLam' else '↩️'
            self.status_button = Button(text=status_btn_text, size_hint_x=0.2, on_press=self.toggle_status)
            self.add_widget(self.status_button)

        # Nút Xóa
        delete_button = Button(text='🗑️', size_hint_x=0.2, on_press=self.delete_item)
        self.add_widget(delete_button)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def toggle_status(self, instance):
        """Chuyển đổi trạng thái (Chưa làm <-> Hoàn thành)"""
        new_status = 'HoanThanh' if instance.text == '✔️' else 'ChuaLam'
        self.manager.update_status(self.item_id, new_status)
        # Tải lại màn hình để cập nhật giao diện
        self.callback(self.loai)

    def delete_item(self, instance):
        """Xóa item khỏi database và giao diện"""
        self.manager.delete_item(self.item_id)
        # Tải lại màn hình để cập nhật giao diện
        self.callback(self.loai)


# --- 3. Lớp Màn hình Danh sách (Task List Screen) ---

class TaskListScreen(BoxLayout):
    def __init__(self, db_manager, loai_item, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.db_manager = db_manager
        self.loai_item = loai_item  # 'CongViec', 'CaNhan', 'GiaDinh', 'GhiChu'

        # Layout chính chứa danh sách
        self.scroll_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        self.scroll_layout.bind(minimum_height=self.scroll_layout.setter('height'))

        # ScrollView để cuộn danh sách
        scroll_view = ScrollView()
        scroll_view.add_widget(self.scroll_layout)
        self.add_widget(scroll_view)

        # Thêm nút "Thêm mới"
        add_button = Button(text=f'➕ Thêm {loai_item}', size_hint_y=None, height=dp(50), on_press=self.open_add_popup)
        self.add_widget(add_button)

        # Tải dữ liệu ban đầu
        Clock.schedule_once(lambda dt: self.load_items(), 0)

    def load_items(self):
        """Tải dữ liệu từ database và hiển thị lên giao diện"""
        self.scroll_layout.clear_widgets()
        items = self.db_manager.get_items_by_loai(self.loai_item)

        for item in items:
            task_widget = TaskItem(item, self.db_manager, self.load_items)
            self.scroll_layout.add_widget(task_widget)

    def open_add_popup(self, instance):
        """Mở màn hình/popup để thêm mới công việc/ghi chú"""
        # Sử dụng Kivy Popup đơn giản thay vì cửa sổ mới
        from kivy.uix.popup import Popup

        popup_content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        popup_content.add_widget(Label(text=f'Thêm {self.loai_item} mới', size_hint_y=None, height=dp(40)))

        # Tiêu đề
        popup_content.add_widget(Label(text='Tiêu đề:', size_hint_y=None, height=dp(30)))
        tieu_de_input = TextInput(size_hint_y=None, height=dp(40))
        popup_content.add_widget(tieu_de_input)

        # Mô tả
        popup_content.add_widget(Label(text='Mô tả/Chi tiết:', size_hint_y=None, height=dp(30)))
        mo_ta_input = TextInput(size_hint_y=None, height=dp(80), multiline=True)
        popup_content.add_widget(mo_ta_input)

        # Chỉ thêm các trường đặc trưng cho Công việc/Cá nhân/Gia đình
        ngay_den_han_input = None
        muc_uu_tien_spinner = None

        if self.loai_item != 'GhiChu':
            popup_content.add_widget(Label(text='Ngày đến hạn (YYYY-MM-DD):', size_hint_y=None, height=dp(30)))
            ngay_den_han_input = TextInput(size_hint_y=None, height=dp(40),
                                           hint_text=datetime.now().strftime("%Y-%m-%d"))
            popup_content.add_widget(ngay_den_han_input)

            popup_content.add_widget(Label(text='Mức ưu tiên:', size_hint_y=None, height=dp(30)))
            muc_uu_tien_spinner = Spinner(
                text='TrungBinh',
                values=('Cao', 'TrungBinh', 'Thap'),
                size_hint_y=None, height=dp(40)
            )
            popup_content.add_widget(muc_uu_tien_spinner)

        # Nút hành động
        action_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        add_btn = Button(text='Thêm')
        action_layout.add_widget(add_btn)

        cancel_btn = Button(text='Hủy')
        action_layout.add_widget(cancel_btn)

        popup_content.add_widget(action_layout)

        # Định nghĩa Popup
        popup = Popup(title=f'Thêm {self.loai_item}', content=popup_content,
                      size_hint=(0.9, 0.9 if self.loai_item == 'GhiChu' else 1.0),
                      auto_dismiss=False)

        # Gán hành động cho các nút
        def on_add(instance):
            tieu_de = tieu_de_input.text.strip()
            mo_ta = mo_ta_input.text.strip()

            if not tieu_de:
                # Có thể thêm thông báo lỗi ở đây
                return

            if self.loai_item != 'GhiChu':
                ngay_den_han = ngay_den_han_input.text.strip()
                muc_uu_tien = muc_uu_tien_spinner.text
                self.db_manager.add_item(tieu_de, self.loai_item, mo_ta, ngay_den_han, muc_uu_tien)
            else:
                self.db_manager.add_item(tieu_de, self.loai_item, mo_ta)

            self.load_items()
            popup.dismiss()

        add_btn.bind(on_press=on_add)
        cancel_btn.bind(on_press=popup.dismiss)

        popup.open()


# --- 4. Lớp Ứng dụng Kivy Chính ---

class TaskTrackerApp(App):
    def build(self):
        self.db_manager = DatabaseManager()

        # Tạo TabbedPanel
        root_widget = TabbedPanel()
        root_widget.do_default_tab = False
        root_widget.background_color = (0.9, 0.9, 0.9, 1)  # Màu nền nhẹ

        # Danh sách các loại (loai) cần theo dõi
        categories = ['CôngViec', 'CaNhan', 'GiaDinh', 'GhiChu']

        for category in categories:
            # Tạo màn hình danh sách cho từng loại
            screen = TaskListScreen(self.db_manager, category)

            # Tạo Tab cho màn hình
            tab = TabbedPanelItem(text=category)
            tab.content = screen
            root_widget.add_widget(tab)

        return root_widget


if __name__ == '__main__':
    TaskTrackerApp().run()