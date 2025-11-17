

class Parent(object):

    class_attr = 'something'
    
    def __init__(self):
        self.numAvg = 4
     
class Child(Parent):
    
    def __init__(self):
        Parent.__init__()
        self.my_attribute = 5     
c = Child()
p = Parent()

print('child sees numAvg before changing as: {}'.format(c.numAvg))
p.numAvg = 8
print('child sees numAvg after changing as: {}'.format(c.numAvg))


C:\Users\Erik\AppData\Local\Programs\Python\Python35-32\Scripts\;C:\Users\Erik\AppData\Local\Programs\Python\Python35-32\