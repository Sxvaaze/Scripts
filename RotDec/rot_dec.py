langs = {
    'gr': ["α", "β", "γ", "δ", "ε", "ζ", "η", "θ", "ι", "κ", "λ", "μ", "ν", "ξ", "ο", "π", "ρ", "σ", "τ", "υ", "φ", "χ", "ψ", "ω"],
    'en': ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u","v", "w", "x", "y", "z"]
}

alphabets = ""
i = 0
for val in langs.keys():
    alphabets += f"({i}). " + val.upper() + "\n"
    i += 1

alphabet = input(f"Please choose a language:\n{alphabets}")
alphabet = alphabet.lower()

while alphabet not in langs.keys():
    alphabet = input(f"Please choose a valid language:\n{alphabets} ")
    alphabet = alphabet.lower()

str_dec = input("Give string to decrypt: ")
rot_num = int(input("Give ROT num: "))

rot_calc = len(langs[alphabet])
rot_num %= rot_calc

str_dec_len = len(str_dec)
output = ""
for i in range(str_dec_len):
    if str_dec[i].isalpha():
        for k in range(rot_calc):
            temp = str_dec[i]
            if str_dec[i].lower() == langs[alphabet][k]:
                if temp == str_dec[i].lower():
                    output += langs[alphabet][(k + rot_num) % rot_calc]
                else:
                    output += langs[alphabet][(k + rot_num) % rot_calc].upper()
    else:
        output += str_dec[i]

print(output) 