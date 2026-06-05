from traitlets import HasTraits, Int, default, validate, observe, observe

class MyTraits(HasTraits):
    value = Int()

    @default('value')
    def default_value(self):
        print("1. @default executed")
        return 10

    @validate('value')
    def validate_value(self, proposal):
        print("2. @validate executed")
        if proposal['value'] < 0:
            raise TraitError("negative value not allowed")
        return proposal['value']

    @observe('value')
    def observe_value(self, change):
        print("3. @observe executed: old={}, new={}".format(change['old'], change['new']))

# --- 场景1: 对象初始化 ---
obj = MyTraits() 
# x = obj.value
# 输出:
# 1. @default executed
# 2. @validate executed

# --- 场景2: 后续属性修改（赋值）---
obj.value = 20
# 输出:
# 2. @validate executed
# 3. @observe executed: old=10, new=20