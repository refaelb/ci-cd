import os
p=os.listdir()
for i in p:
    if os.path.isdir(i):
        print(i)