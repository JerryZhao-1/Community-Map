# n = int(input("Enter a number: "))

# hundreds = n // 100
# tens = (n // 10) % 10
# units = n % 10
# sum_of_digits = hundreds + tens + units
# print("Sum of digits:", sum_of_digits)


# n = int(input())
# q = n // 25
# d = (n % 25) // 10
# ni = (n % 25 % 10) // 5
# p = (n  % 25 % 10 % 5) // 1
# print(q, d, ni, p)

# x = int(input())
# print(abs(x))

x = int(input("Enter a number:"))
y=x
if(x < 0):
    y = -x

print("Absolute value of", x ,"is" , y)