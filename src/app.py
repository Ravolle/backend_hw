from flask import Flask, request
from models.plate_reader import PlateReader
import logging
import shutil
import requests
import io

app = Flask(__name__)
plate_reader = PlateReader.load_from_file('./model_weights/plate_reader_model.pth')

@app.route('/')
def hello():
    return '<h1><center>Hello!</center></h1>'




# ip:port/ID?s <- img
@app.route('/ID')
def id_reciever():
    s = request.args['s']
    if not s.isdigit():
        return 'invalid args', 400

    url = 'http://51.250.83.169:7878/images/{x}'.format(x = s)
    file_name = 'ID {x}'.format(x = s)

    res = requests.get(url, stream = True)

    if res.status_code == 200:
        im = io.BytesIO(res.content)
        body = plate_reader.read_text(im)
        return {'number': body}
    elif res.status_code > 499:
        return 'sevice down', 500
    else:
        return 'Not Found', 404
        
# ip:port/ID?s1, s2 <- img
@app.route('/DuoID')
def id_multi_reciever():
    s = request.args['s']
    b = s.split(',')

    if len(b) != 2 or not b[0].isdigit() or not b[1].isdigit():
        return 'invalid args', 400

    url_1 = 'http://51.250.83.169:7878/images/{x}'.format(x = b[0])
    url_2 = 'http://51.250.83.169:7878/images/{x}'.format(x = b[1])

    res_1 = requests.get(url_1, stream = True)
    res_2 = requests.get(url_2, stream = True)

    if res_1.status_code == 200 and res_2.status_code == 200:
        im_1 = io.BytesIO(res_1.content)
        im_2 = io.BytesIO(res_2.content)
        body_1 = plate_reader.read_text(im_1)
        body_2 = plate_reader.read_text(im_2)
        return {'number_1': body_1, 'number_2': body_2}
    elif res_1.status_code > 499 or res_2.status_code > 499:
        return 'sevice down', 500
    else:
        return 'Not Found', 404


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(levelname)s] [%(asctime)s] %(message)s',
        level=logging.INFO,
    )

    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', port=5000, debug=True)
