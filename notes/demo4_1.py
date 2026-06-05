from traitlets import HasTraits, Int, default, validate, observe

class Demo(HasTraits):
    x = Int()

    @default('x')
    def _x_default(self):
        print('1. @default called')
        return 10

    @validate('x')
    def _x_validate(self, proposal):
        print('2. @validate called, proposed value:', proposal['value'])
        return proposal['value'] + 1   # 转换一下

    @observe('x')
    def _x_changed(self, change):
        print('3. @observe called, new value:', change['new'])

# 实例化（未传 x，触发默认值生成、验证、观察）
d = Demo()
print('Final value:', d.x)
print('Final value:', d.x)