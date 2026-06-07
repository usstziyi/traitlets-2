"""
主窗口模块
==========

提供应用主窗口 UI，包括配置的加载、保存、导入、导出功能。
"""

import json
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QFileDialog, QMessageBox
)

from config_models import AppConfig
from settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self, config: AppConfig):
        super().__init__()
        self.setWindowTitle("Demo 5: 配置系统")
        self.resize(600, 450)

        self.config = config
        self.config_file = "config.json"

        # 加载配置到内存 self.config
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

        # 把默认配置显示在 UI
        self._update_display()

    def _load_config(self):
        # 第二次运行，从配置文件加载配置到内存 self.config
        if Path(self.config_file).exists():
            self.config.load_from_file(self.config_file)
            print(f"配置已从 {self.config_file} 加载")
        else:
            # 首次运行，创建默认配置并保存到文件 self.config_file
            self.config.save_to_file(self.config_file)
            print(f"默认配置已保存到 {self.config_file}")

    def _update_display(self):
        # 此时 self.config 已经加载了配置，所以可以直接获取配置
        general = self.config.get_general_config()
        network = self.config.get_network_config()

        self.status_label.setText(
            f"应用名称: {general.app_name}\n"
            f"主题: {general.theme} | 语言: {general.language} | 字体: {general.font_size}px\n"
            f"服务器: {network.server_url}:{network.port}\n"
            f"超时: {network.timeout}s | 重试: {network.retry_count}次"
        )

        # 通过 general 和 network 对象能够拿到内部的属性值，而不是一个长的字符串
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
            # 创建了一个 新的实例 ，所有 trait 都是默认值。
            default_config = AppConfig()
            default_config.save_to_file(self.config_file)
            self.config.load_from_file(self.config_file)
            # self.config.load_from_dict(default_config.to_dict())
            self._update_display()
            QMessageBox.information(self, "提示", "配置已重置为默认值")
