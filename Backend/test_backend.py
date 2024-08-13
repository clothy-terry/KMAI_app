import requests
import json

def test1():
    url = 'http://localhost:5000/search'
    data = {'query': 'nitrogen hydrogen'}
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, data=json.dumps(data), headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # The response of the POST request
        print(response.json())
    else:
        print(f"Request failed with status code {response.status_code}")

def test2():
    url = 'http://localhost:5000/keyword_frequency'
    data = {'doc_ids': ['Alerts Library / AbradableCoatings-220622.docx', 'Alerts Library / AbradableCoatings-220929.docx'], 'keywords': ['knowledge','environmentally']}
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, data=json.dumps(data), headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # The response of the POST request
        print(response.json())
    else:
        print(f"Request failed with status code {response.status_code}")

def test_keyword_context():
    url = 'http://localhost:5000/keyword_context'
    data = {'doc_ids':['Alerts Library / NitricOxide-220608.doc'], 
            'keywords': ['journal subscriptions'], 
            'window_size': None}
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, data=json.dumps(data), headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # The response of the POST request
        print(response.json())
    else:
        print(f"Request failed with status code {response.status_code}")

def test_extract_and_build_index_route():
    url = 'http://localhost:5000/extract_and_build_index'
    # Open the files in binary mode
    files = [('files', ('FoodProcessing-240111.doc', open('FoodProcessing\FoodProcessing-240111.doc', 'rb')))]
    # Include the necessary data for your POST request
    data = {
        'index_name': 'test_index',
    }
    response = requests.post(url, files=files, data=data)
    # Close the files
    for _, (_, file) in files:
        file.close()
    if response.status_code == 200:
        print(response.json()['skipped'], 'successful')
    else:
        print(f"Request failed with status code {response.status_code}")

if __name__ == '__main__':
    #test1()
    #test2()
    #test_keyword_context()
    test_extract_and_build_index_route()