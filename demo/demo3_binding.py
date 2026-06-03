"""
Demo 3: 控件与 Traitlets 双向绑定
================================

本教程实现一个通用的双向绑定机制：
1. 创建 binder 工具类，简化绑定代码
2. 支持多种 PySide6 控件
3. 演示表单场景下的批量绑定

运行方式: uv run demo3_binding.py

Signature: trea cn
"""

import sys
from typing import Any
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox, QDoubleSpinBox,
    QCheckBox, QComboBox, QTextEdit, QGroupBox, QFormLayout,
    QSlider, QMessageBox
)
from PySide6.QtCore import Signal, QObject
from traitlets import HasTraits, Int, Unicode, Float, Bool, Enum, default, observe


# ============================================================
# 1. 通用 Binder 类
# ============================================================

class TraitletsBinder:
    """
    Traitlets 与 PySide6 控件的双向绑定器。

    使用方式:
        binder = TraitletsBinder(model, widget)
        binder.bind("name", name_input)
        binder.bind("age", age_spinbox)
    """

    def __init__(self, model: HasTraits, parent: QObject = None):
        """
        Args:
            model: traitlets HasTraits 实例
            parent: 可选的父 QObject（用于信号生命周期管理）
        """
        self.model = model
        self.parent = parent
        self._bindings = {}

    def bind(self, trait_name: str, widget: Any, widget_property: str = "text",
             widget_signal: str = "textChanged", to_widget_func=None, from_widget_func=None):
        """
        绑定一个 traitlets 属性到 UI 控件。

        Args:
            trait_name: traitlets 属性名
            widget: PySide6 控件
            widget_property: 控件属性名（如 "text", "value", "isChecked"）
            widget_signal: 控件信号名（如 "textChanged", "valueChanged"）
            to_widget_func: 从 traitlets 到 widget 的转换函数
            from_widget_func: 从 widget 到 traitlets 的转换函数
        """
        # 初始化控件值
        initial_value = getattr(self.model, trait_name)
        if to_widget_func:
            initial_value = to_widget_func(initial_value)
        self._set_widget_value(widget, widget_property, initial_value)

        # widget -> model
        signal = getattr(widget, widget_signal)
        signal.connect(lambda v: self._on_widget_change(trait_name, v, from_widget_func))

        # model -> widget
        self.model.observe(
            lambda change: self._on_model_change(widget, widget_property, change, to_widget_func),
            names=[trait_name]
        )

        self._bindings[trait_name] = {
            "widget": widget,
            "property": widget_property,
        }

    def _on_widget_change(self, trait_name, value, from_func):
        """当控件值变化时，更新 model"""
        if from_func:
            value = from_func(value)
        setattr(self.model, trait_name, value)

    def _on_model_change(self, widget, prop_name, change, to_func):
        """当 model 变化时，更新控件"""
        value = change["new"]
        if to_func:
            value = to_func(value)
        self._set_widget_value(widget, prop_name, value)

    @staticmethod
    def _set_widget_value(widget, prop_name, value):
        """设置控件属性值"""
        setter_name = f"set{prop_name[0].upper()}{prop_name[1:]}"
        setter = getattr(widget, setter_name, None)
        if setter:
            setter(value)
        else:
            setattr(widget, prop_name, value)


# ============================================================
# 2. 便捷绑定函数
# ============================================================

def bind_text(model: HasTraits, trait_name: str, line_edit: QLineEdit):
    """绑定 Unicode traitlets 到 QLineEdit"""
    binder = TraitletsBinder(model)
    binder.bind(
        trait_name, line_edit,
        widget_property="text",
        widget_signal="textChanged"
    )
    return binder


def bind_int(model: HasTraits, trait_name: str, spinbox: QSpinBox):
    """绑定 Int traitlets 到 QSpinBox"""
    binder = TraitletsBinder(model)
    binder.bind(
        trait_name, spinbox,
        widget_property="value",
        widget_signal="valueChanged"
    )
    return binder


def bind_float(model: HasTraits, trait_name: str, spinbox: QDoubleSpinBox):
    """绑定 Float traitlets 到 QDoubleSpinBox"""
    binder = TraitletsBinder(model)
    binder.bind(
        trait_name, spinbox,
        widget_property="value",
        widget_signal="valueChanged"
    )
    return binder


def bind_bool(model: HasTraits, trait_name: str, checkbox: QCheckBox):
    """绑定 Bool traitlets 到 QCheckBox"""
    binder = TraitletsBinder(model)
    binder.bind(
        trait_name, checkbox,
        widget_property="checked",
        widget_signal="toggled"
    )
    return binder


# ============================================================
# 3. 数据模型
# ============================================================

class EmployeeModel(HasTraits):
    """员工信息模型"""
    name = Unicode()
    age = Int()
    salary = Float()
    department = Unicode()
    is_manager = Bool()
    level = Unicode()

    @default("name")
    def _default_name(self):
        return ""

    @default("age")
    def _default_age(self):
        return 25

    @default("salary")
    def _default_salary(self):
        return 5000.0

    @default("department")
    def _default_department(self):
        return "技术部"

    @default("is_manager")
    def _default_is_manager(self):
        return False

    @default("level")
    def _default_level(self):
        return "初级"


# ============================================================
# 4. 表单窗口
# ============================================================

class EmployeeFormWindow(QMainWindow):
    """使用双向绑定的员工表单"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo 3: 双向绑定")
        self.resize(500, 400)

        # 创建模型
        self.model = EmployeeModel()

        # 创建控件
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入姓名")

        self.age_spinbox = QSpinBox()
        self.age_spinbox.setRange(18, 65)

        self.salary_spinbox = QDoubleSpinBox()
        self.salary_spinbox.setRange(0, 100000)
        self.salary_spinbox.setDecimals(2)
        self.salary_spinbox.setPrefix("¥ ")

        self.department_combo = QComboBox()
        self.department_combo.addItems(["技术部", "产品部", "设计部", "市场部", "人事部"])

        self.manager_check = QCheckBox("是否经理")

        self.level_combo = QComboBox()
        self.level_combo.addItems(["初级", "中级", "高级", "专家"])

        # 状态显示
        self.json_label = QLabel()
        self.json_label.setWordWrap(True)
        self.json_label.setStyleSheet("background-color: #f5f5f5; padding: 10px; font-family: monospace;")

        # 按钮
        self.reset_btn = QPushButton("重置为默认值")
        self.reset_btn.clicked.connect(self._reset)

        self.demo_btn = QPushButton("演示：代码修改模型")
        self.demo_btn.clicked.connect(self._demo)

        # 布局
        form_layout = QFormLayout()
        form_layout.addRow("姓名:", self.name_input)
        form_layout.addRow("年龄:", self.age_spinbox)
        form_layout.addRow("薪资:", self.salary_spinbox)
        form_layout.addRow("部门:", self.department_combo)
        form_layout.addRow("经理:", self.manager_check)
        form_layout.addRow("级别:", self.level_combo)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addWidget(self.demo_btn)
        main_layout.addLayout(btn_layout)

        main_layout.addWidget(QLabel("当前模型状态:"))
        main_layout.addWidget(self.json_label)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # 建立绑定
        self._setup_bindings()

        # 初始显示
        self._update_json_display()

        # 监听所有变化
        self.model.observe(self._update_json_display, names=list(self.model.trait_names()))

    def _setup_bindings(self):
        """设置所有双向绑定"""
        # 姓名
        TraitletsBinder(self.model).bind("name", self.name_input, "text", "textChanged")

        # 年龄
        TraitletsBinder(self.model).bind("age", self.age_spinbox, "value", "valueChanged")

        # 薪资
        TraitletsBinder(self.model).bind("salary", self.salary_spinbox, "value", "valueChanged")

        # 部门（需要转换函数）
        TraitletsBinder(self.model).bind(
            "department", self.department_combo,
            widget_property="currentText",
            widget_signal="currentTextChanged"
        )

        # 是否经理
        TraitletsBinder(self.model).bind(
            "is_manager", self.manager_check,
            widget_property="checked",
            widget_signal="toggled"
        )

        # 级别
        TraitletsBinder(self.model).bind(
            "level", self.level_combo,
            widget_property="currentText",
            widget_signal="currentTextChanged"
        )

    def _update_json_display(self, change=None):
        """更新 JSON 显示"""
        import json
        data = self.model._trait_values
        # 过滤掉 traitlets 内部属性
        clean_data = {k: v for k, v in data.items() if not k.startswith("_")}
        self.json_label.setText(json.dumps(clean_data, indent=2, ensure_ascii=False))

    def _reset(self):
        """重置为默认值"""
        self.model.name = ""
        self.model.age = 25
        self.model.salary = 5000.0
        self.model.department = "技术部"
        self.model.is_manager = False
        self.model.level = "初级"

    def _demo(self):
        """演示通过代码修改模型"""
        self.model.name = "张三"
        self.model.age = 30
        self.model.salary = 15000.0
        self.model.department = "产品部"
        self.model.is_manager = True
        self.model.level = "高级"


# ============================================================
# 5. 滑块示例
# ============================================================

class SliderModel(HasTraits):
    """滑块演示模型"""
    value = Int()
    label = Unicode()

    @default("value")
    def _default_value(self):
        return 50

    @default("label")
    def _default_label(self):
        return "数值: 50"

    @observe("value")
    def _update_label(self, change):
        self.label = f"数值: {change['new']}"


class SliderWindow(QMainWindow):
    """滑块示例窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo 3: 滑块示例")
        self.resize(400, 200)

        self.model = SliderModel()

        # 滑块
        self.slider = QSlider()
        self.slider.setOrientation(1)  # 水平
        self.slider.setRange(0, 100)

        # 显示
        self.display = QLabel()
        self.display.setAlignment(8)  # 居中
        self.display.setStyleSheet("font-size: 24px; font-weight: bold;")

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.display)
        layout.addWidget(self.slider)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 绑定
        TraitletsBinder(self.model).bind("value", self.slider, "value", "valueChanged")

        # 显示绑定
        self.model.observe(self._update_display, names=["label"])
        self._update_display()

    def _update_display(self, change=None):
        self.display.setText(self.model.label)


# ============================================================
# 主函数
# ============================================================

def main():
    app = QApplication(sys.argv)

    # 表单示例（推荐先看这个）
    window = EmployeeFormWindow()

    # 滑块示例
    # window = SliderWindow()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
