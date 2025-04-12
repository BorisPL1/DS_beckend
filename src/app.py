import logging
import requests
from flask import Flask, request, jsonify
from models.plate_reader import PlateReader, InvalidImage
import logging
import io


app = Flask(__name__)
reader = PlateReader.load_from_file(r'C:\Studying\AAA\Term2\DS_beckend\src\plate_reader_model.pth')

class PlateReaderClient:
    def __init__(self, host: str):
        self.host = host

    def get_image(self, name):
        res = requests.get(f'{self.host}/images/' + name)
        return res.content
    
class PlateReaderClient1:
    def __init__(self, host: str):
        self.host = host

    def get_image(self, name):
        res = requests.get(f'{self.host}/images/' + name, timeout=5)
        return res.content
    
@app.route('/')
def read_plate():
    id_list = ['10022', '9965']
    name = request.args.get('name')
    if name is None or name not in id_list:
        return {'Error': 'Invalid or missing name'}, 400
    client = PlateReaderClient(host='http://89.169.157.72:8080')
    try:
        im = client.get_image(name)
    except requests.exceptions.HTTPError as e:
        return {'Error': 'Failed to retrieve image from server'}, 503  # Ошибка сервера
    except requests.exceptions.ConnectionError:
        return {'Error': 'Connection error'}, 503  # Ошибка соединения
    except requests.exceptions.Timeout:
        return {'Error': 'Request timed out'}, 504  # Ошибка таймаута
    except requests.exceptions.RequestException as e:
        return {'Error': 'An error occurred while processing the request'}, 500  # Общая ошибка
    im = io.BytesIO(im)
    result = reader.read_text(im)
    return {'result}': result}    

@app.route('/reader', methods=['POST'])
def read_plate_many():
    data = request.get_json()
    results = []
    client = PlateReaderClient1(host='http://89.169.157.72:8080')
    for i in data:
        try:
            im = client.get_image(f"{i}")
        except requests.exceptions.HTTPError as e:
            return {'Error': 'Failed to retrieve image from server'}, 503  # Ошибка сервера
        except requests.exceptions.ConnectionError:
            return {'Error': 'Connection error'}, 503  # Ошибка соединения
        except requests.exceptions.Timeout:
            return {'Error': 'Request timed out'}, 504  # Ошибка таймаута
        except requests.exceptions.RequestException as e:
            return {'Error': 'An error occurred while processing the request'}, 500  # Общая ошибка
        im = io.BytesIO(im)
        results.append(reader.read_text(im))
    return {f'result{i}': results[i] for i in range(len(results))}

if __name__ == '__main__':
    logging.basicConfig(
        format='[%(levelname)s] [%(asctime)s] %(message)s',
        level=logging.INFO,
    )

    app.run(host='0.0.0.0', port=8080, debug=True)
