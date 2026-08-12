from flask import Flask, render_template, request
from predict import predict

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    url = ''
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if url:
            # ensure scheme present for parsing
            if not (url.startswith('http://') or url.startswith('https://')):
                url = 'http://' + url
            result = predict(url)
    return render_template('index.html', result=result, url=url)

if __name__ == '__main__':
    app.run(debug=True)
