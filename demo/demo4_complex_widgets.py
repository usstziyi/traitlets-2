"""
Demo 4: 复杂控件与自定义验证
===========================

本教程介绍：
1. 复杂控件（表格、列表、树）与 traitlets 的集成
2. 自定义验证器
3. 列表/字典类型的 traitlets
4. 动态表单生成

运行方式: uv run demo4_complex_widgets.py

Signature: trea cn
"""

import sys
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox, QDoubleSpinBox,
    QCheckBox, QComboBox, QTextEdit, QGroupBox, QFormLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QListWidget, QListWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt
from traitlets import (
    HasTraits, Int, Unicode, Float, Bool, List, Dict, Enum,
    default, observe, validate, TraitError
)


# ============================================================
# 1. 列表/字典类型的 Traitlets
# ============================================================

class DataModel(HasTraits):
    """演示 List 和 Dict 类型"""
    tags = List(Unicode())
    scores = Dict()
    selected_tag = Unicode()

    @default("tags")
    def _default_tags(self):
        return ["Python", "PySide6", "Traitlets"]

    @default("scores")
    def _default_scores(self):
        return {"数学": 90, "语文": 85, "英语": 88}

    @default("selected_tag")
    def _default_selected_tag(self):
        return ""

    def add_tag(self, tag: str):
        """添加标签"""
        if tag and tag not in self.tags:
            # 创建一个 全新的列表对象 ，内容是原列表的所有元素 + 新标签
            # 将这个新列表赋值给 self.tags ，这会触发 traitlets 的 setter 机制 ，从而发出变更通知
            self.tags = self.tags + [tag]

    def remove_tag(self, tag: str):
        """移除标签"""
        if tag in self.tags:
            self.tags = [t for t in self.tags if t != tag]

    def set_score(self, subject: str, score: float):
        """设置分数"""
        # traitlets 的 Dict 类型 无法检测到 self.scores["数学"] = 95 这种原地修改
        # 必须通过赋值一个全新对象来触发变更通知机制
        new_scores = dict(self.scores)
        new_scores[subject] = score
        self.scores = new_scores


class DataWindow(QMainWindow):
    """列表示例窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo 4.1: 列表与字典")
        self.resize(500, 400)

        self.model = DataModel()

        # 标签列表
        self.tag_list = QListWidget()

        # 输入框
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("输入标签并回车")
        self.tag_input.returnPressed.connect(self._add_tag)

        self.add_btn = QPushButton("添加")
        self.add_btn.clicked.connect(self._add_tag)

        self.remove_btn = QPushButton("移除选中")
        self.remove_btn.clicked.connect(self._remove_tag)

        # 分数表格
        self.score_table = QTableWidget()
        self.score_table.setColumnCount(2)
        self.score_table.setHorizontalHeaderLabels(["科目", "分数"])
        self.score_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        # JSON 显示
        self.json_display = QTextEdit()
        self.json_display.setReadOnly(True)

        # 布局
        tab_widget = QTabWidget()

        # 标签页
        tag_tab = QWidget()
        tag_layout = QVBoxLayout()
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.tag_input)
        input_layout.addWidget(self.add_btn)
        input_layout.addWidget(self.remove_btn)
        tag_layout.addLayout(input_layout)
        tag_layout.addWidget(self.tag_list)
        tag_tab.setLayout(tag_layout)

        # 分数页
        score_tab = QWidget()
        score_layout = QVBoxLayout()
        score_layout.addWidget(self.score_table)
        score_tab.setLayout(score_layout)

        tab_widget.addTab(tag_tab, "标签管理")
        tab_widget.addTab(score_tab, "分数管理")

        main_layout = QVBoxLayout()
        main_layout.addWidget(tab_widget)
        main_layout.addWidget(QLabel("模型状态:"))
        main_layout.addWidget(self.json_display)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # 监听变化
        self.model.observe(self._on_tags_change, names=["tags"])
        self.model.observe(self._on_scores_change, names=["scores"])

        # 初始化
        self._refresh_tags()
        self._refresh_scores()
        self._update_json()

    def _add_tag(self):
        tag = self.tag_input.text().strip()
        if tag:
            self.model.add_tag(tag)
            self.tag_input.clear()

    def _remove_tag(self):
        current = self.tag_list.currentItem()
        if current:
            self.model.remove_tag(current.text())

    def _on_tags_change(self, change):
        self._refresh_tags()
        self._update_json()

    def _on_scores_change(self, change):
        self._refresh_scores()
        self._update_json()

    def _refresh_tags(self):
        self.tag_list.clear()
        for tag in self.model.tags:
            self.tag_list.addItem(tag)

    def _refresh_scores(self):
        self.score_table.setRowCount(0)
        for subject, score in self.model.scores.items():
            row = self.score_table.rowCount()
            self.score_table.insertRow(row)
            self.score_table.setItem(row, 0, QTableWidgetItem(subject))
            score_item = QTableWidgetItem(str(score))
            score_item.setFlags(score_item.flags() & ~Qt.ItemIsEditable)
            self.score_table.setItem(row, 1, score_item)

    def _update_json(self, change=None):
        data = {
            "tags": self.model.tags,
            "scores": self.model.scores,
        }
        self.json_display.setText(json.dumps(data, indent=2, ensure_ascii=False))


# ============================================================
# 2. 复杂验证：多字段联动
# ============================================================

class FormModel(HasTraits):
    """带有复杂验证的表单模型"""
    username = Unicode()
    password = Unicode()
    password_confirm = Unicode()
    email = Unicode()
    age = Int()
    agreement = Bool()

    @default("username")
    def _default_username(self):
        return ""

    @default("password")
    def _default_password(self):
        return ""

    @default("password_confirm")
    def _default_password_confirm(self):
        return ""

    @default("email")
    def _default_email(self):
        return ""

    @default("age")
    def _default_age(self):
        return 18

    @default("agreement")
    def _default_agreement(self):
        return False

    @validate("username")
    def _validate_username(self, proposal):
        value = proposal["value"]
        if len(value) < 3:
            raise TraitError("用户名至少需要 3 个字符")
        if len(value) > 20:
            raise TraitError("用户名不能超过 20 个字符")
        if not value.isalnum():
            raise TraitError("用户名只能包含字母和数字")
        return value

    @validate("password")
    def _validate_password(self, proposal):
        value = proposal["value"]
        if len(value) < 6:
            raise TraitError("密码至少需要 6 个字符")
        return value

    @validate("password_confirm")
    def _validate_password_confirm(self, proposal):
        value = proposal["value"]
        if value != self.password:
            raise TraitError("两次输入的密码不一致")
        return value

    @validate("email")
    def _validate_email(self, proposal):
        value = proposal["value"]
        if value and "@" not in value:
            raise TraitError("邮箱格式不正确")
        return value

    @validate("age")
    def _validate_age(self, proposal):
        value = proposal["value"]
        if value < 18:
            raise TraitError("年龄必须满 18 岁")
        return value

    def is_valid(self) -> tuple[bool, str]:
        """检查所有字段是否有效"""
        try:
            if not self.username:
                return False, "用户名不能为空"
            if not self.password:
                return False, "密码不能为空"
            if self.password != self.password_confirm:
                return False, "两次输入的密码不一致"
            if not self.email:
                return False, "邮箱不能为空"
            if not self.agreement:
                return False, "请同意用户协议"
            return True, ""
        except TraitError as e:
            return False, str(e)


class ValidationWindow(QMainWindow):
    """验证示例窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo 4.2: 复杂验证")
        self.resize(450, 350)

        self.model = FormModel()

        # 控件
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("3-20位字母或数字")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("至少6个字符")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.password_confirm_input = QLineEdit()
        self.password_confirm_input.setPlaceholderText("再次输入密码")
        self.password_confirm_input.setEchoMode(QLineEdit.Password)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@email.com")

        self.age_spinbox = QSpinBox()
        self.age_spinbox.setRange(1, 150)

        self.agreement_check = QCheckBox("我已阅读并同意用户协议")

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red;")

        self.submit_btn = QPushButton("提交")
        self.submit_btn.clicked.connect(self._submit)

        self.status_label = QLabel()
        self.status_label.setWordWrap(True)

        # 布局
        form_layout = QFormLayout()
        form_layout.addRow("用户名:", self.username_input)
        form_layout.addRow("密码:", self.password_input)
        form_layout.addRow("确认密码:", self.password_confirm_input)
        form_layout.addRow("邮箱:", self.email_input)
        form_layout.addRow("年龄:", self.age_spinbox)
        form_layout.addRow("", self.agreement_check)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.error_label)
        main_layout.addWidget(self.submit_btn)
        main_layout.addWidget(self.status_label)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # 绑定
        self.username_input.textChanged.connect(self._on_username)
        self.password_input.textChanged.connect(self._on_password)
        self.password_confirm_input.textChanged.connect(self._on_password_confirm)
        self.email_input.textChanged.connect(self._on_email)
        self.age_spinbox.valueChanged.connect(self._on_age)
        self.agreement_check.toggled.connect(self._on_agreement)

        # 错误提示
        self.model.observe(self._on_error, names=[
            "username", "password", "password_confirm", "email", "age"
        ])

    def _on_username(self, text):
        try:
            self.model.username = text
            self.error_label.clear()
        except TraitError as e:
            self.error_label.setText(str(e))

    def _on_password(self, text):
        try:
            self.model.password = text
            self.error_label.clear()
        except TraitError as e:
            self.error_label.setText(str(e))

    def _on_password_confirm(self, text):
        try:
            self.model.password_confirm = text
            self.error_label.clear()
        except TraitError as e:
            self.error_label.setText(str(e))

    def _on_email(self, text):
        try:
            self.model.email = text
            self.error_label.clear()
        except TraitError as e:
            self.error_label.setText(str(e))

    def _on_age(self, value):
        try:
            self.model.age = value
            self.error_label.clear()
        except TraitError as e:
            self.error_label.setText(str(e))

    def _on_agreement(self, checked):
        self.model.agreement = checked

    def _on_error(self, change):
        pass  # 错误已经在输入时处理

    def _submit(self):
        valid, msg = self.model.is_valid()
        if valid:
            self.status_label.setText(f"提交成功！\n用户名: {self.model.username}\n邮箱: {self.model.email}")
            QMessageBox.information(self, "成功", "表单验证通过！")
        else:
            self.error_label.setText(f"验证失败: {msg}")


# ============================================================
# 3. 动态表单生成
# ============================================================

class DynamicFormModel(HasTraits):
    """动态表单模型"""
    settings = Dict()

    @default("settings")
    def _default_settings(self):
        return {
            "theme": "light",
            "font_size": 14,
            "auto_save": True,
            "language": "zh_CN",
        }


class DynamicFormWindow(QMainWindow):
    """动态表单生成示例"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo 4.3: 动态表单")
        self.resize(400, 300)

        self.model = DynamicFormModel()

        # 表单定义（可以来自配置文件）
        self.form_definition = [
            {"key": "theme", "type": "combo", "label": "主题", "options": ["light", "dark"]},
            {"key": "font_size", "type": "spin", "label": "字体大小", "min": 8, "max": 32},
            {"key": "auto_save", "type": "check", "label": "自动保存"},
            {"key": "language", "type": "combo", "label": "语言", "options": ["zh_CN", "en_US", "ja_JP"]},
        ]

        self.widgets = {}
        self.form_layout = QFormLayout()

        # 动态生成表单
        for field in self.form_definition:
            widget = self._create_widget(field)
            self.widgets[field["key"]] = widget
            self.form_layout.addRow(f"{field['label']}:", widget)

            # 连接信号
            self._connect_signal(field, widget)

        # JSON 显示
        self.json_display = QTextEdit()
        self.json_display.setReadOnly(True)

        # 布局
        main_layout = QVBoxLayout()
        main_layout.addLayout(self.form_layout)
        main_layout.addWidget(QLabel("当前设置:"))
        main_layout.addWidget(self.json_display)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # 初始化显示
        self._init_widgets()
        self._update_json()

        # 监听变化
        self.model.observe(self._on_settings_change, names=["settings"])

    def _create_widget(self, field):
        """根据字段类型创建控件"""
        field_type = field["type"]
        if field_type == "combo":
            combo = QComboBox()
            combo.addItems(field["options"])
            return combo
        elif field_type == "spin":
            spin = QSpinBox()
            spin.setRange(field.get("min", 0), field.get("max", 100))
            return spin
        elif field_type == "check":
            return QCheckBox()
        else:
            return QLineEdit()

    def _connect_signal(self, field, widget):
        """连接控件信号到 model"""
        key = field["key"]
        field_type = field["type"]

        if field_type == "combo":
            widget.currentTextChanged.connect(lambda v: self._set_setting(key, v))
        elif field_type == "spin":
            widget.valueChanged.connect(lambda v: self._set_setting(key, v))
        elif field_type == "check":
            widget.toggled.connect(lambda v: self._set_setting(key, v))
        else:
            widget.textChanged.connect(lambda v: self._set_setting(key, v))

    def _set_setting(self, key, value):
        """更新设置"""
        new_settings = dict(self.model.settings)
        new_settings[key] = value
        self.model.settings = new_settings

    def _on_settings_change(self, change):
        self._update_json()

    def _update_json(self, change=None):
        self.json_display.setText(json.dumps(self.model.settings, indent=2, ensure_ascii=False))

    def _init_widgets(self):
        """初始化控件值"""
        settings = self.model.settings
        for field in self.form_definition:
            key = field["key"]
            widget = self.widgets[key]
            value = settings.get(key)

            if field["type"] == "combo":
                idx = widget.findText(str(value))
                if idx >= 0:
                    widget.setCurrentIndex(idx)
            elif field["type"] == "spin":
                widget.setValue(int(value))
            elif field["type"] == "check":
                widget.setChecked(bool(value))


# ============================================================
# 主函数
# ============================================================

def main():
    app = QApplication(sys.argv)

    # 列表示例
    # window = DataWindow()

    # 验证示例
    window = ValidationWindow()

    # 动态表单示例
    # window = DynamicFormWindow()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
