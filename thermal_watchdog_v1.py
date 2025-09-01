import subprocess
import time
import datetime
import sys

# set max temps for cpu, battery, ssd, wifi chip, and gpu in millidegrees celsius
max_cpu_temp = 90000
max_battery_temp = 60000
max_nvme_temp = 80000
max_wifi_temp = 100000
max_gpu_temp = 90000

# set loop interval in seconds
sleep_interval = 5

# set script failure path and temperature exceed path for log files
failure_path = './watchdog_script_failure.log'
exceed_temp_path = './thermal_temp_exceed.log'

# start loop
while True:

    # grab temps for cpu, battery, ssd, wifi chip, and gpu from /sys/class/hwmon/ and store as subprocess output (including stdout and stderr)
    cpu_temp = subprocess.run(['cat', '/sys/class/hwmon/hwmon1/temp1_input'], capture_output=True, text=True)
    battery_temp = subprocess.run(['cat', '/sys/class/hwmon/hwmon3/temp1_input'], capture_output=True, text=True)
    nvme_temp = subprocess.run(['cat', '/sys/class/hwmon/hwmon4/temp1_input'], capture_output=True, text=True)
    wifi_temp = subprocess.run(['cat', '/sys/class/hwmon/hwmon5/temp1_input'], capture_output=True, text=True)
    gpu_temp = subprocess.run(['cat', '/sys/class/hwmon/hwmon6/temp1_input'], capture_output=True, text=True)

    # counter for how many sensors fail
    # go through each subprocess output and check for suitable output/errors
    temp_fail_count = 0

    if len(cpu_temp.stdout) == 0 or len(cpu_temp.stderr) != 0:
        temp_fail_count += 1
    else:
        cpu_temp_int = int(cpu_temp.stdout)

    if len(battery_temp.stdout) == 0 or len(battery_temp.stderr) != 0:
        temp_fail_count += 1
    else:
        battery_temp_int = int(battery_temp.stdout)

    if len(nvme_temp.stdout) == 0 or len(nvme_temp.stderr) != 0:
        temp_fail_count += 1
    else:
        nvme_temp_int = int(nvme_temp.stdout)

    if len(wifi_temp.stdout) == 0 or len(wifi_temp.stderr) != 0:
        temp_fail_count += 1
    else:
        wifi_temp_int = int(wifi_temp.stdout)

    if len(gpu_temp.stdout) == 0 or len(gpu_temp.stderr) != 0:
        temp_fail_count += 1
    else:
        gpu_temp_int = int(gpu_temp.stdout)
    
    # if all sensors fail record error and exit
    if temp_fail_count == 5:
        with open(failure_path, 'a') as file:
            file.write(f'{datetime.datetime.now()}: Failure to find temperatures for all devices\n')
        sys.exit(-1)

    # check if each recorded temp is equal to or higher than max set temp, if so shutdown
    if cpu_temp_int >= max_cpu_temp:
        with open(exceed_temp_path, 'a') as file:
            file.write(f'{datetime.datetime.now()}: CPU is at or exceeded max safe operating temperature ({max_cpu_temp / 1000} °C). Recorded CPU temperature before safe shutdown: {cpu_temp_int / 1000} °C\n')
            subprocess.run(['sudo', 'shutdown', '-h', 'now'])
            sys.exit(0)

    if battery_temp_int >= max_battery_temp:
        with open(exceed_temp_path, 'a') as file:
            file.write(f'{datetime.datetime.now()}: Battery is at or exceeded max safe operating temperature ({max_battery_temp / 1000} °C). Recorded battery temperature before safe shutdown: {battery_temp_int / 1000} °C\n')
            subprocess.run(['sudo', 'shutdown', '-h', 'now'])
            sys.exit(0)

    if nvme_temp_int >= max_nvme_temp:
        with open(exceed_temp_path, 'a') as file:
            file.write(f'{datetime.datetime.now()}: NVMe SSD is at or exceeded max safe operating temperature ({max_nvme_temp / 1000} °C). Recorded SSD temperature before safe shutdown: {nvme_temp_int / 1000} °C\n')
            subprocess.run(['sudo', 'shutdown', '-h', 'now'])
            sys.exit(0)

    if wifi_temp_int >= max_wifi_temp:
        with open(exceed_temp_path, 'a') as file:
            file.write(f'{datetime.datetime.now()}: WiFi chip is at or exceeded max safe operating temperature ({max_wifi_temp / 1000} °C). Recorded chip temperature before safe shutdown: {wifi_temp_int / 1000} °C\n')
            subprocess.run(['sudo', 'shutdown', '-h', 'now'])
            sys.exit(0)

    if gpu_temp_int >= max_gpu_temp:
        with open(exceed_temp_path, 'a') as file:
            file.write(f'{datetime.datetime.now()}: GPU is at or exceeded max safe operating temperature ({max_gpu_temp / 1000} °C). Recorded GPU temperature before safe shutdown: {gpu_temp_int / 1000} °C\n')
            subprocess.run(['sudo', 'shutdown', '-h', 'now'])
            sys.exit(0)
        
    # repeat loop every interval until shutdown incurs
    time.sleep(sleep_interval)
