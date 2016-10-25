import io
import random
from PIL import Image

def get_marker(b, index):
    return (b[index] << 8 | b[index+1])

def get_length(b, index):
    return (b[index] << 8 | b[index+1])

def get_bit(byte, loc):
    return (byte & (1 << loc)) >> loc

# bit: 1 or 0
def set_bit(byte, loc, bit):
    if bit == 1:
        return (byte | (1 << loc))
    elif bit == 0:
        return (byte & ~(1 << loc))
    else:
        print("Error: bit argment should be 1 or 0 (%d given)" % bit)
        raise

def flip_one_bit(byte):
    loc = random.randint(0, 7)
    target_bit = get_bit(byte, loc)
    flipped_bit = (~target_bit) & 1
    ret = set_bit(byte, loc, flipped_bit)
    return ret.to_bytes(1, "big")

def flip_with_interval(byte_array, start, interval):
    n = 0

    for i in range(start, len(byte_array)):
        if i % interval == 0:
            # Note: return value of flip_one_bit is bytes, not a byte
            byte_array[i] = flip_one_bit(byte_array[i])[0]
            n += 1

    return n

# flip `num' bites randomly chosen within `byte_array'
def flip_n_bits(byte_array, start, n):
    targets = []

    while len(targets) < n:
        new_target = random.randint(start, len(byte_array))
        if new_target in targets:
            continue
        else:
            targets.append(new_target)

    for i in targets:
        byte_array[i] = flip_one_bit(byte_array[i])[0]
        
def main():
    filename = "./vege"
    img = Image.open(filename + ".jpg", "r")
    f = io.BytesIO()

    img.save(f, format="jpeg")

    b = f.getbuffer()

    index = 0
    marker = 0

    # SOI
    # These 2 lines cannot be inside the while loop,
    # as SOI doesn't have length field but all other fields have one.
    marker = get_marker(b, index)
    index += 2

    # 0xFFDA == SOS (Start of Scan), after which the actual data comes
    while marker != 0xFFDA:
        marker = get_marker(b, index)
        index += 2

        length = get_length(b, index)
        index += length

    #interval = 1024 * 32
    #n = flip_with_interval(b, index, interval)
    n = 8
    flip_n_bits(b, index, n)

    print("Injected %d bits of error" % n)
    
    f_out = open(filename + "_error.jpg", "wb")
    f_out.write(b)
    f_out.close()

if __name__ == "__main__":
    main()
