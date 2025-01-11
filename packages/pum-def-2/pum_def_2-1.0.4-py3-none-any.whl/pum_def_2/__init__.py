def merge_sort(massive: list) -> list:
    "Merge sort of of the list[int]"
    def merge(A: list, B: list):
        res = []
        i = 0
        j = 0
        while i < len(A) and j < len(B):
            if A[i] <= B[j]:
                res.append(A[i])
                i += 1
            else:
                res.append(B[j])
                j += 1
        res += A[i:] + B[j:]
        return res

    if len(massive) <= 1:
        return(massive)
    else:
        l = massive[:len(massive)//2]
        r = massive[len(massive)//2:]
    return (
        merge(merge_sort(l), merge_sort(r)))

def select_sort(massive: list) -> list:
    "Selection sort of the list[int]"
    for i in range(len(massive)-1):
        x = massive[i]
        m = i
        for j in range(i+1, len(massive)):
            if a[j] < x:
                x = massive[j]
                m = j
        massive[m], massive[i] = massive[i], massive[m]
    return massive

def insertion_sort(massive: list) -> list:
    "Insertion sort of the list[int]"
    for i in range(1,len((massive))):
        temp = massive[i]
        j = i - 1
        while (j >= 0 and temp < massive[j]):
            massive[j+1] = massive[j]
            j = j - 1
        massive[j+1] = temp
    return massive

def buble_sort(massive: list) -> list:
    "Buble sort of the list[int]"
    for i in range(len(massive)-1):
        for j in range(len(massive)-i-1):
            if massive[j+1] < massive[j]:
                massive[j], massive[j+1] = massive[j+1], massive[j]
    return massive

def count_sort(massive: list) -> list:
    "Count sort of the list[int]"
    from collections import defaultdict
    def mx(massive):
        max_element = massive[0]
        for i in range(len(massive)):
            if massive[i] > max_element:
                max_element = massive[i]
        return max_element

    def mn(massive):
        min_element = massive[0]
        for i in range(len(massive)):
            if massive[i] < min_element:
                min_element = massive[i]
        return min_element
    
    count = defaultdict(int)

    for i in massive:
        count[i] += 1
    result = []
    for j in range(mn(massive), (mx(massive)+1)):
        if count.get(j) is not None:
            for i in range(count.get(j)):
                result.append(j)
    return result

def quick_sort(massive):
    "Quick sort of the list[int]"
    from random import choice

    if len(massive)<= 1:
        return massive
    else:
        q = choice(massive)
        l_nums = [n for n in massive if n < q]
        e_nums = [q]
        r_nums = [n for n in massive if n > q]
        return quick_sort(l_nums) + e_nums + quick_sort(r_nums)

def binary_search_left(element: int, massive: list) -> int:
    "Binary search of int element from left boundary"
    left = -1
    right = len(massive)
    while right - left > 1:
        middle = (left + right) // 2
        if massive[middle] < element:
            left = middle
        else:
            right = middle
    return left + 1

def binary_search_right(element: int, massive: list) -> int:
    "Binary search of int element from right boundary"
    left = -1
    right = len(element)
    while right - left > 1:
        middle = (left + right) // 2
        if element[middle] <= massive:
            left = middle
        else:
            right = middle
    return right - 1

def to_base(number: int, base: int) -> str:
    "Converts int number to base<=36"
    if base > 36:
        raise Exception('radix is geater than expected')
    ans = ''
    while number > 0:
        number, remainder = divmod(number, base)
        if remainder > 9:
            remainder = chr(ord('A') + remainder - 10)
        ans = str(remainder) + ans
    return ans

def to_int(number: str, base: int) -> int:
    "Converts str number to base<=36"
    number = str(number)
    if base > 36:
        raise Exception('radix is geater than expected')
    table = {'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15, 'G': 16, 'H': 17, 'I': 18, 'J': 19, 'K': 20, 'L': 21,
             'M': 22, 'N': 23, 'O': 24, 'P': 25, 'Q': 26, 'R': 27, 'S': 28, 'T': 29, 'U': 30, 'W': 32, 'X': 33, 'Y': 34,
             'Z': 35}
    s = 0
    for i in range(len(number)):
        if number[i].isalpha():
            a = int(len(number) - 1 - i)
            b = base ** a
            c = table.get(number[i])
            s += c * b
        else:
            a = int(len(number) - 1 - i)
            b = base ** a
            c = int(number[i])
            s += c * b
    return s

def max_index(massive: list) -> int:
    "Returns int index of the max element"
    max_index = 0
    for i in range(len(massive)):
        if massive[i] > massive[max_index]:
            max_index = i
    return max_index

def min_index(massive: list) -> int:
    "Returns int index of the min element"
    min_index = 0
    for i in range(len(massive)):
        if massive[i] < massive[min_index]:
            min_index = i
    return min_index

def arinc429_bnr_generator() -> None:
    """Function for generating ARINC429 messages through console \n 
BNR only, SDI as label extension"""
    message = ''

    print("""Select label:
    001 Distance to go
    012 Ground speed
    100 Selected radial on VOR
    101 Heading select
    102 Selected altitude
    104 Selected altitude rate
    105 QFU
    114 Selected airspeed/mach
    116 Cross track distance
    117 NAV vertical divation
    140 Flight director yaw command
    141 Flight director roll command
    142 Fast/slow indicator
    143 Fligth director pitch command
    162 ADF1
    173 Localizer
    205 Glide slope
    206 Indicated airspeed
    210 True airspeed
    212 Barometric altitude rate
    222 Omnibearing on VOR
    270 Alert and To-From bitfield
    312 Ground speed
    313 True track angle
    314 True heading
    320 Magnetic heading
    321 Ground speed
    324 Pitch angle
    325 Roll angle
    335 Track rate angle
    365 Inertial vertical velocity""")
    selected_label = input()
    if selected_label not in ['001', '012', '100', '102', '104', '105', '114', '116', '117', '140', '141', '141', '142', '143', '162', '173', '205', '206', '210', '212', '222', '270', '312', '313', '314', '320', '321', '324', '325', '335', '365']:
        raise SystemExit("wrong label")
    label = str(bin(int(selected_label)))[2::]
    while len(label) < 10:
        label = '0' + label
    message += label

    print("enter data (must be less then 262143)")
    selected_data = bin(int(input()))[2::]
    if len(selected_data) > 18:
        raise SystemExit('selected data must be less then 262143')
    while len(selected_data) < 18:
        selected_data = '0' + selected_data
    message += selected_data

    print("""enter data sign (29th bit)
0 Plus, North, East, Right, To, Above
1 Minus, South, West, Left, From, Below""")
    selected_sign = input()
    if selected_sign != '0' and selected_sign != '1':
        raise SystemExit("wrong data sign")
    message += selected_sign

    print("""enter SSM
    00 Failure Warning
    01 No Computed Data
    10 Functional Test
    11 Normal Operation""")
    selected_ssm = input()
    if selected_ssm != '00' and selected_ssm != '01' and selected_ssm != '10' and selected_ssm != '11':
        raise SystemExit("wrong ssm")
    message += selected_ssm

    print("enter parity (1bit)")
    selected_parity = input()
    if selected_parity != '0' and selected_parity != '1':
        raise SystemExit("wrong parity")
    message += selected_parity

    print(message)