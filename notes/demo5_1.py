from traitlets import HasTraits, Int

class Foo(HasTraits):
    x = Int(default_value=42)

f = Foo()
f.x = 999  # 改掉

print(f.x)                                    # 999
print(f.class_traits()["x"].default_value)    # 42  ← 默认值完好