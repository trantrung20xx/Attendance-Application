class Wrapper:
    def __init__(self, value):
        self.value = value

def pass_by_refer(variable):
    variable.value += 10

a = Wrapper(10)

print(a.value)

pass_by_refer(a)

print(a.value)  # Output 20
