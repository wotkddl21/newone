
i = 0
while True:
    try:
        a = 10 / i
        i -= 1
        print(a)
        break
        #print(contents)
    except Exception as e:
        print(e)
        continue
