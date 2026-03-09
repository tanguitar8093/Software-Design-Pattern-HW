def leetcode_string_histogram():
    ss = "  d ...ka%&*ba9c0   .... dz" 
    counts = [0] * 26
    for char in ss:
        ascii_val = ord(char)
        if ascii_val >= 97 and ascii_val <= 122:
            index = ascii_val - 97
        # if 'a' <= char <= 'z':    
            counts[index] += 1
    for i, count in enumerate(counts):
            if count > 0:
                char = chr(ord('a') + i)
                print(f"{char} {count}")

leetcode_string_histogram()