from flask import Flask, jsonify, request
from pymodm import connect
from pymodm import MongoModel, fields, errors
import pymodm
from datetime import datetime
import numpy as np
import logging


connect("mongodb://kck22:5chool@ds255403.mlab.com:55403/bme590")  # connect to database
app = Flask(__name__)


class Patient(MongoModel):
    patient_id = fields.CharField(primary_key=True)
    attending_email = fields.EmailField()
    user_age = fields.IntegerField()
    heart_rate = fields.ListField(field=fields.IntegerField())
    heart_rate_time = fields.ListField(field=fields.DateTimeField())
    created = fields.DateTimeField()


def check_exist(info):
    try:
        Patient.objects.raw({"_id": info["patient_id"]}).first()
    except pymodm.errors.DoesNotExist:
        return False
    return True


@app.route("/api/new_patient", methods=["POST"])
def new_patient():
    set_logging()
    info = request.get_json()
    valid_check = check_new_info(info)
    if valid_check is True:
        if check_exist(info) is False:
                patient = create_user(info)
                print("Patient successfully saved.")
        else:
            print("Patient_ID already exists, please enter new ID. ")
            logging.error("Patient_ID already exists, please enter new ID. ")
            return "Patient_ID already exists, please enter new ID. ", 400
    else:
        logging.error("Invalid Input")
        return "Invalid Input", 400
    return jsonify(patient), 200


def create_user(info):
    set_logging()
    patient_number = info["patient_id"]
    email = info["attending_email"]
    age = info["user_age"]
    time_initialize = datetime.now()
    p = Patient(patient_number, email, age, [50], [time_initialize], time_initialize)
    p.save()
    logging.info("New Patient Added. ")
    patient = {
        "Message": "New Patient successfully added.",
        "Patient ID": info["patient_id"],
        "Attending Email": info["attending_email"],
        "Age": info["user_age"]
    }
    return patient


def check_new_info(info):
    msg = "Data input is OK. "
    set_logging()
    try:
        int(info["patient_id"])
    except KeyError:
        msg = "Patient ID Error: No input provided for 'patient_id'. "
        print(msg)
        logging.error(msg)
        return False
    except ValueError:
        msg = "Patient ID Error: 'patient_id' input must be an integer. "
        print(msg)
        logging.error(msg)
        return False
    try:
        if type(info["attending_email"]) is not str:
            msg = "Email Error: 'attending_email' input must be a string. "
            print(msg)
            logging.error(msg)
            return False
    except KeyError:
        msg = "Email Error: No input provided for 'attending_email'. "
        print(msg)
        logging.error(msg)
        return False
    try:
        float(info["user_age"])
        if info["user_age"] > 120:
            logging.warning("Warning: Your age inputted is >120")
    except KeyError:
        msg = "User Age Error: No input provided for 'user_age'."
        print(msg)
        logging.error(msg)
        return False
    except ValueError:
        msg = "User Age Error: 'user_age' input must be a number. "
        print(msg)
        logging.error(msg)
        return False
    print(msg)
    logging.info(msg)
    return True


@app.route("/api/heart_rate", methods=["POST"])
def heart_rate():
    set_logging()
    data = request.get_json()
    if check_hr_input(data) is True:
        patient_number = data["patient_id"]
        if check_exist(data) is True:
            hr = data["heart_rate"]
            curr_time = datetime.now()
            add_heart_rate(patient_number, hr, curr_time)
            data = {
                "Patient ID": patient_number,
                "Heart Rate": hr,
                "Current Time": curr_time
            }
        else:
            print("Patient ID doesn't exist. Please create new patient first.")
            logging.error("Patient ID doesn't exist. Please create new patient first.")
            return "Patient ID doesn't exist. Please create new patient first.", 400
    else:
        logging.error("Invalid Input")
        return "Invalid Input", 400
    return jsonify(data), 200


def add_heart_rate(patient_id, hr, time):
    p = Patient.objects.raw({"_id": patient_id}).first()
    if p.heart_rate_times[0] == p.created:
        p.heart_rate_times[0] = time
        p.heart_rate[0] = hr
    else:
        p.heart_rate.append(hr)
        p.heart_rate_times.append(time)
    p.save()


def check_hr_input(info):
    msg = "Data input is OK. "
    set_logging()
    try:
        int(info["patient_id"])
    except KeyError:
        msg = "Patient ID Error: No input provided for 'patient_id'. "
        print(msg)
        logging.error(msg)
        return False
    except ValueError:
        msg = "Patient ID Error: 'patient_id' input must be an integer. "
        print(msg)
        logging.error(msg)
        return False
    try:
        float(info["heart_rate"])
        if info["heart_rate"] > 200:
            logging.warning("Warning: Heart rate is >200")
    except KeyError:
        msg = "Heart Rate Error. No input provided for 'heart_rate'."
        print(msg)
        logging.error(msg)
        return False
    except ValueError:
        msg = "Heart Rate Error. 'heart_rate' input must be a float. "
        logging.error(msg)
        print(msg)
        return False
    print(msg)
    logging.info(msg)
    return True


@app.route("/api/status/<patient_id>", methods=["GET"])
def status(patient_id):
    set_logging()
    try:
        condition = get_status(patient_id)
    except pymodm.errors.DoesNotExist:
        message = "No Data associated with Patient ID"
        logging.error(message)
        print(message)
        return message, 400
    return jsonify(condition), 200


def get_status(patient_id):
    patient = Patient.objects.raw({"_id": patient_id}).first()
    hr = patient.heart_rate[-1]
    condition = diagnosis(hr, patient.user_age)
    hr_t = patient.heart_rate_time[-1]
    data = {
        "Patient ID": patient_id,
        "Most Recent Heart Rate": hr_t,
        "Status": condition
    }
    return data


def diagnosis(hr, age):
    set_logging()
    condition = "Normal"
    if age <= 1 and hr >= 159:
        condition = "Tachycardia"
    elif age <= 2 and hr >= 151:
        condition = "Tachycardia"
    elif age <= 4 and hr >= 137:
        condition = "Tachycardia"
    elif age <= 7 and hr >= 133:
        condition = "Tachycardia"
    elif age <= 11 and hr >= 130:
        condition = "Tachycardia"
    elif age <= 15 and hr >= 119:
        condition = "Tachycardia"
    elif hr >= 100:
        condition = "Tachycardia"
    return condition


@app.route("/api/heart_rate/<patient_id>", methods=["GET"])
def heart_rate_patient(patient_id):
    #patient_id = int(patient_id)
    set_logging()
    try:
        data = print_user(patient_id)
    except pymodm.errors.DoesNotExist:
        message = "No data associated with patient id."
        print(message)
        logging.error(message)
        return message, 400
    return jsonify(data), 200


def print_user(patient_id):
    set_logging()
    patient = Patient.objects.raw({"_id": patient_id}).first()
    data = {
        "Patient ID": patient_id,
        "Recorded Heart Rates": patient.heart_rate,
        "Time Recorded": patient.heart_rate_time
    }
    return data


@app.route("/api/heart_rate/average/<patient_id>", methods=["GET"])
def average_patient(patient_id):
    set_logging()
    try:
        hr = return_hr(patient_id)
        av = average_hr(hr)
        result = {
            "Patient ID": patient_id,
            "Average Heart Rate": av
        }
    except pymodm.errors.DoesNotExist:
        msg = "No data associated with patient id."
        logging.error(msg)
        return msg, 400
    return jsonify(result), 200


def average_hr(hr):
    set_logging()
    if len(hr) is 1:
        logging.warning("Average is calculated for only one heart rate!")
    average = np.mean(hr)
    logging.info("Average heart rate calculated successfully.")
    return average


def return_hr(patient_id):
    set_logging()
    patient = Patient.objects.raw({"_id": patient_id}).first()
    hr = patient.heart_rate
    hr_t = patient.heart_rate_time
    return hr, hr_t


@app.route("/api/heart_rate/interval_average", methods=["POST"])
def interval_average():
    set_logging()
    info = request.get_json()
    if check_interval(info) is True:
        if check_exist(info) is True:
            try:
                int_avg = interval(info)
                data = {
                    "Patient ID": info["patient_id"],
                    "Average Heart Rate": int_avg,
                    "Since": info["heart_rate_average_since"]
                }
            except pymodm.errors.DoesNotExist:
                message = "No data associated with patient id."
                print(message)
                logging.error(message)
                return message, 400
        else:
            print("Patient ID doesn't exist. Please create new patient first.")
            logging.error("Patient ID doesn't exist. Please create new patient first.")
            return 400
    else:
        logging.error("Invalid Input")
        return "Invalid Input", 400
    return jsonify(data), 200


def interval(info):
    [hr, hr_t] = return_hr(info["patient_id"])
    time = info["heart_rate_average_since"]
    hr_since = []
    for n, t in enumerate(hr_t):
        if t > time:
            hr_since.append(hr[n])
    average = average_hr(hr_since)
    return average


def check_interval(info):
    msg = "Data input is OK. "
    set_logging()
    try:
        int(info["patient_id"])
    except KeyError:
        msg = "Patient ID Error: No input provided for 'patient_id'. "
        print(msg)
        logging.error(msg)
        return False
    except ValueError:
        msg = "Patient ID Error: 'patient_id' input must be an integer. "
        print(msg)
        logging.error(msg)
        return False
    try:
        time = datetime.strptime(info["heart_rate_average_since"],
                                 "%Y-%m-%d %H:%M:%S.%f")
        logging.info("%s%s", "Time requested is valid: ", time)
    except KeyError:
        msg = "Requested Time Error. No input provided for 'heart_rate_average_since'."
        print(msg)
        logging.error(msg)
        return False
    except ValueError:
        msg = "Requested Time Error. 'heart_rate_average_since' input must be a datetime."
        logging.error(msg)
        print(msg)
        return False
    print(msg)
    logging.info(msg)
    return True


def set_logging():
    logging.basicConfig(filename='webservice.txt',
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)
    return


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002)
