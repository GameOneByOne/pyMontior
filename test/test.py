


class test:
    def __init__(self):
        pass

    def desc(func):
        def w(*args, **kwargs):
            print(len(args))
            args[0].hello()
            print(args[1])
            func(*args, **kwargs)
            print("func after")
        return w

    def hello(self):
        print("hello")

    @desc
    def func(self,a,b):
        print(" I am A ")


a = test()

a.func(1,2)

