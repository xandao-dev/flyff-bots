import serial
import time

# initialization and open the port
# possible timeout values:
#    1. None: wait forever, block call
#    2. 0: non-blocking mode, return immediately
#    3. x, x is bigger than 0, float allowed, timeout block call

ser = serial.Serial()
ser.port = "COM4"
ser.baudrate = 9600
ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
ser.parity = serial.PARITY_NONE  # set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
ser.timeout = 1  # non-block read
ser.xonxoff = False  # disable software flow control
ser.rtscts = False  # disable hardware (RTS/CTS) flow control
ser.dsrdtr = False  # disable hardware (DSR/DTR) flow control
ser.writeTimeout = 2  # timeout for write

try:
    ser.open()
except Exception as e:
    print("error open serial port: " + str(e))
    exit()

if ser.isOpen():
    try:
        ser.flushInput()  # flush input buffer, discarding all its contents
        ser.flushOutput()  # flush output buffer, aborting current output
        # and discard all that is in buffer

        time.sleep(2)
        # write data
        print("Start")
        ser.write(b"AT+CSQ")
        print("Done 1")
        ser.write(b"hello")
        print("Done 2")
        ser.write(b'\x03')
        print("Done 3")

        #print("write data: AT+CSQ")
        time.sleep(0.5)  # give the serial port sometime to receive the data
        numOfLines = 0

        while True:
            response = str(ser.readline())
            print("read data: " + response)
            numOfLines = numOfLines + 1
            if (numOfLines >= 5):
                break
        ser.close()
    except Exception as e:
        print("error communicating...: " + str(e))
else:
    print("cannot open serial port")
