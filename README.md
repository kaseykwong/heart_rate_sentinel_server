# heart_rate_sentinel_server
This assignment will have you build a simple centralized heart rate sentinel server. This server will be built to receive POST requests from mock patient heart rate monitors that contain patient heart rate information over time. If a patient exhibits a tachycardic heart rate, the physician should receive an email warning them. 

Author: Kasey Kwong

This Flask server is designed to:
- Create new patients in database
- Allow Attending physician to upload new Heart Rate data for the patient
- Provide a quick diagnostic of Patient's Heart condition (Tachycardia)
- Provide read-access of Patient's recorded Heart Rates
- Calculate average Heart rate over all time or over specific time interval

How to use code:
```
VCM: vcm-6183.vm.duke.edu:5000
VCM IP address: 
Create Virtual Environment
python3.6 -m venv .venv
source .venv/bin/activate


Install requirements.txt
pip install -r requirements.txt


pip install sendgrid

Run server on local machine: make sure to change host= 127.0.0.1, port= 5002
python3.6 server.py

"Client":
- make sure to "uncomment" which functions in main you want to run
python3.6 main.py

```

Travis Build Status: [![Build Status](https://travis-ci.com/kaseykwong/heart_rate_sentinel_server.svg?branch=master)](https://travis-ci.com/kaseykwong/heart_rate_sentinel_server)