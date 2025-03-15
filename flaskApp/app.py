from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World from Cloud Run but now with Flask!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)