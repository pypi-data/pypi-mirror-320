import string
from os import system, path
from sys import platform
import tkinter
import tkinter.filedialog

root = tkinter.Tk()
root.withdraw()

COMMAND = [*"12"]

def check(arg1, arg2) -> bool:
    for k in arg1:
        if k in arg2:
            return True
    return False

def Caesar(user_input, shift) -> str:
    output = ""
    ALPHABET, ALPHABET_UPPER = [*string.ascii_lowercase], [*string.ascii_uppercase]
    shifted =  ALPHABET[shift % 26:] + ALPHABET[:shift % 26]
    shifted_upper = ALPHABET_UPPER[shift % 26:] + ALPHABET_UPPER[:shift % 26]
    for k in user_input:
        if k in ALPHABET:
            output += shifted[ALPHABET.index(k)]
        elif k in ALPHABET_UPPER:
            output += shifted_upper[ALPHABET_UPPER.index(k)]
        else:
            output += k
    return output

def fileProcessor(file_name, output_file, shift) -> None:
    with open(file_name, encoding = "latin-1") as data:
        with open(output_file, "w", encoding = "latin-1") as out:
            out.write(Caesar(data.read(), shift))

def clear():
    if platform == "win32":
        system("cls")
    else:
        system("clear")

def IsInt(inp) -> bool:
    try:
        int(inp)
        return True
    except ValueError:
        return False

def main() -> None:
    clear()
    while True:
        run = True
        cmd = input("""1. Enciphering.
2. Deciphering. 
3. Exit.
Your input: """).strip()
        if cmd == "3":
            clear()
            exit(0)
        elif not cmd:
            clear()
            print("Invalid input: Empty input. \n")
            continue
        elif cmd not in COMMAND:
            clear()
            print("Invalid input: Command does not exist. \n")
            continue
        
        clear()
        while run:
            mode = input("""1. Input from keyboard.
2. Input from file.
3. Cancel.
Your input: """).strip()
            if mode == "3":
                clear()
                break
            elif mode == "2":
                clear()
                input_file = tkinter.filedialog.askopenfilename(title="Choose your input file (cancel to go back to menu)", 
                                                                filetypes=[("All files", "*.*")])
                if not input_file:
                    return
            elif mode not in COMMAND:
                clear()
                print("Invalid input: Mode does not exist. \n")
                continue

            clear()
            while mode == "2" and run:
                output_file = input("""Type the name of your output file, leave empty for the default name (output.txt)
(If the name does not contain an extension then the program will automatically add a .txt extension): """).strip()
                if check(output_file, [*'\\/:*?"<>|']) and not output_file:
                    print("Invalid input: Illegal file name (file name cannot contains \"\\/:*?\"<>|\"). \n")
                elif output_file == input_file:
                    print("Invalid input: Output file cannot be the same name as input file. \n")
                elif not output_file:
                    output_file = "output.txt"
                    run = False
                elif output_file[len(output_file) - 1] != "." or "." not in output_file:
                    output_file += ".txt"
                    run = False
            
            while mode == "2":
                clear()
                output_folder = tkinter.filedialog.askdirectory(title="Choose your output folder")
                if output_folder:
                    output_dir = path.join(output_folder, output_file)
                    break

            clear()
            while mode == "1" and run:
                user_input = [*input("Your input: ").strip()]
                if not user_input:
                    clear()
                    print("Invalid input: Empty input. \n")
                else:
                    clear()
                    run = False

        clear()
        while mode != "3":
            shift = input("Shift (type / to cancel): ").strip()
            if IsInt(shift) and mode == "1":
                clear()
                if cmd == "1": print(f"Output: {Caesar(user_input, int(shift))}")
                elif cmd == "2": print(f"Output: {Caesar(user_input, -int(shift))}")
            elif IsInt(shift) and mode == "2":
                clear()
                if cmd == "1": fileProcessor(input_file, output_dir, int(shift))
                elif cmd == "2": fileProcessor(input_file, output_dir, -int(shift))
            elif shift == "/":
                clear()
                break
            elif not shift:
                clear()
                print("Invalid input: Empty input. \n")
            else:
                clear()
                print("Invalid input: Not an integer. \n")
        
if __name__ == "__main__":
    while True:
        main()