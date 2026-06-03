# PySide6 + Traitlets 结合教程

由浅入深学习如何将 PySide6 控件与 traitlets 配置管理结合，最终实现以 JSON 文件导出和启动加载的完整配置系统。

## 环境要求

- Python >= 3.10
- uv（Python 包管理工具）

## 安装依赖

```bash
uv sync
```

## 教程结构

本教程包含 5 个由浅入深的示例，建议按顺序学习：

### Demo 1: Traitlets 基础入门

```bash
uv run demo1_traitlets_basics.py
```

**学习内容：**

- `HasTraits` 类与基本类型（`Int`、`Unicode`、`Float`、`Bool`）
- 默认值生成（`@default` 装饰器）
- 观察者模式（`@observe` 装饰器）
- 输入验证（`@validate` 装饰器）
- 交叉验证与 `hold_trait_notifications`
- 元数据标注（`.tag()` 方法）

### Demo 2: Traitlets 与 PySide6 基础集成

```bash
uv run demo2_pyside6_basic.py
```

**学习内容：**

- traitlets 变化 -> 自动更新 UI（`@observe` + Qt 控件）
- UI 事件 -> 更新 traitlets（信号连接）
- 单向绑定与双向联动模式

### Demo 3: 控件与 Traitlets 双向绑定

```bash
uv run demo3_binding.py
```

**学习内容：**

- 通用 `TraitletsBinder` 绑定器实现
- 支持多种控件：`QLineEdit`、`QSpinBox`、`QDoubleSpinBox`、`QCheckBox`、`QComboBox`、`QSlider`
- 便捷绑定函数：`bind_text()`、`bind_int()`、`bind_float()`、`bind_bool()`
- 完整表单场景示例

### Demo 4: 复杂控件与自定义验证

```bash
uv run demo4_complex_widgets.py
```

**学习内容：**

- `List` 和 `Dict` 类型 traitlets
- 复杂控件集成（`QListWidget`、`QTableWidget`）
- 多字段联动验证（密码确认、年龄限制等）
- 动态表单生成（基于配置定义自动生成 UI）

### Demo 5: 完整的 JSON 配置系统

```bash
uv run demo5_config_system.py
```

**学习内容：**

- `ConfigBase` 配置基类设计
- JSON 序列化/反序列化（`to_dict`、`from_dict`、`to_json`、`from_json`）
- 文件持久化（`save_to_file`、`load_from_file`）
- 启动自动加载：`load_or_create()`
- 配置组合模式（多个子配置聚合）
- 设置对话框、配置导入/导出功能

## 核心模块

### config\_base.py

通用的配置基类，所有需要配置管理的模型都可以继承此类：

```python
from config_base import ConfigBase
from traitlets import Unicode, Int, default

class MyAppConfig(ConfigBase):
    name = Unicode()
    version = Int()

    @default("name")
    def _default_name(self):
        return "MyApp"

    @default("version")
    def _default_version(self):
        return 1

# 使用
config = MyAppConfig()
config.load_or_create("config.json")  # 启动时加载或创建
config.name = "NewName"
config.save_to_file("config.json")    # 运行时保存
```

### 项目结构

```
├── pyproject.toml            # 项目配置（uv 依赖管理）
├── config_base.py             # 通用配置基类
├── demo1_traitlets_basics.py  # Demo 1: 基础入门
├── demo2_pyside6_basic.py     # Demo 2: PySide6 集成
├── demo3_binding.py           # Demo 3: 双向绑定
├── demo4_complex_widgets.py   # Demo 4: 复杂控件
└── demo5_config_system.py     # Demo 5: 完整配置系统
```

## 参考资料

- [Traitlets 官方文档](https://traitlets.readthedocs.io/)
- [PySide6 官方文档](https://doc.qt.io/qtforpython/)

***

Signature: trae cn
