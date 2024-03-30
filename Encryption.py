# Encryption parameters
multiplier = 7
adder = 13
modulus = 10

def encrypt(code):
    code = str(code)

    # Encrypt each digit using the parameters
    encrypted_code = ''
    for digit in code:
        encrypted_digit = (int(digit) * multiplier + adder) % modulus
        encrypted_code += str(encrypted_digit)
    
    return (encrypted_code)

def decrypt(code):
    code = str(code)

    # Decrypt each digit using the parameters
    decrypted_code = ''
    for digit in code:
        decrypted_digit = (int(digit) - adder) * pow(multiplier, -1, modulus) % modulus
        decrypted_code += str(decrypted_digit)
    
    return (decrypted_code)