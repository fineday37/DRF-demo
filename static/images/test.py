import os

with open(os.path.join(os.path.dirname(__file__), "秋水.jpg"), 'rb') as f:
    image = f.read()
print(image)