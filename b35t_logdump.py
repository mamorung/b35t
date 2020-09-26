"""
Derived from DeanCording's b35t dumper: https://github.com/DeanCording/owonb35/blob/master/owonb35.c

(https://www.eevblog.com/forum/testgear/linux-bluetooth-client-for-owon-b35-multimeter/ )

"""
import datetime
import sys

def print_timestamp(b):
    
    msec = int.from_bytes(b[:2], byteorder='little')
    tm = int.from_bytes(b[2:], byteorder='little')
    dt = datetime.datetime.fromtimestamp(tm)
    s = dt.strftime('%Y/%m/%d-%H:%M:%S.') + ("%03d" % msec)

    return s

def print_measurement(measurement, decimal, units, scale):
    
    if (decimal > 3):
        s = "Overload"
    else:
        if (units != 0 and (units != scale)):
            measurement = measurement * pow(10,0, (scale - units)*3)
            decimal = decimal - (scale - units)*3
        s = "%.*f" % (decimal, measurement)

    return s

def print_units(scale, units, function):

    sc = { 1:'n', 2:'u', 3:'m', 5:'k', 6:'M' }
    fn = [ 'Vdc', 'Vac', 'Adc',  'Aac', 'Ohms', 'F', 'Hz', '%', '°C', '°F', 'V', 'Ohms', 'hFE' ]
    if (units == 0):
        s = ""
    else:
        s = sc[units]
    if (function >= 0 and function < len(fn)):
        s = s + fn[function]

    return s

def print_type(type):

    tp = { 0x02:"Δ", 0x10:"min", 0x20:"max", 0x01:"hold" }
    if (type in tp):
        s = tp[type]
    else:
        s = ""

    return s

def sep(bCSV):

    return ',' if (bCSV) else ' '

def display_reading(reading, bCSV, units, bShowUnits):

    r0 = int.from_bytes(reading[6:8], 'little')
    r1 = int.from_bytes(reading[8:10], 'little')
    r2 = int.from_bytes(reading[10:12], 'little')

    function = (r0 >> 6) & 0x0f
    scale = (r0 >> 3) & 0x07
    decimal = r0 & 0x07
    if (r2 < 0x7fff):
        measurement = r2 / pow(10.0, decimal)
    else:
        measurement = -1 * (r2 & 0x7fff) / pow(10.0, decimal)

    if ((r1 & 0x08) != 0):
        se = "LOW BATTERY\n"
        sys.stderr.write(se)

    s = print_timestamp(reading[0:6])

    s = s + sep(bCSV)
    s = s + print_measurement(measurement, decimal, units, scale)
    if (bShowUnits):
        s = s + sep(bCSV)
        s = s + print_units(scale, units, function)
        s = s + sep(bCSV)
        s = s + print_type(r1)
        s = s + '\n'

    sys.stdout.write(s)
    sys.stdout.flush()

def main():

    if (len(sys.argv) < 1):
        sys.stderr.write("error: argc != 2")
        sys.exit(0)

    f = open(sys.argv[1], 'rb')
    b = f.read(12)
    while (len(b) == 12):
        display_reading(b, False, 0, True)
        b = f.read(12)
    f.close()
    sys.stdin.readline()
        

main()
