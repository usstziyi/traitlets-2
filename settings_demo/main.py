"""
Demo 5: 完整的 JSON 配置系统
==========================

本教程演示完整的配置管理方案：
1. ConfigBase 基类使用
2. 启动时加载配置文件
3. 运行时修改并自动保存
4. 配置变更实时反映到 UI
5. 完整的设置对话框

文件结构:
    config_base.py       - 配置基类 (to_dict/from_dict/JSON 序列化等)
    config_models.py     - 配置模型类 (GeneralConfig, NetworkConfig, AppConfig)
    settings_dialog.py   - 设置对话框 UI
    main_window.py       - 主窗口 UI
    demo5_config_system.py - 入口文件 (本文件)

运行方式: uv run demo5_config_system.py

配置文件会在首次运行时自动生成到 config.json

Signature: trea cn
"""

import sys
from PySide6.QtWidgets import QApplication

from config_models import AppConfig
from main_window import MainWindow


def main():
    # 如需独立测试 ConfigBase，运行: python test_config_base.py

    app = QApplication(sys.argv)
    # 创建配置（会在启动时自动加载 config.json）
    config = AppConfig(config_path="config.json")
    window = MainWindow(config)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
