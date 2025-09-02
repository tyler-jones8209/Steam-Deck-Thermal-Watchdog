import subprocess
import time
import datetime
import sys

# set max temps for cpu, battery, ssd, wifi chip, and gpu in millidegrees celsius
# switch to dictionary for easier storing and comparison
max_temps = {
    'cpu': 90000,
    'battery': 60000,
    'nvme': 80000,
    'wifi': 100000,
    'gpu': 90000
}

# set sensor paths for each device found through testing lm-sensors
# switch to dictionary for easier storing and comparison
sensor_paths = {
    'cpu': '/sys/class/hwmon/hwmon1/temp1_input',
    'battery': '/sys/class/hwmon/hwmon3/temp1_input',
    'nvme': '/sys/class/hwmon/hwmon4/temp1_input',
    'wifi': '/sys/class/hwmon/hwmon5/temp1_input',
    'gpu': '/sys/class/hwmon/hwmon6/temp1_input'
}

# set script failure path and temperature exceed path for log files
failure_path = './watchdog_script_failure.log'
exceed_temp_path = './thermal_temp_exceed.log'

# set loop interval in seconds
sleep_interval = 5

# function to read sensor information with given path
def read_sensor(path):

    # open file and put data into sensor variable
    with open(path, 'r') as sensor:

        # read single line from file and store as temp; strip extra junk if applicable
        temp = sensor.read().strip()

        # if temp not found or it consists of 0 characters set it to None and return
        if not temp or len(temp) == 0:
            temp = None
            return temp

        # if found, return temp as int
        else:
            return int(temp)

# function for logging failures of various reasons
def log_failure(message):

    # retrieve date and time for timestamp
    timestamp = datetime.datetime.now()

    # open log file and write timestamp with failure message
    with open(failure_path, 'a') as file:
        file.write(f"{timestamp}: {message}\n")

# function for logging any instances of a device exceeding it's max temperature
def log_exceed(device, current_temp, max_temp):

    # retrieve date and time for timestamp
    timestamp = datetime.datetime.now()

    # open log file and write timestamp with device info such as name, max temp, and recorded temp at shutdown
    with open(exceed_temp_path, 'a') as file:
        file.write(f"{timestamp}: {device.upper()} exceeded max safe temperature ({max_temp / 1000}°C). Current temp: {current_temp / 1000}°C. Initiating safe shutdown.\n")

# function to perform safe shutdown with subprocess
def safe_shutdown():
    subprocess.run(['sudo', 'shutdown', '-h', 'now'])
    sys.exit(0)

# start loop
while True:

    # bool checking for if all sensors fail; replaced old counting method
    all_sensors_fail = True

    # dictionary formatted as device: current_temp 
    temps = {}

    # loop through devices and read current temp
    for device, path in sensor_paths.items():
        
        # find temp using function
        temp = read_sensor(path)
        
        # log failure with custom message if temp is None 
        if temp is None:
            log_failure(f"Failure to locate {device} temperatue at {path}")
        
        # record device/temp pair in dictionary and set all_sensors_fail to false
        # i'm assuming that the steam deck is small enough that if at least one sensors makes it through that it will protect the entire machine
        else:
            temps[device] = temp
            all_sensors_fail = False

    # if all sensors fail, log it, exit the script, and pray to the Valve gods that it doesn't explode
    if all_sensors_fail:
        log_failure("All sensors failed. Exiting script.")
        sys.exit(-1)

    # loop through devices and check current temps against max temps; if exceeded log timestamp and temp and safely shutdown (in theory)
    for device, temp in temps.items():
        max_temp = max_temps[device]
        if temp >= max_temp:
            log_exceed(device, temp, max_temp)
            safe_shutdown()

    # repeat loop every interval until shutdown incurs
    time.sleep(sleep_interval)
