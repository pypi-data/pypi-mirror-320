sentence = "how many vowels are in this exact sentence?"
vowels = "aeiouAEIOU"
count = 0
for char in sentence:
    if char in vowels:
        count += 1
print(count)
