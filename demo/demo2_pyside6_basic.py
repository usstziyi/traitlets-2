"""
Demo 2: Traitlets 与 PySide6 基础集成
=====================================

本教程介绍如何将 traitlets 与 PySide6 控件结合:
1. 基本思路：traitlets 变化 -> 更新 UI
2. UI 事件 -> 更新 traitlets
3. 单向绑定：数据驱动 UI

核心思想：traitlets 的 @observe 可以监听属性变化，
在变化回调中更新 PySide6 控件，实现数据驱动 UI。

运行方式: uv run demo2_pyside6_basic.py

Signature: trea cn
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox, QDoubleSpinBox,
    QCheckBox, QTextEdit
)
from traitlets import HasTraits, Int, Unicode, Float, Bool, default, observe


# ============================================================
# 1. 最基础: traitlets 驱动 UI 更新
# ============================================================

class PersonModel(HasTraits):
    """数据模型：使用 traitlets 管理属性"""
    name = Unicode()
    age = Int()

    @default("name")
    def _default_name(self):
        return "请输入姓名"

    @default("age")
    def _default_age(self):
        return 0


class BasicWindow(QMainWindow):
    """基础示例窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo 2.1: traitlets 驱动 UI")
        self.resize(400, 200)

        # 创建数据模型
        self.model = PersonModel()

        # 创建 UI 控件
        self.name_label = QLabel("姓名:")
        self.name_display = QLabel(self.model.name)
        self.age_label = QLabel("年龄:")
        self.age_display = QLabel(str(self.model.age))

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_display)
        layout.addWidget(self.age_label)
        layout.addWidget(self.age_display)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 关键：使用 @observe 监听 traitlets 变化，自动更新 UI
        self.model.observe(self._on_name_change, names=["name"])
        self.model.observe(self._on_age_change, names=["age"])

        # 5秒后演示自动更新
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, self._demo_update)

    def _on_name_change(self, change):
        """当 model.name 变化时，自动更新 UI"""
        self.name_display.setText(change["new"])

    def _on_age_change(self, change):
        """当 model.age 变化时，自动更新 UI"""
        self.age_display.setText(str(change["new"]))

    def _demo_update(self):
        """演示：修改 traitlets 会自动触发 UI 更新"""
        self.model.name = "张三"
        self.model.age = 25

        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self, "提示",
            "修改了 model.name 和 model.age\n"
            "注意 UI 自动更新了！不需要手动调用 setText"
        )


# ============================================================
# 2. 进阶: UI 事件更新 traitlets
# ============================================================

class EditablePersonModel(HasTraits):
    """可编辑的数据模型"""
    name = Unicode()
    age = Int()
    score = Float()
    is_active = Bool()

    @default("name")
    def _default_name(self):
        return ""

    @default("age")
    def _default_age(self):
        return 100

    @default("score")
    def _default_score(self):
        return 0.0

    @default("is_active")
    def _default_is_active(self):
        return False

    @observe("name", "age", "score", "is_active")
    def _log_change(self, change):
        """当 model 变化时，记录日志"""
        print(f"  {change['old']} 变化为 {change['new']}")


class EditWindow(QMainWindow):
    """可编辑示例窗口：UI 输入 -> 更新 traitlets"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo 2.2: UI 事件更新 traitlets")
        self.resize(450, 300)

        # 创建数据模型
        self.model = EditablePersonModel()

        # 创建 UI 控件
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("输入姓名")

        self.age_input = QSpinBox()
        self.age_input.setRange(0, 150)

        self.score_input = QDoubleSpinBox()
        self.score_input.setRange(0.0, 100.0)
        self.score_input.setDecimals(1)

        self.active_check = QCheckBox("是否激活")

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("操作日志将显示在这里...")

        # 设置布局
        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("姓名:"))
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(QLabel("年龄:"))
        form_layout.addWidget(self.age_input)
        form_layout.addWidget(QLabel("分数:"))
        form_layout.addWidget(self.score_input)
        form_layout.addWidget(self.active_check)
        form_layout.addWidget(QLabel("日志:"))
        form_layout.addWidget(self.log_text)

        container = QWidget()
        container.setLayout(form_layout)
        self.setCentralWidget(container)

        # 关键：UI 事件 -> 更新 traitlets
        self.name_input.textChanged.connect(self._on_name_input)
        self.age_input.valueChanged.connect(self._on_age_input)
        self.score_input.valueChanged.connect(self._on_score_input)
        self.active_check.toggled.connect(self._on_active_input)

        # traitlets 变化 -> 记录日志
        self.model.observe(self._log_change, names=["name", "age", "score", "is_active"])

    def _on_name_input(self, text):
        """姓名输入框变化 -> 更新 model.name"""
        self.model.name = text

    def _on_age_input(self, value):
        """年龄输入框变化 -> 更新 model.age"""
        self.model.age = value

    def _on_score_input(self, value):
        """分数输入框变化 -> 更新 model.score"""
        self.model.score = value

    def _on_active_input(self, checked):
        """复选框变化 -> 更新 model.is_active"""
        self.model.is_active = checked

    def _log_change(self, change):
        """记录 traitlets 变化到日志"""
        name = change["name"]
        old = change["old"]
        new = change["new"]
        self.log_text.append(f"[{name}] {old} -> {new}")


# ============================================================
# 3. 完整示例: 双向联动
# ============================================================

class SyncPersonModel(HasTraits):
    """同步模型：带有验证"""
    name = Unicode()
    age = Int()

    @default("name")
    def _default_name(self):
        return "匿名"

    @default("age")
    def _default_age(self):
        return 100


class SyncWindow(QMainWindow):
    """双向联动示例"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo 2.3: 双向联动")
        self.resize(500, 250)

        self.model = SyncPersonModel()

        # UI 控件
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("输入姓名")

        self.age_input = QSpinBox()
        self.age_input.setRange(0, 150)

        # 显示当前模型状态的标签
        self.status_label = QLabel()

        # 演示按钮
        self.demo_btn = QPushButton("演示：代码修改 traitlets")

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(QLabel("姓名:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("年龄:"))
        layout.addWidget(self.age_input)
        layout.addWidget(self.demo_btn)
        layout.addWidget(self.status_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 连接：UI -> model
        self.name_input.textChanged.connect(lambda t: setattr(self.model, "name", t))
        self.age_input.valueChanged.connect(lambda v: setattr(self.model, "age", v))

        # 连接：model -> UI (显示)
        self.model.observe(self._update_display, names=["name", "age"]) # 同步状态栏
        self.model.observe(self._sync_ui, names=["name", "age"]) # 同步控件

        # 按钮事件
        self.demo_btn.clicked.connect(self._demo_change)

        # 初始化显示
        self._update_display({"name": "init", "new": ""})

    def _sync_ui(self, change):
        """当 traitlets 变化时，同步 UI 控件（避免无限循环）"""
        # 注意：这里需要小心处理，避免 UI->model->UI 的无限循环
        # 在实际项目中，通常使用更智能的绑定方式
        if change["name"] == "name":
            if self.name_input.text() != change["new"]:
                self.name_input.setText(change["new"])
        elif change["name"] == "age":
            if self.age_input.value() != change["new"]:
                self.age_input.setValue(change["new"])

    def _update_display(self, change):
        """更新状态显示"""
        self.status_label.setText(
            f"当前模型状态:\n"
            f"  姓名: {self.model.name}\n"
            f"  年龄: {self.model.age}"
        )

    def _demo_change(self):
        """演示通过代码修改 traitlets"""
        self.model.name = "李四"
        self.model.age = 30


# ============================================================
# 主函数
# ============================================================

def main():
    app = QApplication(sys.argv)

    # 选择要展示的窗口
    # 你可以取消注释来查看不同的示例

    # 示例 1: traitlets 驱动 UI
    # window = BasicWindow()

    # 示例 2: UI 事件更新 traitlets
    # window = EditWindow()

    # 示例 3: 双向联动
    window = SyncWindow()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
