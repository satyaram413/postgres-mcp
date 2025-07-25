class SomeClass:
    def __init__(self):
        self.dispatcher = "Some Value"
    
    def change_value(self):
        self.dispatcher = "Not this"
        return self.dispatcher

a= SomeClass()
print(a.dispatcher)
print(a.change_value())
print(a.dispatcher)