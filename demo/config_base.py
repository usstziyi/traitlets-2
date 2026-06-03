"""
通用配置基类模块
================

提供 ConfigBase 基类，实现 traitlets 的 JSON 序列化/反序列化。
所有需要配置管理的模型都可以继承此类。

使用方式:
    class MyAppConfig(ConfigBase):
        name = Unicode()
        version = Int()

    config = MyAppConfig()
    config.save_to_file("config.json")  # 保存
    config.load_from_file("config.json")  # 加载

Signature: trea cn
"""

import json
import os
from pathlib import Path
from typing import Optional, Any
from traitlets import HasTraits, Unicode, default


class ConfigBase(HasTraits):
    """
    配置基类：提供 JSON 导出/导入功能。

    子类只需定义 traitlets 属性，即可自动获得：
    - to_dict(): 导出为字典
    - from_dict(data): 从字典加载
    - to_json(): 导出为 JSON 字符串
    - from_json(json_str): 从 JSON 字符串加载
    - save_to_file(path): 保存到文件
    - load_from_file(path): 从文件加载
    """

    # 可选：配置文件路径
    config_path = Unicode()

    @default("config_path")
    def _default_config_path(self):
        return ""

    def to_dict(self, include_private: bool = False) -> dict[str, Any]:
        """
        将当前 traitlets 导出为字典。

        Args:
            include_private: 是否包含私有属性（以下划线开头）

        Returns:
            包含所有 traitlets 值的字典
        """
        result = {}
        for name, trait in self.class_traits().items():
            if name == "trait":
                continue
            if not include_private and name.startswith("_"):
                continue
            try:
                result[name] = getattr(self, name)
            except Exception:
                # 如果获取某个属性失败，跳过
                continue
        return result

    def from_dict(self, data: dict[str, Any], strict: bool = False) -> None:
        """
        从字典加载 traitlets 值。

        Args:
            data: 包含配置值的字典
            strict: 严格模式，如果字典中包含不存在的 key 则抛出异常
        """
        if strict:
            for key in data:
                if not self.has_trait(key):
                    raise KeyError(f"未知的配置项: {key}")

        for key, value in data.items():
            if self.has_trait(key):
                setattr(self, key, value)

    def to_json(self, indent: int = 2, **kwargs) -> str:
        """
        将配置导出为 JSON 字符串。

        Args:
            indent: JSON 缩进空格数
            **kwargs: 传递给 json.dumps 的其他参数

        Returns:
            JSON 字符串
        """
        data = self.to_dict()
        return json.dumps(data, indent=indent, ensure_ascii=False, **kwargs)

    def from_json(self, json_str: str) -> None:
        """
        从 JSON 字符串加载配置。

        Args:
            json_str: JSON 字符串
        """
        data = json.loads(json_str)
        self.from_dict(data)

    def save_to_file(self, path: Optional[str] = None, indent: int = 2) -> str:
        """
        保存配置到 JSON 文件。

        Args:
            path: 文件路径，如果不提供则使用 config_path
            indent: JSON 缩进空格数

        Returns:
            实际保存的文件路径
        """
        path = path or self.config_path
        if not path:
            raise ValueError("未指定配置文件路径")

        # 确保目录存在
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        json_str = self.to_json(indent=indent)
        path.write_text(json_str, encoding="utf-8")

        return str(path)

    def load_from_file(self, path: Optional[str] = None) -> str:
        """
        从 JSON 文件加载配置。

        Args:
            path: 文件路径，如果不提供则使用 config_path

        Returns:
            实际加载的文件路径
        """
        path = path or self.config_path
        if not path:
            raise ValueError("未指定配置文件路径")

        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {path}")

        json_str = path.read_text(encoding="utf-8")
        self.from_json(json_str)

        return str(path)

    def load_or_create(self, path: Optional[str] = None) -> bool:
        """
        尝试从文件加载配置，如果文件不存在则创建默认配置并保存。

        Args:
            path: 文件路径

        Returns:
            True 表示从文件加载成功，False 表示创建了新的配置文件
        """
        path = path or self.config_path
        if not path:
            raise ValueError("未指定配置文件路径")

        if Path(path).exists():
            self.load_from_file(path)
            return True
        else:
            self.save_to_file(path)
            return False

    def get_traits_info(self) -> dict:
        """
        获取所有 traitlets 的元数据信息。

        Returns:
            包含每个 traitlets 信息的字典
        """
        info = {}
        for name, trait in self.class_traits().items():
            if name == "trait":
                continue
            info[name] = {
                "type": trait.__class__.__name__,
                "description": trait.metadata.get("description", ""),
                "default": trait.default(),
                **{k: v for k, v in trait.metadata.items() if k not in ("description",)},
            }
        return info

    def __repr__(self):
        data = self.to_dict()
        items = ", ".join(f"{k}={v!r}" for k, v in data.items())
        return f"{self.__class__.__name__}({items})"
