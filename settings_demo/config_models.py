"""
配置模型模块
============

定义应用的配置模型类，基于 ConfigBase 基类。
"""

from traitlets import Int, Unicode, Bool, Dict, default, validate, TraitError
from config_base import ConfigBase


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
    general = Dict().tag(description="通用配置")
    network = Dict().tag(description="网络配置")

    @default("general")
    def _default_general(self):
        return GeneralConfig().to_dict()

    @default("network")
    def _default_network(self):
        return NetworkConfig().to_dict()

    # 从内存中获取配置对象
    def get_general_config(self) -> GeneralConfig:
        """获取通用配置对象"""
        config = GeneralConfig()
        config.from_dict(self.general)
        return config
    
    # 设置配置内存中的通用配置
    def set_general_config(self, config: GeneralConfig):
        """设置通用配置"""
        self.general = config.to_dict()

    # 从内存中获取配置对象
    def get_network_config(self) -> NetworkConfig:
        """获取网络配置对象"""
        config = NetworkConfig()
        config.from_dict(self.network)
        return config
    
    # 设置配置内存中的网络配置
    def set_network_config(self, config: NetworkConfig):
        """设置网络配置"""
        self.network = config.to_dict()
