"""
Demo 5: 完整的 JSON 配置系统
==========================

本教程演示完整的配置管理方案：
1. ConfigBase 基类使用
2. 启动时加载配置文件
3. 运行时修改并自动保存
4. 配置变更实时反映到 UI
5. 完整的设置对话框

运行方式: uv run demo5_config_system.py

配置文件会在首次运行时自动生成到 config.json

Signature: trea cn
"""

import sys
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox, QDoubleSpinBox,
    QCheckBox, QComboBox, QTextEdit, QGroupBox, QFormLayout,
    QFileDialog, QMessageBox, QTabWidget, QListWidget, QSplitter
)
from PySide6.QtCore import Qt, QTimer
from traitlets import (
    HasTraits, Int, Unicode, Float, Bool, List, default, observe, validate, TraitError
)

# 导入配置基类
from config_base import ConfigBase


# ============================================================
# 1. 应用配置模型
# ============================================================

class GeneralConfig(ConfigBase):
    """通用设置"""
    app_name = Unicode().tag(description="应用名称")
    theme = Unicode().tag(description="主题", options=["light", "dark", "system"])
    language = Unicode().tag(description="语言", options=["zh_CN", "en_US", "ja_JP"])
    font_size = Int().tag(description="字体大小", min=8, max=32)
    auto_start = Bool().tag(description="开机自启")

    @default("app_name")
    def _default_app_name(self):
        return "我的应用"

    @default("theme")
    def _default_theme(self):
        return "light"

    @default("language")
    def _default_language(self):
        return "zh_CN"

    @default("font_size")
    def _default_font_size(self):
        return 14

    @default("auto_start")
    def _default_auto_start(self):
        return False


class NetworkConfig(ConfigBase):
    """网络设置"""
    server_url = Unicode().tag(description="服务器地址")
    port = Int().tag(description="端口", min=1, max=65535)
    timeout = Int().tag(description="超时时间(秒)", min=1, max=300)
    retry_count = Int().tag(description="重试次数", min=0, max=10)
    use_proxy = Bool().tag(description="使用代理")
    proxy_url = Unicode().tag(description="代理地址")

    @default("server_url")
    def _default_server_url(self):
        return "https://api.example.com"

    @default("port")
    def _default_port(self):
        return 8080

    @default("timeout")
    def _default_timeout(self):
        return 30

    @default("retry_count")
    def _default_retry_count(self):
        return 3

    @default("use_proxy")
    def _default_use_proxy(self):
        return False

    @default("proxy_url")
    def _default_proxy_url(self):
        return ""

    @validate("port")
    def _validate_port(self, proposal):
        value = proposal["value"]
        if value < 1 or value > 65535:
            raise TraitError("端口必须在 1-65535 之间")
        return value


class AppConfig(ConfigBase):
    """
    总配置类：组合多个子配置。

    这是实际应用中的推荐做法：将配置按功能拆分为多个类，
    然后用一个总配置类组合起来。
    """
    general = Unicode().tag(description="通用配置(JSON)")
    network = Unicode().tag(description="网络配置(JSON)")

    @default("general")
    def _default_general(self):
        return json.dumps(GeneralConfig().to_dict(), ensure_ascii=False)

    @default("network")
    def _default_network(self):
        return json.dumps(NetworkConfig().to_dict(), ensure_ascii=False)

    # 便捷方法
    def get_general_config(self) -> GeneralConfig:
        """获取通用配置对象"""
        config = GeneralConfig()
        config.from_json(self.general)
        return config

    def set_general_config(self, config: GeneralConfig):
        """设置通用配置"""
        self.general = config.to_json(indent=2)

    def get_network_config(self) -> NetworkConfig:
        """获取网络配置对象"""
        config = NetworkConfig()
        config.from_json(self.network)
        return config

    def set_network_config(self, config: NetworkConfig):
        """设置网络配置"""
        self.network = config.to_json(indent=2)


# ============================================================
# 2. 设置对话框
# ============================================================

class SettingsDialog(QMainWindow):
    """设置对话框"""

    def __init__(self, config: AppConfig):
        super().__init__()
        self.setWindowTitle("设置")
        self.resize(550, 450)

        self.config = config
        self.general_config = config.get_general_config()
        self.network_config = config.get_network_config()

        # 创建标签页
        tab_widget = QTabWidget()
        tab_widget.addTab(self._create_general_tab(), "通用设置")
        tab_widget.addTab(self._create_network_tab(), "网络设置")
        tab_widget.addTab(self._create_json_tab(), "JSON 预览")

        # 按钮
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self._save)
        self.reset_btn = QPushButton("恢复默认")
        self.reset_btn.clicked.connect(self._reset)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.close)

        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addWidget(self.cancel_btn)

        # 布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(tab_widget)
        main_layout.addLayout(btn_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def _create_general_tab(self):
        """创建通用设置标签页"""
        tab = QWidget()
        layout = QFormLayout()

        self.name_input = QLineEdit(self.general_config.app_name)
        layout.addRow("应用名称:", self.name_input)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark", "system"])
        idx = self.theme_combo.findText(self.general_config.theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
        layout.addRow("主题:", self.theme_combo)

        self.lang_combo = QComboBox()
        lang_map = {"zh_CN": "简体中文", "en_US": "English", "ja_JP": "日本語"}
        for key, label in lang_map.items():
            self.lang_combo.addItem(label, key)
        idx = self.lang_combo.findData(self.general_config.language)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        layout.addRow("语言:", self.lang_combo)

        self.font_spinbox = QSpinBox()
        self.font_spinbox.setRange(8, 32)
        self.font_spinbox.setValue(self.general_config.font_size)
        layout.addRow("字体大小:", self.font_spinbox)

        self.autostart_check = QCheckBox("开机自动启动")
        self.autostart_check.setChecked(self.general_config.auto_start)
        layout.addRow("", self.autostart_check)

        tab.setLayout(layout)
        return tab

    def _create_network_tab(self):
        """创建网络设置标签页"""
        tab = QWidget()
        layout = QFormLayout()

        self.url_input = QLineEdit(self.network_config.server_url)
        layout.addRow("服务器地址:", self.url_input)

        self.port_spinbox = QSpinBox()
        self.port_spinbox.setRange(1, 65535)
        self.port_spinbox.setValue(self.network_config.port)
        layout.addRow("端口:", self.port_spinbox)

        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(1, 300)
        self.timeout_spinbox.setValue(self.network_config.timeout)
        layout.addRow("超时时间(秒):", self.timeout_spinbox)

        self.retry_spinbox = QSpinBox()
        self.retry_spinbox.setRange(0, 10)
        self.retry_spinbox.setValue(self.network_config.retry_count)
        layout.addRow("重试次数:", self.retry_spinbox)

        self.proxy_check = QCheckBox("使用代理")
        self.proxy_check.setChecked(self.network_config.use_proxy)
        self.proxy_check.toggled.connect(self._on_proxy_toggle)
        layout.addRow("", self.proxy_check)

        self.proxy_input = QLineEdit(self.network_config.proxy_url)
        self.proxy_input.setEnabled(self.network_config.use_proxy)
        layout.addRow("代理地址:", self.proxy_input)

        tab.setLayout(layout)
        return tab

    def _create_json_tab(self):
        """创建 JSON 预览标签页"""
        tab = QWidget()
        layout = QVBoxLayout()

        self.json_display = QTextEdit()
        self.json_display.setReadOnly(True)
        self.json_display.setStyleSheet("font-family: monospace; font-size: 12px;")
        layout.addWidget(self.json_display)

        tab.setLayout(layout)
        self._update_json_preview()
        return tab

    def _on_proxy_toggle(self, checked):
        self.proxy_input.setEnabled(checked)

    def _update_json_preview(self):
        """更新 JSON 预览"""
        data = {
            "general": self.general_config.to_dict(),
            "network": self.network_config.to_dict(),
        }
        self.json_display.setText(json.dumps(data, indent=2, ensure_ascii=False))

    def _collect_settings(self):
        """从 UI 收集设置"""
        # 通用设置
        self.general_config.app_name = self.name_input.text()
        self.general_config.theme = self.theme_combo.currentText()
        lang_data = self.lang_combo.currentData()
        self.general_config.language = lang_data if lang_data else "zh_CN"
        self.general_config.font_size = self.font_spinbox.value()
        self.general_config.auto_start = self.autostart_check.isChecked()

        # 网络设置
        self.network_config.server_url = self.url_input.text()
        self.network_config.port = self.port_spinbox.value()
        self.network_config.timeout = self.timeout_spinbox.value()
        self.network_config.retry_count = self.retry_spinbox.value()
        self.network_config.use_proxy = self.proxy_check.isChecked()
        self.network_config.proxy_url = self.proxy_input.text()

    def _save(self):
        """保存设置"""
        self._collect_settings()
        self.config.set_general_config(self.general_config)
        self.config.set_network_config(self.network_config)
        self._update_json_preview()
        QMessageBox.information(self, "提示", "设置已保存！")

    def _reset(self):
        """恢复默认设置"""
        reply = QMessageBox.question(
            self, "确认", "确定要恢复默认设置吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.general_config = GeneralConfig()
            self.network_config = NetworkConfig()
            self.config.set_general_config(self.general_config)
            self.config.set_network_config(self.network_config)
            self._refresh_ui()
            self._update_json_preview()

    def _refresh_ui(self):
        """刷新 UI 显示"""
        self.name_input.setText(self.general_config.app_name)
        idx = self.theme_combo.findText(self.general_config.theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
        idx = self.lang_combo.findData(self.general_config.language)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        self.font_spinbox.setValue(self.general_config.font_size)
        self.autostart_check.setChecked(self.general_config.auto_start)

        self.url_input.setText(self.network_config.server_url)
        self.port_spinbox.setValue(self.network_config.port)
        self.timeout_spinbox.setValue(self.network_config.timeout)
        self.retry_spinbox.setValue(self.network_config.retry_count)
        self.proxy_check.setChecked(self.network_config.use_proxy)
        self.proxy_input.setText(self.network_config.proxy_url)
        self.proxy_input.setEnabled(self.network_config.use_proxy)


# ============================================================
# 3. 主窗口
# ============================================================

class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self, config: AppConfig):
        super().__init__()
        self.setWindowTitle("Demo 5: 配置系统")
        self.resize(600, 450)

        self.config = config
        self.config_file = "config.json"

        # 尝试加载配置
        self._load_config()

        # UI
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)

        self.config_display = QTextEdit()
        self.config_display.setReadOnly(True)

        # 按钮
        self.settings_btn = QPushButton("打开设置")
        self.settings_btn.clicked.connect(self._open_settings)

        self.export_btn = QPushButton("导出配置")
        self.export_btn.clicked.connect(self._export_config)

        self.import_btn = QPushButton("导入配置")
        self.import_btn.clicked.connect(self._import_config)

        self.reset_btn = QPushButton("重置配置")
        self.reset_btn.clicked.connect(self._reset_config)

        # 布局
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.settings_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.import_btn)
        btn_layout.addWidget(self.reset_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("当前配置概要:"))
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(QLabel("完整配置 (JSON):"))
        main_layout.addWidget(self.config_display)
        main_layout.addLayout(btn_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # 更新显示
        self._update_display()

    def _load_config(self):
        """加载配置"""
        if Path(self.config_file).exists():
            self.config.load_from_file(self.config_file)
            print(f"配置已从 {self.config_file} 加载")
        else:
            # 首次运行，创建默认配置
            self.config.save_to_file(self.config_file)
            print(f"默认配置已保存到 {self.config_file}")

    def _update_display(self):
        """更新显示"""
        general = self.config.get_general_config()
        network = self.config.get_network_config()

        self.status_label.setText(
            f"应用名称: {general.app_name}\n"
            f"主题: {general.theme} | 语言: {general.language} | 字体: {general.font_size}px\n"
            f"服务器: {network.server_url}:{network.port}\n"
            f"超时: {network.timeout}s | 重试: {network.retry_count}次"
        )

        full_config = {
            "general": general.to_dict(),
            "network": network.to_dict(),
        }
        self.config_display.setText(json.dumps(full_config, indent=2, ensure_ascii=False))

    def _open_settings(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self.config)
        dialog.exec()
        # 保存并更新显示
        self.config.save_to_file(self.config_file)
        self._update_display()

    def _export_config(self):
        """导出配置到指定位置"""
        path, _ = QFileDialog.getSaveFileName(
            self, "导出配置", "", "JSON Files (*.json)"
        )
        if path:
            self.config.save_to_file(path)
            QMessageBox.information(self, "成功", f"配置已导出到:\n{path}")

    def _import_config(self):
        """从文件导入配置"""
        path, _ = QFileDialog.getOpenFileName(
            self, "导入配置", "", "JSON Files (*.json)"
        )
        if path:
            try:
                self.config.load_from_file(path)
                self.config.save_to_file(self.config_file)
                self._update_display()
                QMessageBox.information(self, "成功", "配置已导入！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导入配置失败:\n{e}")

    def _reset_config(self):
        """重置配置"""
        reply = QMessageBox.question(
            self, "确认", "确定要重置为默认配置吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # 创建新的默认配置
            default_config = AppConfig()
            default_config.save_to_file(self.config_file)
            self.config.load_from_file(self.config_file)
            self._update_display()
            QMessageBox.information(self, "提示", "配置已重置为默认值")


# ============================================================
# 4. 独立测试：ConfigBase 功能演示
# ============================================================

def test_config_base():
    """测试 ConfigBase 的所有功能"""
    print("=" * 60)
    print("ConfigBase 功能测试")
    print("=" * 60)

    from config_base import ConfigBase
    from traitlets import Int, Unicode, Float, Bool, default

    class TestConfig(ConfigBase):
        name = Unicode()
        version = Int()
        rate = Float()
        enabled = Bool()

        @default("name")
        def _default_name(self):
            return "测试配置"

        @default("version")
        def _default_version(self):
            return 1

        @default("rate")
        def _default_rate(self):
            return 0.95

        @default("enabled")
        def _default_enabled(self):
            return True

    # 创建配置
    config = TestConfig()
    print("\n1. 初始配置:")
    print(f"   {config}")

    # 导出为字典
    print("\n2. 导出为字典:")
    print(f"   {config.to_dict()}")

    # 导出为 JSON
    print("\n3. 导出为 JSON:")
    print(config.to_json())

    # 修改并保存
    config.name = "修改后的配置"
    config.version = 2
    config.rate = 0.88

    print("\n4. 修改后保存:")
    config.save_to_file("test_config.json")
    print("   已保存到 test_config.json")

    # 从文件加载到新对象
    new_config = TestConfig()
    new_config.load_from_file("test_config.json")
    print(f"\n5. 从文件加载:")
    print(f"   {new_config}")

    # 从 JSON 字符串加载
    json_str = '{"name": "JSON加载", "version": 3, "rate": 0.77, "enabled": false}'
    config.from_json(json_str)
    print(f"\n6. 从 JSON 字符串加载:")
    print(f"   {config}")

    # 获取元数据
    print("\n7. 配置项元数据:")
    for name, info in config.get_traits_info().items():
        print(f"   {name}: {info}")

    # 从目录中删除测试文件
    # Path("test_config.json").unlink(missing_ok=True)

    print("\n" + "=" * 60)
    print("ConfigBase 测试完成！")
    print("=" * 60)


# ============================================================
# 主函数
# ============================================================

def main():
    # 首先运行配置测试
    # test_config_base()

    # 然后启动 GUI
    print("\n启动 GUI 应用...\n")

    app = QApplication(sys.argv)

    # 创建配置（会在启动时自动加载 config.json）
    config = AppConfig(config_path="config.json")

    window = MainWindow(config)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
