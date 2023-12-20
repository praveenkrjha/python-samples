import numpy as np
from qiskit import *
from math import gcd
import random
from random import randint

qasm_sim = Aer.get_backend('qasm_simulator')

def period(a, N):
    """
    Calculate the period of 'a' modulo 'N' using Quantum Circuit.
    """
    available_qubits = 16 
    r = -1   
    
    if N >= 2**available_qubits:
        print(str(N) + ' is too big for IBMQX')
    
    qr = QuantumRegister(available_qubits)   
    cr = ClassicalRegister(available_qubits)
    qc = QuantumCircuit(qr, cr)
    x0 = random.randint(1, N-1) 
    x_binary = np.zeros(available_qubits, dtype=bool)
    
    for i in range(1, available_qubits + 1):
        bit_state = (N % (2**i) != 0)
        if bit_state:
            N -= 2**(i-1)
        x_binary[available_qubits-i] = bit_state    
    
    for i in range(0, available_qubits):
        if x_binary[available_qubits-i-1]:
            qc.x(qr[i])
    x = x0
    
    while np.logical_or(x != x0, r <= 0):
        r += 1
        qc.measure(qr, cr) 
        for i in range(0,3): 
            qc.x(qr[i])
        qc.cx(qr[2],qr[1])
        qc.cx(qr[1],qr[2])
        qc.cx(qr[2],qr[1])
        qc.cx(qr[1],qr[0])
        qc.cx(qr[0],qr[1])
        qc.cx(qr[1],qr[0])
        qc.cx(qr[3],qr[0])
        qc.cx(qr[0],qr[1])
        qc.cx(qr[1],qr[0])

        result = execute(qc, backend=qasm_sim, shots=1024).result()
        counts = result.get_counts()
        
        results = [[],[]]
        for key, value in counts.items(): 
            results[0].append(key)
            results[1].append(int(value))
        s = results[0][np.argmax(np.array(results[1]))]
    return r

def shors_breaker(N):
    """
    Shor's algorithm implementation to factorize the given 'N'.
    """
    N = int(N)
    while True:
        a = random.randint(0, N-1)
        g = gcd(a, N)
        if g != 1 or N == 1:
            return g, N//g
        else:
            r = period(a, N) 
            if r % 2 != 0:
                continue
            elif pow(a, r//2, N) == -1:
                continue
            else:
                p = gcd(pow(a, r//2)+1, N)
                q = gcd(pow(a, r//2)-1, N)
                if p == N or q == N:
                    continue
                return p, q

def mod_inverse(a, m):
    """
    Calculate the modular inverse of 'a' modulo 'm'.
    """
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return -1

def generate_keypair(keysize):
    p = randint(1, 1000)
    q = randint(1, 1000)
    nMin = 1 << (keysize - 1)
    nMax = (1 << keysize) - 1
    primes = [2]
    start = 1 << (keysize // 2 - 1)
    stop = 1 << (keysize // 2 + 1)
    if start >= stop:
        return []
    for i in range(3, stop + 1, 2):
        for p in primes:
            if i % p == 0:
                break
        else:
            primes.append(i)
    while (primes and primes[0] < start):
        del primes[0]
    # Select two random prime numbers p and q
    while primes:
        p = random.choice(primes)
        primes.remove(p)
        q_values = [q for q in primes if nMin <= p * q <= nMax]
        if q_values:
            q = random.choice(q_values)
            break
    # Calculate n
    n = p * q
    # Calculate phi
    phi = (p - 1) * (q - 1)
    # Select e
    e = random.randrange(1, phi)
    g = gcd(e, phi)
    # Calculate d
    while True:
        e = random.randrange(1, phi)
        g = gcd(e, phi)
        d = mod_inverse(e, phi)
        if g == 1 and e != d:
            break

    return ((e, n), (d, n))

def encrypt(plaintext, package):
    e, n = package
    ciphertext = [pow(ord(c), e, n) for c in plaintext]
    return ''.join(map(lambda x: str(x), ciphertext)), ciphertext

def decrypt(ciphertext, package):
    d, n = package
    plaintext = [chr(pow(c, d, n)) for c in ciphertext]
    return (''.join(plaintext))

bit_length = int(input("Enter bit length (max 4 bits supported on quantum simulators): "))

public_key, private_key = generate_keypair(2**bit_length)
print(f"Public key:  {public_key}")
print(f"Private key: {private_key}")

N_shor = public_key[1]
assert N_shor > 0, "Input must be positive"
p, q = shors_breaker(N_shor)
phi = (p - 1) * (q - 1)  
d_shor = mod_inverse(public_key[0], phi)

plain_txt = input("Enter a message: ")
cipher_txt, cipher_obj = encrypt(plain_txt, public_key)

print("Encrypted message: {}".format(cipher_txt))

print('Message decrypted with Shor\'s Algorithm: {} '.format(decrypt(cipher_obj, (d_shor, N_shor))))
