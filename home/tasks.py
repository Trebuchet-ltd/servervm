from servervm.celery import *

@app.task
def add(x, y):
    z = x + y
    print("working")
    print(z)
    return z

