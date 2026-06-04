import sys
from typing import Any, Callable, Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox, QDoubleSpinBox,
    QCheckBox, QComboBox, QTextEdit, QGroupBox, QFormLayout,
    QMessageBox
)
from PySide6.QtCore import Qt, Signal, QObject, Property


# ============================================================
# 1. 通用 Binder 类 (Qt 原生信号槽版本)
# ============================================================

class QtBinder:
    """
    Qt Property 与 PySide6 控件的双向绑定器。
    
    使用方式:
        binder = QtBinder(model)
        binder.bind("name", name_input)
        binder.bind("age", age_spinbox)
    """

    def __init__(self, model: QObject):
        self.model = model
        self._bindings = {}
        # 防止循环更新的标志位
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
        """
        绑定一个 Qt Property 到 UI 控件。

        Args:
            prop_name: Model 中的 Property 名称
            widget: PySide6 控件
            widget_property: 控件属性名 (如 "text", "value", "checked")
            widget_signal: 控件信号名 (如 "textChanged", "valueChanged", "toggled")
            to_widget_func: model -> widget 的值转换函数
            from_widget_func: widget -> model 的值转换函数
        """
        # ① 读取初始值并写入控件
        initial_value = self.model.property(prop_name)
        if to_widget_func:
            initial_value = to_widget_func(initial_value)
        self._set_widget_value(widget, widget_property, initial_value)

        # ② 连接 widget -> model (用户操作控件时更新模型)
        signal = getattr(widget, widget_signal)
        
        def on_widget_changed(value):
            if self._updating:
                return
            converted = from_widget_func(value) if from_widget_func else value
            self.model.setProperty(prop_name, converted)

        signal.connect(on_widget_changed)

        # ③ 连接 model -> widget (模型变化时更新控件)
        # Qt Property 的 notify 信号命名约定: <prop_name>Changed
        notify_signal_name = f"{prop_name}Changed"
        notify_signal = getattr(self.model, notify_signal_name, None)
        
        if notify_signal is None:
            raise AttributeError(
                f"Model '{type(self.model).__name__}' 缺少通知信号 '{notify_signal_name}'。"
                f"请确保 Property 定义了 notify=<signal>"
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

        # ④ 记录绑定关系
        self._bindings[prop_name] = {
            "widget": widget,
            "property": widget_property,
        }

    @staticmethod
    def _set_widget_value(widget: Any, prop_name: str, value: Any):
        """通过 setter 方法安全地设置控件值"""
        setter_name = f"set{prop_name[0].upper()}{prop_name[1:]}"
        setter = getattr(widget, setter_name, None)
        if callable(setter):
            setter(value)
        else:
            setattr(widget, prop_name, value)
"""
model.age = 30                           ← 外部代码赋值
       │
       ▼
EmployeeModel.age.setter(30)             ← 触发 @Property 的 setter
       │
       ▼
if self._age != 30:                      ← 🔑 等值判断（防循环关键）
    self._age = 30
    self.ageChanged.emit()               ← 发射 Qt notify 信号
       │
       ▼
on_model_changed()                       ← Binder 中注册的槽函数（闭包/lambda）
       │
       ▼
if self._updating:                       ← 🔑 反向更新锁检查
    return                                  如果正在处理 Widget→Model，直接跳过
       │
       ▼
self._updating = True                    ← 加锁，防止接下来的 setValue 触发 Widget→Model
       │
       ▼
widget_value = to_widget_func(30)        ← 可选的值转换（如 int → str）
       │
       ▼
spinBox.setValue(widget_value)           ← 写入 UI 控件
       │
       ▼
self._updating = False                   ← 解锁
"""

# ============================================================
# 2. Employee Model (纯 Qt 实现)
# ============================================================

class EmployeeModel(QObject):
    """
    员工信息模型 - 使用 Qt Property + Signal 替代 traitlets
    
    每个属性需要三件套:
      1. 内部存储变量 (_xxx)
      2. 通知信号 (xxxChanged)
      3. Property 声明 (含 getter/setter/notify)
    """

    # --- 通知信号 ---
    nameChanged = Signal()
    ageChanged = Signal()
    salaryChanged = Signal()
    departmentChanged = Signal()
    isManagerChanged = Signal()
    levelChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # 内部存储
        self._name = ""
        self._age = 25
        self._salary = 5000.0
        self._department = "技术部"
        self._is_manager = False
        self._level = "初级"

    # --- name ---
    @Property(str, notify=nameChanged)
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if self._name != value:
            self._name = value
            self.nameChanged.emit()

    # --- age ---
    @Property(int, notify=ageChanged)
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int):
        if self._age != value:
            self._age = value
            self.ageChanged.emit()

    # --- salary ---
    @Property(float, notify=salaryChanged)
    def salary(self) -> float:
        return self._salary

    @salary.setter
    def salary(self, value: float):
        if self._salary != value:
            self._salary = value
            self.salaryChanged.emit()

    # --- department ---
    @Property(str, notify=departmentChanged)
    def department(self) -> str:
        return self._department

    @department.setter
    def department(self, value: str):
        if self._department != value:
            self._department = value
            self.departmentChanged.emit()

    # --- is_manager ---
    @Property(bool, notify=isManagerChanged)
    def isManager(self) -> bool:
        return self._is_manager

    @isManager.setter
    def isManager(self, value: bool):
        if self._is_manager != value:
            self._is_manager = value
            self.isManagerChanged.emit()

    # --- level ---
    @Property(str, notify=levelChanged)
    def level(self) -> str:
        return self._level

    @level.setter
    def level(self, value: str):
        if self._level != value:
            self._level = value
            self.levelChanged.emit()


# ============================================================
# 3. 主窗口示例
# ============================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Employee Manager (Qt Native Binding)")
        self.resize(450, 380)

        # 创建模型和绑定器
        self.model = EmployeeModel(self)
        self.binder = QtBinder(self.model)

        # 构建 UI
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

        # 执行绑定
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

        # 演示: 代码修改模型 → UI 自动同步
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