CRC8 = lambda vetorBytes : sum( vetorBytes ) & 0xff

a = CRC8( bytearray([1,3,3,4]) )
print(a)


def fun():
    fun() 

a = 100_000

