import sys
from typing import Any, Callable, Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox, QDoubleSpinBox,
    QCheckBox, QComboBox, QTextEdit, QGroupBox, QFormLayout,
    QMessageBox
)
from PySide6.QtCore import Qt, Signal, QObject, Property


# =============================================================================
# 0. qt_property 描述符（自动生成 Property 三件套）
# =============================================================================
# Qt Property（Qt 属性）是 Qt 框架在标准 C++/Python 语言特性之上构建的一套元对象属性系统。
# 它不仅仅是一个存储数据的变量或普通的 getter/setter，
# 而是被注册到 Qt 元对象系统（Meta-Object System, MOC） 中的“一等公民”。
# 这意味着该属性在运行时可以被反射、被 QML 引擎识别、被动画系统驱动、被序列化框架处理。
# =============================================================================

def qt_property(type_, default=None):
    """自动生成完整的 Qt Property 三件套: storage + signal + Property"""
    class Descriptor:
        def __init__(self):
            self.signal_name = None
            self.storage_name = None

        def __set_name__(self, owner, name):
            self.storage_name = f"_{name}"
            self.signal_name = f"{name}Changed"
            # 自动在类上创建 Signal
            setattr(owner, self.signal_name, Signal())
            # 自动创建 @Property
            store = self.storage_name
            prop = Property(
                type_,
                fget=lambda self: getattr(self, store, default),
                fset=self._make_setter(),
                notify=getattr(owner, self.signal_name),
            )
            setattr(owner, name, prop)

        def _make_setter(self):
            sig_name = self.signal_name
            store_name = self.storage_name
            def setter(self, value):
                if getattr(self, store_name, default) != value:
                    setattr(self, store_name, value)
                    getattr(self, sig_name).emit()
            return setter

    return Descriptor()


# ============================================================
# 1. 通用 Binder 类 (无需修改，与 qt_property 完全兼容)
# ============================================================

class QtBinder:
    """Qt Property 与 PySide6 控件的双向绑定器。"""

    def __init__(self, model: QObject):
        self.model = model
        self._bindings = {}
        self._updating = False

    def bind(
        self,
        prop_name: str,
        widget: Any,
        widget_property: str = "text",
        widget_signal: str = "textChanged",
        to_widget_func: Optional[Callable] = None,
        from_widget_func: Optional[Callable] = None,
    ):
        # ① 初始值写入控件
        initial_value = self.model.property(prop_name)
        if to_widget_func:
            initial_value = to_widget_func(initial_value)
        self._set_widget_value(widget, widget_property, initial_value)

        # ② Widget → Model
        signal = getattr(widget, widget_signal)
        def on_widget_changed(value):
            if self._updating:
                return
            converted = from_widget_func(value) if from_widget_func else value
            self.model.setProperty(prop_name, converted)
        signal.connect(on_widget_changed)

        # ③ Model → Widget
        notify_signal_name = f"{prop_name}Changed"
        notify_signal = getattr(self.model, notify_signal_name, None)
        if notify_signal is None:
            raise AttributeError(
                f"Model '{type(self.model).__name__}' 缺少通知信号 '{notify_signal_name}'。"
            )

        def on_model_changed():
            if self._updating:
                return
            self._updating = True
            try:
                value = self.model.property(prop_name)
                if to_widget_func:
                    value = to_widget_func(value)
                self._set_widget_value(widget, widget_property, value)
            finally:
                self._updating = False
        notify_signal.connect(on_model_changed)

        # ④ 记录绑定
        self._bindings[prop_name] = {
            "widget": widget,
            "property": widget_property,
        }

    @staticmethod
    def _set_widget_value(widget: Any, prop_name: str, value: Any):
        setter_name = f"set{prop_name[0].upper()}{prop_name[1:]}"
        setter = getattr(widget, setter_name, None)
        if callable(setter):
            setter(value)
        else:
            setattr(widget, prop_name, value)


# ============================================================
# 2. Employee Model (🔥 重构后：80行 → 10行)
# ============================================================

class EmployeeModel(QObject):
    """员工信息模型 - 使用 qt_property 描述符，零样板代码"""
    name       = qt_property(str, "")
    age        = qt_property(int, 25)
    salary     = qt_property(float, 5000.0)
    department = qt_property(str, "技术部")
    isManager  = qt_property(bool, False)
    level      = qt_property(str, "初级")

    def __init__(self, parent=None):
        super().__init__(parent)


# ============================================================
# 3. 主窗口示例 (完全不变)
# ============================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Employee Manager (Qt Native Binding)")
        self.resize(450, 380)

        self.model = EmployeeModel(self)
        self.binder = QtBinder(self.model)

        central = QWidget()
        self.setCentralWidget(central)
        form = QFormLayout(central)

        self.name_edit = QLineEdit()
        self.age_spin = QSpinBox()
        self.age_spin.setRange(18, 65)
        self.salary_spin = QDoubleSpinBox()
        self.salary_spin.setRange(0, 999999)
        self.salary_spin.setDecimals(2)
        self.dept_combo = QComboBox()
        self.dept_combo.addItems(["技术部", "市场部", "人事部", "财务部"])
        self.manager_check = QCheckBox("是经理")
        self.level_combo = QComboBox()
        self.level_combo.addItems(["初级", "中级", "高级", "专家"])

        form.addRow("姓名:", self.name_edit)
        form.addRow("年龄:", self.age_spin)
        form.addRow("薪资:", self.salary_spin)
        form.addRow("部门:", self.dept_combo)
        form.addRow("经理:", self.manager_check)
        form.addRow("级别:", self.level_combo)

        # 绑定方式完全不变，因为 qt_property 生成的信号名遵循 <name>Changed 约定
        self.binder.bind("name", self.name_edit)
        self.binder.bind("age", self.age_spin,
                         widget_property="value",
                         widget_signal="valueChanged")
        self.binder.bind("salary", self.salary_spin,
                         widget_property="value",
                         widget_signal="valueChanged")
        self.binder.bind("department", self.dept_combo,
                         widget_property="currentText",
                         widget_signal="currentTextChanged")
        self.binder.bind("isManager", self.manager_check,
                         widget_property="checked",
                         widget_signal="toggled")
        self.binder.bind("level", self.level_combo,
                         widget_property="currentText",
                         widget_signal="currentTextChanged")

        btn = QPushButton("测试: 代码设置 name='张三', age=30")
        btn.clicked.connect(lambda: (
            setattr(self.model, 'name', '张三'),
            setattr(self.model, 'age', 30),
        ))
        form.addRow(btn)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())