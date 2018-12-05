import requests

def post_patient():
    r = requests.post("http://vcm-6183.vm.duke.edu:5000/api/new_patient", json={
        "patient_id": "3",
        "attending_email": "kck22@duke.edu",
        "user_age": 23})
    # r = requests.post("http://127.0.0.1:5002/api/new_patient", json={
    #     "patient_id": "15",
    #     "attending_email": "kck22@duke.edu",
    #     "user_age": 23})

def post_heart_rate():
    r = requests.post("http://vcm-6183.vm.duke.edu:5000/api/heart_rate", json={
        "patient_id": "2",
        "heart_rate": 103})

def get_status():
    r = requests.get("http://vcm-6183.vm.duke.edu:5000/api/status/2")
    print(r.text)


def get_all_heart_rate():
    r = requests.get("http://vcm-6183.vm.duke.edu:5000/api/heart_rate/2")
    print(r.text)

def get_average():
    r = requests.get("http://127.0.0.1:5002/api/heart_rate/average/2")
    print(r.text)

def post_interval():
    r = requests.post("http://vcm-6183.vm.duke.edu:5000/api/heart_rate/interval_average", json={
        "patient_id": '2',
        "heart_rate_average_since": "2018-07-09 11:00:36.378429"
    })
    print(r.text)

if __name__ == "__main__":
    post_patient()
    # post_heart_rate()
    # get_status()
    # get_all_heart_rate()
    # get_average()
    # post_interval()