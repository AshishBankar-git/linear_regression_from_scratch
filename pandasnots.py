# series datastructres
import pandas as pd
s = pd.Series([10,25,30,55,85,'abc'])
'''print(s)
# multiple opeartions 
print(s.dtype)
print(s.values)
print(s.index)
print(s.name)
print(s)
print(s.name)
print(s)'''
'''print(s[4])
print(s[0])
print(s[2:5])
print(s.iloc[3])
print(s.iloc[[1,5,3]])'''
'''s.name = "claoriars"
new_index = ["apple ","grapes","waterlemon","banana","lemon","mango"]
s.index = new_index
print(s['grapes'])
v = s.loc['grapes':'waterlemon']
print(v)'''
# series uisng dictories 
fruits_calories = {
    "apple": 52,
    "banana": 89,
    "orange": 47,
    "mango": 60,
    "grapes": 69,
    "pineapple": 50,
    "watermelon": 30,
    "papaya": 43,
    "strawberry": 32,
    "blueberry": 57,
    "kiwi": 61,
    "pear": 57,
    "peach": 39,
    "plum": 46,
    "cherry": 50,
    "pomegranate": 83,
    "guava": 68,
    "lychee": 66,
    "coconut": 354,
    "fig": 74
}
s2 =pd.Series(fruits_calories,name = "ashish")
# conditional output
'''print(s2>57)'''
# printing only those who statisfy the conitions
'''print(s2[s2>57])'''
'''print(s2[(s2>46)&(s2>100)])'''
# update the index value
s2["kiwi"] = 65
print(s2["kiwi"])

# data frame
data ={
    "Name" : ["om","yug","sachin","frag"],
    "post" : ["j","s","j","j"],
    "age" :[25,36,41,52]
}
v= pd.DataFrame(data)
'''print(v)'''
'''print(v(.head(2))
print(v.tail(3))'''
'''print(v.iloc[2:3])'''
'''print(v.loc[1:4 ,["post","age"]])'''
'''print(v["age"])'''
#to drop data from datset
'''print(v.drop("age" ,axis =1 ))
print(v.drop("age" ,axis =1,inplace = True ))
print(v)'''
# to check shap of data set 
'''print(v.shape)'''
# 4 row and 3cloums
'''print(v.info())'''
'''print(v.describe())'''
#Broadcasting
'''v["age"] = v["age"] +10
print(v)'''
#rename the columns
r=v.rename(columns={"post":"Roll"},inplace = 1)
'''print(v)
print(v.shape)'''
# print(v.info())
'''print(v.describe())'''
#broard casting
'''v["age"] =v["age"]+10
print(v["age"])
print(v["age"].unique())'''
'''q=v['age'].value_counts()
print(q)'''



