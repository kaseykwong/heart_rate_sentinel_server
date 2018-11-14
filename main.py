import requests

def post_patient():
    r = requests.post("http://127.0.0.1:5002/api/new_patient", json = {"patient_id": 2,"attending_email": "kck22@duke.edu","user_age": 23})


if __name__ == "__main__":
    post_patient()