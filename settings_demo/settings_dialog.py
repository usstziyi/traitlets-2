"""
设置对话框模块
==============

提供完整的设置对话框 UI。
"""

import json
from socketserver import DatagramRequestHandler
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox,
    QCheckBox, QComboBox, QTextEdit, QFormLayout,
    QTabWidget, QMessageBox
)

from config_models import AppConfig, GeneralConfig, NetworkConfig


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, config: AppConfig):
        super().__init__()
        self.setWindowTitle("设置")
        self.resize(550, 450)

        self.config = config
        # 从内存中获取配置对象
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
        self.setLayout(main_layout)

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
