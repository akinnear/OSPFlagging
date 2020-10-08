import requests

def test_simple_create_test():
    url = "localhost:5000/create_flag/FLAG1A/"
    r = requests.post(url)
    print(r.status_code)
    print(r.content)


