import struct
import time

# Max values for each data type
# temp = 100
# rh = 100
# pr = 2000
# al = 3000
# gx = 2000
# gy = 2000
# gz = 2000
# ax = 16
# ay = 16
# az = 16
# temp2 = 100

def pack (data):
    
    MAX_SHORT = 32767
    MAX_USHORT = 65535
    # MAX_INT = 2147483647
    # MAX_UINT = 4294967295
    # t  = data[0]
    temp = data[1]
    rh = data[2]
    pr = data[3]
    # al = data[4]
    gx = data[5]
    gy = data[6]
    gz = data[7]
    ax = data[8]
    ay = data[9]
    az = data[10]
    temp2 = data[11]
    
    tPacked     = data[0]
    tempPacked  = int(temp * (MAX_SHORT/100))
    rhPacked    = int(rh * (MAX_USHORT/100))
    prPacked    = int(pr * (MAX_USHORT/2000))
    alPacked    = data[4]
    gxPacked    = int(gx * (MAX_SHORT/2000))
    gyPacked    = int(gy * (MAX_SHORT/2000))
    gzPacked    = int(gz * (MAX_SHORT/2000))
    axPacked    = int(ax * (MAX_SHORT/16))
    ayPacked    = int(ay * (MAX_SHORT/16))
    azPacked    = int(az * (MAX_SHORT/16))
    temp2Packed = int(temp2 * (MAX_SHORT/100))

    buffer = struct.pack(">fhHHfhhhhhhh", tPacked, tempPacked, rhPacked, prPacked, alPacked, gxPacked, gyPacked, gzPacked, axPacked, ayPacked, azPacked, temp2Packed)
    print(buffer)


    file = open("logs/test", mode='wb')
    file.write(buffer)
    file.close()