"""
ConfigBase 功能测试
==================

独立测试脚本，不依赖 GUI，验证 ConfigBase 的 JSON 序列化/反序列化功能。

运行方式: python test_config_base.py
"""

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


def main():
    """测试 ConfigBase 的所有功能"""
    print("=" * 60)
    print("ConfigBase 功能测试")
    print("=" * 60)

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

    print("\n" + "=" * 60)
    print("ConfigBase 测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
