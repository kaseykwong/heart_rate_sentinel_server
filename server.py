from flask import Flask, jsonify, request
from pymodm import connect
from pymodm import MongoModel, fields, errors
import pymodm
from datetime import datetime
import numpy as np
import logging
import sendgrid
import os
from sendgrid.helpers.mail import *


connect("mongodb://kck22:5chool@ds255403.mlab.com:55403/bme590")
# connect to database
app = Flask(__name__)


class Patient(MongoModel):
    """
    Patient Class
    Includes:
        Patient ID
        Attending Physician Email
        Patient Age
        Recorded Heart Rates
        Time of Recorded Heart Rates
    """
    patient_id = fields.CharField(primary_key=True)
    attending_email = fields.EmailField()
    user_age = fields.IntegerField()
    heart_rate = fields.ListField(field=fields.IntegerField())
    heart_rate_time = fields.ListField(field=fields.DateTimeField())
    created = fields.DateTimeField()


def check_exist(info):
    """
    Checks if a patient and related information exists in the database/server
    :param info: a request json file
    :return: boolean of whether or not patient exists in server
    """
    try:
        Patient.objects.raw({"_id": str(info["patient_id"])})
    except pymodm.errors.DoesNotExist:
        return False
    return True


@app.route("/api/new_patient", methods=["POST"])
def new_patient():
    """
    Flask function to post a new patient to the server
    :return:
    """
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
    """
    Creates a new patient in the server
    :param info: json request file containing patient id, attending email,
    user age
    :return:
    """
    set_logging()
    patient_number = str(info["patient_id"])
    a_email = info["attending_email"]
    age = info["user_age"]
    time_initialize = datetime.now()
    p = Patient(patient_number, a_email, age, [50],
                [time_initialize], time_initialize)
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
    """
    Checks that new patient information is good
    :param info:
    :return:
    """
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
    """
    Function to post and add new heart rate data to a patient
    :return:
    """
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
            print("Patient ID doesn't exist. Please create new "
                  "patient first.")
            logging.error("Patient ID doesn't exist. Please create"
                          " new patient first.")
            return "Patient ID doesn't exist. Please create new " \
                   "patient first.", 400
    else:
        logging.error("Invalid Input")
        return "Invalid Input", 400
    return jsonify(data), 200


def add_heart_rate(patient_id, hr, time):
    """
    Function to append heart rate and current time to patient's info
    :param patient_id:
    :param hr: heart rate to be recorded
    :param time: current time
    :return:
    """
    p = Patient.objects.raw({"_id": str(patient_id)}).first()
    if p.heart_rate_time[0] == p.created:
        p.heart_rate_time[0] = time
        p.heart_rate[0] = hr
    else:
        p.heart_rate.append(hr)
        p.heart_rate_time.append(time)
    if diagnosis(p.user_age, hr) == 'Tachycardia':
        send_email(p.attending_email, patient_id)
    p.save()


def send_email(a_email, patient_id):
    """
    Function to send email in case of Tachycardia detected
    :param a_email: attending's email
    :param patient_id:
    :return:
    """
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("kck22@duke.edu")
    to_email = Email(a_email)
    subject = "Patient Heart Rate Warning"
    content = Content("text/plain", "Patient:" + patient_id +
                      " has shown signs of tachycardia based on most "
                      "recent heart rate.")
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)
    return "email sent"


def check_hr_input(info):
    """
    Check that new heart rate data is good
    :param info:
    :return:
    """
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
    except TypeError:
        msg = "Heart Rate Error. 'heart_rate' input must be a float. "
        logging.error(msg)
        print(msg)
        return False
    print(msg)
    logging.info(msg)
    return True


@app.route("/api/status/<patient_id>", methods=["GET"])
def status(patient_id):
    """
    GET method to request recent status of patient
    :param patient_id:
    :return:
    """
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
    """
    function to identify patient and call diagnosis function
    :param patient_id:
    :return:
    """
    patient = Patient.objects.raw({"_id": str(patient_id)}).first()
    hr = patient.heart_rate[-1]
    condition = diagnosis(patient.user_age, hr)
    hr_t = patient.heart_rate_time[-1]
    data = {
        "Patient ID": patient_id,
        "Most Recent Heart Rate": hr_t,
        "Status": condition
    }
    return data


def diagnosis(age, hr):
    """
    deteremine diagnosis based on age and heart rate
    :param age: age of patient
    :param hr: recorded heart rate
    :return: condition of patient
    """
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
    elif age > 15 and hr >= 100:
        condition = "Tachycardia"
    return condition


@app.route("/api/heart_rate/<patient_id>", methods=["GET"])
def heart_rate_patient(patient_id):
    """
    GET method to return all recorded heart rates of patient
    :param patient_id:
    :return:
    """
    # patient_id = int(patient_id)
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
    """
    function to return list of heart rates for stated interval or all
    :param patient_id:
    :return:
    """
    set_logging()
    patient = Patient.objects.raw({"_id": str(patient_id)}).first()
    data = {
        "Patient ID": patient_id,
        "Recorded Heart Rates": patient.heart_rate,
        "Time Recorded": patient.heart_rate_time
    }
    return data


@app.route("/api/heart_rate/average/<patient_id>", methods=["GET"])
def average_patient(patient_id):
    """
    GET method to return Average heart rate of patient
    :param patient_id:
    :return:
    """
    set_logging()
    try:
        [hr, hr_t] = return_hr(patient_id)
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
    """
    Function to calculate average heart rate
    :param hr:
    :return:
    """
    set_logging()
    if len(hr) is 1:
        logging.warning("Average is calculated for only one heart rate!")
    average = np.mean(hr)
    logging.info("Average heart rate calculated successfully.")
    return average


def return_hr(patient_id):
    """
    function to call patient info and extract heart rate and time data
    :param patient_id:
    :return:
    """
    set_logging()
    patient = Patient.objects.raw({"_id": str(patient_id)}).first()
    hr = patient.heart_rate
    hr_t = patient.heart_rate_time
    return hr, hr_t


@app.route("/api/heart_rate/interval_average", methods=["POST"])
def interval_average():
    """
    POST method to return average heart rate over interval of time
    :return:
    """
    set_logging()
    info = request.get_json()
    if check_interval(info) is True:
        if check_exist(info) is True:
            try:
                [hr, hr_t] = return_hr(info["patient_id"])
                t_since = info["heart_rate_average_since"]
                int_avg = interval(hr, hr_t, t_since)
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
            logging.error("Patient ID doesn't exist. Please "
                          "create new patient first.")
            return 400
    else:
        logging.error("Invalid Input")
        return "Invalid Input", 400
    return jsonify(data), 200


def interval(hr, hr_t, t_since):
    """
    function to isolate heart rates within the interval of interest
    :param hr:
    :param hr_t:
    :param t_since:
    :return:
    """
    hr_since = []
    for n, t in enumerate(hr_t):
        if t > datetime.strptime(t_since, "%Y-%m-%d %H:%M:%S.%f"):
            hr_since.append(hr[n])
    average = average_hr(hr_since)
    return average


def check_interval(info):
    """
    Function to check that interval average calling inputs are ok
    :param info:
    :return:
    """
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
        msg = "Requested Time Error. No input provided " \
              "for 'heart_rate_average_since'."
        print(msg)
        logging.error(msg)
        return False
    except ValueError:
        msg = "Requested Time Error. 'heart_rate_average_since' " \
              "input must be a datetime."
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
    app.run(host="0.0.0.0.")
