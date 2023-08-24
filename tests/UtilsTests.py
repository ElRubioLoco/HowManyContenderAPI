import base64

if __name__ == "__main__":
    print(base64.b64encode(open("src/utils/authenticate.txt", 'r', encoding='utf-8').read().encode('ascii')).decode('ascii'))