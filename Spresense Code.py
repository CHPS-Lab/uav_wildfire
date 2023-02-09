import time
import board
import busio
from digitalio import DigitalInOut
import analogio
import sdioio
import storage
import camera
import math
import adafruit_ds3231
import adafruit_bme680
from adafruit_pm25.i2c import PM25_I2C
import adafruit_scd4x

# Set up the SD card and mount it as /sd.
print('start sd card setup')
sd = sdioio.SDCard(
    clock=board.SDIO_CLOCK,
    command=board.SDIO_COMMAND,
    data=board.SDIO_DATA,
    frequency=25000000)
time.sleep(3)

vfs = storage.VfsFat(sd)

storage.mount(vfs, '/sd')
print('end sd card setup')

# Set up i2c.  You have to do this only once.
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)  # Uses board.SCL and board.SDA

rtc = adafruit_ds3231.DS3231(i2c)

# Reset pin is used for the PMS particle sensor. Since we are not using any
# let us set it to None.
reset_pin = None


# Set up the i2c BME680 sensor.
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)

# Connect to a PM2.5 sensor over I2C
pm25 = PM25_I2C(i2c, reset_pin)
#print("Found PM2.5 sensor, reading data...")

scd4x = adafruit_scd4x.SCD4X(i2c)
#print("Serial number:", [hex(i) for i in scd4x.serial_number])

scd4x.start_periodic_measurement()
#print("Waiting for first measurement....")

# The HCHO sensor (Grove) is set up using the DAC option.  This sends an analog
# signal to the microcontroller and we use the A2 pin to read it. The second line
# concerns the analog signal to a concentration based on a calibration line.
# The ADC at pin A2 is 5V internal voltage and 10 bit. But, it show values as unsigned
# 16 bit.
pin = analogio.AnalogIn(board.A2)
#print(pin.value, 3.125 * (pin.value * 5. / 2**16) - 1.25 )

old_time = time.monotonic()

t = rtc.datetime
Date = str(t.tm_year) +"_"+ str(t.tm_mon) +"_"+ str(t.tm_mday) +"_"
Time = str(t.tm_hour) +"_"+ str(t.tm_min) +"_"+ str(t.tm_sec)
file_name = "out"+ Date + Time +'.csv'

while True:
        
    t = rtc.datetime
    Date = str(t.tm_year) +"_"+ str(t.tm_mon) +"_"+ str(t.tm_mday) +"_"
    Time = str(t.tm_hour) +"_"+ str(t.tm_min) +"_"+ str(t.tm_sec)
   
# Get local date and time.
    
    fo = 0.0

    aqdata = pm25.read()
    pinx = analogio.AnalogIn(board.A2)
    pvx = pinx.value
    #print (pvx)
    fo = 3.125 * (pvx * 5. / 2**16) - 1.25
    data_string = (Date, Time, math.ceil(bme680.temperature), math.ceil(bme680.relative_humidity),
    bme680.pressure, bme680.gas, aqdata["pm10 env"], aqdata["pm25 env"], aqdata["pm100 env"],
    ("{:.2e}".format(aqdata["particles 03um"]*1.0E+04)),
    ("{:.2e}".format(aqdata["particles 05um"]*1.0E+04)),
    ("{:.2e}".format(aqdata["particles 10um"]*1.0E+04)),
    ("{:.2e}".format(aqdata["particles 25um"]*1.0E+04)),
    ("{:.2e}".format(aqdata["particles 50um"]*1.0E+04)),
    ("{:.2e}".format(aqdata["particles 100um"]*1.0E+04)),
    float(("{0:.2f}".format(fo))), scd4x.CO2, scd4x.temperature, scd4x.relative_humidity)
    print(data_string)

    with open("/sd/"+ file_name, "a") as f:
        f.write("{}".format(data_string))
        f.write("\r\n")
    #   time.sleep(5)

    new_time = time.monotonic()
    if (new_time > old_time) :
        old_time=new_time








