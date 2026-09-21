name = input("Whats is your name ? \n")
age = int(input("How old are you ? \n"))

if  32 > age >= 18 :
    print(f"Hello {name} ! Welcome Aboard \n You are an Adult !")

elif age < 18:
    print(f"Hello {name} ! Welcome Aboard \n You are Teenager !")
else:
    print(f"Hello {name} ! Welcome Aboard \n You are Old enough now !")
    
    
for _ in name:
    print( _ , end="_")
    
def future_age(years: int):
    print(f"\nAfter {years} year/years you will be {years + age}")

future_age(20)
future_age(30)