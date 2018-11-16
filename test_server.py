from server import check_hr_input, check_interval, check_new_info, \
    diagnosis, interval, average_hr, send_email
import pytest
from datetime import datetime


def test_check_hr_input():
    good_input1 = {
        "patient_id": "2",
        "heart_rate": 87
    }
    output1 = check_hr_input(good_input1)
    assert output1 is True

    good_input2 = {
        "patient_id": "3",
        "heart_rate": 205
    }
    output2 = check_hr_input(good_input2)
    assert output2 is True

    good_input3 = {
        "patient_id": 4,
        "heart_rate": 95
    }
    output3 = check_hr_input(good_input3)
    assert output3 is True

    bad_input1 = {
        "patient_id": "cool",
        "heart_rate": 87
    }
    output4 = check_hr_input(bad_input1)
    assert output4 is False

    bad_input2 = {
        "heart_rate": 87
    }
    output5 = check_hr_input(bad_input2)
    assert output5 is False

    bad_input3 = {
        "patient_id": 4
    }
    output6 = check_hr_input(bad_input3)
    assert output6 is False

    bad_input4 = {
        "patient_id": "125",
        "heart_rate": "86"
    }
    output7 = check_hr_input(bad_input4)
    assert output7 is False


@pytest.mark.parametrize("a,b,expected", [
    (23, 87, 'Normal'),
    (1, 160, 'Tachycardia'),
    (1, 87, 'Normal'),
    (2, 152, 'Tachycardia'),
    (2, 100, 'Normal'),
    (4, 147, 'Tachycardia'),
    (6, 87, 'Normal'),
    (6, 140, 'Tachycardia'),
    (10, 87, 'Normal'),
    (10, 135, 'Tachycardia'),
    (14, 87, 'Normal'),
    (14, 125, 'Tachycardia'),
    (23, 110, 'Tachycardia')
])
def test_diagnosis_parametrize(a, b, expected):
    """
    test_add_parametrize is called with all of the input & expected output
    combinations specified in the decorator above.
    """
    assert diagnosis(a, b) == expected


def test_interval():
    hr_t = [datetime.strptime("2018-07-09 11:00:36.378429",
                              "%Y-%m-%d %H:%M:%S.%f"),
            datetime.strptime("2018-07-09 11:20:36.378429",
                              "%Y-%m-%d %H:%M:%S.%f"),
            datetime.strptime("2018-07-09 11:40:36.378429",
                              "%Y-%m-%d %H:%M:%S.%f"),
            datetime.strptime("2018-07-09 12:00:36.378429",
                              "%Y-%m-%d %H:%M:%S.%f")]
    hr = [50, 87, 79, 99]
    time_since = "2018-07-09 11:15:36.378429"
    int_avg = round(interval(hr, hr_t, time_since))
    assert int_avg == 88


def test_average():
    hr1 = [55, 65, 75, 85, 95]
    avg1 = average_hr(hr1)
    assert avg1 == 75


def test_check_interval():
    good_input1 = {
        "patient_id": "15",
        "heart_rate_average_since": "2018-07-09 11:00:36.378429"
    }
    output1 = check_interval(good_input1)
    assert output1 is True

    good_input2 = {
        "patient_id": 15,
        "heart_rate_average_since": "2018-07-09 11:00:36.378429"
    }
    output2 = check_interval(good_input2)
    assert output2 is True

    bad_input3 = {
        "heart_rate_average_since": "2018-07-09 11:00:36.378429"
    }
    output3 = check_interval(bad_input3)
    assert output3 is False

    bad_input4 = {
        "patient_id": "15"
    }
    output4 = check_interval(bad_input4)
    assert output4 is False


def test_check_new():
    good_input1 = {
        "patient_id": "2",
        "attending_email": "kck22@duke.edu",
        "user_age": 23
    }
    output1 = check_new_info(good_input1)
    assert output1 is True

    good_input2 = {
        "patient_id": 2,
        "attending_email": "kck22@duke.edu",
        "user_age": 23
    }
    output2 = check_new_info(good_input2)
    assert output2 is True

    bad_input3 = {
        "patient_id": "cool",
        "attending_email": "kck22@duke.edu",
        "user_age": 23
    }
    output3 = check_new_info(bad_input3)
    assert output3 is False

    bad_input4 = {
        "patient_id": "2",
        "attending_email": 3,
        "user_age": 23
    }
    output4 = check_new_info(bad_input4)
    assert output4 is False

    bad_input5 = {
        "patient_id": "2",
        "attending_email": "kck22@duke.edu",
        "user_age": "apple"
    }
    output5 = check_new_info(bad_input5)
    assert output5 is False

    bad_input6 = {
        "attending_email": "kck22@duke.edu",
        "user_age": 23
    }
    output6 = check_new_info(bad_input6)
    assert output6 is False

    bad_input7 = {
        "patient_id": "cool",
        "user_age": 23
    }
    output7 = check_new_info(bad_input7)
    assert output7 is False

    bad_input8 = {
        "patient_id": "cool",
        "attending_email": "kck22@duke.edu",
    }
    output8 = check_new_info(bad_input8)
    assert output8 is False


# def test_send_email():
#     a_email = 'kck22@duke.edu'
#     patient_id = '3'
#     output_e = send_email(a_email, patient_id)
#     msg = "email sent"
#     assert output_e == msg
