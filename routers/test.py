my_dict = {}

data = {"first": "a", "second": "b"}

for key, value in data.items():
    my_dict[str(key)] = value

print(my_dict)

class MyClass:
    def __init__(self, value):
        self.value = value

# Create an instance of MyClass
my_instance = MyClass(42)

# Add a new variable to the instance
my_instance.new_variable = 10

# Access the new variable
print(my_instance.new_variable)  # Output: 10