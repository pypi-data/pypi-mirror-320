import base64
import os

def to_hex_string(byte_values):
    return ''.join([hex(byte)[2:].zfill(2) for byte in byte_values])

def from_hex_string(hex_string):
    return bytes.fromhex(hex_string)

def xor_with_key(byte_list, key):
    return [byte ^ key[i % len(key)] for i, byte in enumerate(byte_list)]

def generate_xor_key(key_length=16):
    return os.urandom(key_length)

def combine_keys(key1, key2):
    return bytes([(key1[i] + key2[i]) % 256 for i in range(len(key1))])

def string_to_executable_list(code):
    return [ord(c) for c in code]

def encryptData(code):
    executable_list = string_to_executable_list(code)
    
    base64_encoded = base64.b64encode(code.encode('utf-8')).decode('utf-8')

    xor_key1 = generate_xor_key()
    xor_key2 = generate_xor_key()
    xor_key3 = combine_keys(xor_key1, xor_key2)

    hex_encoded = to_hex_string(base64_encoded.encode('utf-8'))

    byte_list = [str(byte) for byte in from_hex_string(hex_encoded)]

    byte_list_xored = xor_with_key([int(byte) for byte in byte_list], xor_key3)

    byte_list_xored.append(xor_key3[-1])

    custom_encoded = '||||'.join(map(str, byte_list_xored)) + '###' + '||||'.join(map(str, xor_key1)) + '###' + '||||'.join(map(str, xor_key2)) + '###' + 'extra_data_here'

    return custom_encoded

def encodeData(custom_encoded):
    parts = custom_encoded.split('###')

    byte_list = parts[0].split('||||')
    byte_values = [int(byte) for byte in byte_list]

    xor_key1 = [int(byte) for byte in parts[1].split('||||')]
    xor_key2 = [int(byte) for byte in parts[2].split('||||')]
    xor_key3 = combine_keys(bytes(xor_key1), bytes(xor_key2))

    byte_values = xor_with_key(byte_values[:-1], xor_key3)

    decoded_base64_str = bytes(byte_values).decode('latin1')

    decoded_ascii_str = base64.b64decode(decoded_base64_str).decode('utf-8')

    return decoded_ascii_str

# decrypt and execute data
def daed(custom_encoded):
    parts = custom_encoded.split('###')

    byte_list = parts[0].split('||||')
    byte_values = [int(byte) for byte in byte_list]

    xor_key1 = [int(byte) for byte in parts[1].split('||||')]
    xor_key2 = [int(byte) for byte in parts[2].split('||||')]
    xor_key3 = combine_keys(bytes(xor_key1), bytes(xor_key2))

    byte_values = xor_with_key(byte_values[:-1], xor_key3)

    decoded_base64_str = bytes(byte_values).decode('latin1')
    decoded_ascii_str = base64.b64decode(decoded_base64_str).decode('utf-8')

    exec(decoded_ascii_str)