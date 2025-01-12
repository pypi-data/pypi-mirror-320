def caesar_cipher_decrypt(ciphertext, shift):
    """Decrypt a Caesar cipher."""
    decrypted = ""
    for char in ciphertext:
        if char.isalpha():
            shift_base = 65 if char.isupper() else 97
            decrypted += chr((ord(char) - shift_base - shift) % 26 + shift_base)
        else:
            decrypted += char
    return decrypted
