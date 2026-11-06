import pandas as pd

class Person:
    def __init__(self):
        self.name = input("Enter Name: ")
        self.age = int(input("Enter Age: "))
        self.exp = int(input("Enter Experience: "))

class Employee(Person):
    def __init__(self):
        super().__init__()
        self.post = input("Enter Post: ")
        self.company_exp = int(input("Enter Company Experience: "))

    def to_dict(self):
        return {
            "Name": self.name,
            "Age": self.age,
            "Experience": self.exp,
            "Post": self.post,
            "Company_Experience": self.company_exp
        }

# Number of employees
n = int(input("How many employees do you want to enter? "))

emp_list = []

for i in range(n):
    print(f"\nEnter details of Employee {i+1}")
    e = Employee()
    emp_list.append(e.to_dict())

# Create DataFrame
df = pd.DataFrame(emp_list)

print("\nDataFrame:")
print(df)