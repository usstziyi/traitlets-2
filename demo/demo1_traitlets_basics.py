"""
Demo 1: Traitlets 基础入门
=========================

本教程介绍 traitlets 的核心功能：
1. HasTraits 类与基本类型
2. 默认值（@default）
3. 观察者模式（@observe）
4. 验证器（@validate）

运行方式: uv run demo1_traitlets_basics.py

Signature: trea cn
"""

from traitlets import HasTraits, Int, Unicode, Float, Bool, default, observe, validate, TraitError
from traitlets import Undefined

# ============================================================
# 1. 基础: 定义带有 traitlets 的类
# ============================================================

class Person(HasTraits):
    """最简单的 traitlets 类"""
    name = Unicode()
    age = Int()
    height = Float()
    is_student = Bool()


def test_basic():
    print("=" * 60)
    print("1. 基础 traitlets 使用")
    print("=" * 60)

    person = Person(
        name="张三",
        age=25,
        height=175.5,
        is_student=True
    )
    print(f"姓名: {person.name}")
    print(f"年龄: {person.age}")
    print(f"身高: {person.height}")
    print(f"是否学生: {person.is_student}")

    # traitlets 会进行类型检查
    try:
        person.age = "not_an_int"
    except TraitError as e:
        print(f"类型检查生效: {e}")

    print()


# ============================================================
# 2. 默认值: 使用 @default 装饰器
# ============================================================

class ConfigurablePerson(HasTraits):
    """带有默认值的 traitlets 类"""
    name = Unicode()
    age = Int()
    language = Unicode()

    @default("name")
    def _default_name(self):
        return "匿名用户"

    @default("age")
    def _default_age(self):
        return 18

    @default("language")
    def _default_language(self):
        return "中文"


def test_defaults():
    print("=" * 60)
    print("2. 默认值 (@default)")
    print("=" * 60)

    # 不传任何参数时使用默认值
    person = ConfigurablePerson()
    print(f"默认值 - 姓名: {person.name}, 年龄: {person.age}, 语言: {person.language}")

    # 可以覆盖部分默认值
    person2 = ConfigurablePerson(name="李四", age=30)
    print(f"部分覆盖 - 姓名: {person2.name}, 年龄: {person2.age}, 语言: {person2.language}")

    print()


# ============================================================
# 3. 观察者: 使用 @observe 监听属性变化
# ============================================================

class ObservablePerson(HasTraits):
    """演示观察者模式的类"""
    name = Unicode()
    age = Int()
    mood = Unicode()

    @default("mood")
    def _default_mood(self):
        return "平静"

    @observe("age")
    def _on_age_change(self, change):
        old_val = change["old"]
        new_val = change["new"]

        print(f"old_val is None: {old_val is None}")
        print(f"old_val is Undefined: {old_val is Undefined}")

        print(f"  [观察者] 年龄从 {old_val} 变为 {new_val}")
        if new_val >= 60:
            self.mood = "退休生活"
        elif new_val >= 18:
            self.mood = "成年"
        else:
            self.mood = "未成年"

    @observe("name")
    def _on_name_change(self, change):
        print(f"  [观察者] 姓名从 '{change['old']}' 变为 '{change['new']}'")


def test_observe():
    print("=" * 60)
    print("3. 观察者模式 (@observe)")
    print("=" * 60)

    # 构造函数最后会触发观察者方法
    person = ObservablePerson(name="张三", age=10)
    print(f"初始状态: {person.name}, {person.age}岁, 心情: {person.mood}")

 

    # # 实验B：先创建再赋值
    # person_b = ObservablePerson()          # 此时 trait 已初始化为默认值
    # person_b.age = 10                       # old 应该是 0
    # person_b.name = "张三"                   # old 应该是 ''

    # print("\n修改年龄为 20:")
    # person.age = 20
    # print(f"当前状态: {person.name}, {person.age}岁, 心情: {person.mood}")

    # print("\n修改年龄为 65:")
    # person.age = 65
    # print(f"当前状态: {person.name}, {person.age}岁, 心情: {person.mood}")

    # print("\n修改姓名:")
    # person.name = "张三丰"
    # print()


# ============================================================
# 4. 验证器: 使用 @validate 验证输入值
# ============================================================

class ValidatedPerson(HasTraits):
    """带有验证器的 traitlets 类"""
    name = Unicode()
    age = Int()
    email = Unicode()

    @validate("age")
    def _validate_age(self, proposal):
        value = proposal["value"]
        if value < 0:
            raise TraitError("年龄不能为负数")
        if value > 150:
            raise TraitError("年龄不能超过 150")
        return value

    @validate("email")
    def _validate_email(self, proposal):
        value = proposal["value"]
        if "@" not in value:
            raise TraitError("邮箱格式不正确，必须包含 @")
        return value


def test_validate():
    print("=" * 60)
    print("4. 验证器 (@validate)")
    print("=" * 60)

    person = ValidatedPerson(name="王五", age=25, email="wangwu@example.com")
    print(f"创建成功: {person.name}, {person.age}, {person.email}")

    print("\n尝试设置非法年龄:")
    try:
        person.age = -1
    except TraitError as e:
        print(f"  验证失败: {e}")

    print("\n尝试设置非法邮箱:")
    try:
        person.email = "invalid_email"
    except TraitError as e:
        print(f"  验证失败: {e}")

    print()


# ============================================================
# 5. 交叉验证: 多个属性之间的关联验证
# ============================================================

class CrossValidatedProfile(HasTraits):
    """演示交叉验证的类"""
    min_value = Int()
    max_value = Int()

    @validate("min_value")
    def _validate_min_value(self, proposal):
        value = proposal["value"]
        if value > self.max_value:
            raise TraitError("min_value 不能大于 max_value")
        return value

    @validate("max_value")
    def _validate_max_value(self, proposal):
        value = proposal["value"]
        if value < self.min_value:
            raise TraitError("max_value 不能小于 min_value")
        return value


def test_cross_validate():
    print("=" * 60)
    print("5. 交叉验证")
    print("=" * 60)

    profile = CrossValidatedProfile(min_value=0, max_value=100)
    print(f"初始: min={profile.min_value}, max={profile.max_value}")

    print("\n修改 min_value 为 50 (合法):")
    profile.min_value = 50
    print(f"当前: min={profile.min_value}, max={profile.max_value}")

    print("\n尝试设置 min_value > max_value (非法):")
    try:
        profile.min_value = 150
    except TraitError as e:
        print(f"  验证失败: {e}")

    print("\n同时修改两个值 (使用 hold_trait_notifications):")
    with profile.hold_trait_notifications():
        profile.min_value = 10
        profile.max_value = 200
    print(f"  批量修改后: min={profile.min_value}, max={profile.max_value}")

    print()


# ============================================================
# 6. 元数据: 给 traitlets 添加自定义元数据
# ============================================================

class MetaPerson(HasTraits):
    """演示元数据的类"""
    name = Unicode().tag(description="用户姓名", category="基本信息")
    age = Int().tag(description="用户年龄", min=0, max=150, category="基本信息")
    score = Float().tag(description="用户得分", min=0.0, max=100.0, category="评分")

    def print_traits_info(self):
        for trait_name, trait_obj in self.class_traits().items():
            if trait_name == "trait":
                continue
            desc = trait_obj.metadata.get("description", "无描述")
            category = trait_obj.metadata.get("category", "未分类")
            print(f"  {trait_name}: {desc} (分类: {category})")


def test_metadata():
    print("=" * 60)
    print("6. 元数据 (.tag())")
    print("=" * 60)

    person = MetaPerson(name="赵六", age=30, score=95.5)
    print("属性信息:")
    person.print_traits_info()

    print()


# ============================================================
if __name__ == "__main__":
    # print("\n" + "=" * 60)
    # print("  Traitlets 基础入门教程")
    # print("=" * 60 + "\n")

    # test_basic()
    # test_defaults()
    test_observe()
    # test_validate()
    # test_cross_validate()
    # test_metadata()

    # print("=" * 60)
    # print("  恭喜！你已经了解了 traitlets 的基础知识")
    # print("  接下来请查看 demo2，学习如何与 PySide6 结合")
    # print("=" * 60)
