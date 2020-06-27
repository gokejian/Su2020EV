def decode_action(s_action):
    res = []
    str_list = f'{s_action:015b}'.split()
    for str_elem in str_list:
        res.append(int(str_elem))
    return res

print(decode_action(16))