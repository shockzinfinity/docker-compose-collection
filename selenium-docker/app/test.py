import sys

if len(sys.argv) == 1:
    print("No Args!")
else:
    for i in range(1, len(sys.argv)):
        print(i, ":", sys.argv[i])
