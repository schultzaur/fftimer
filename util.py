import os

BASE_PATH = os.path.join(os.path.expanduser('~'), 'Documents', 'FFTimer')

def format_ms(t):
    return "{:.2f}".format(t/1000)

