# Caesar Cipher Tool<sup><sup>TM</sup></sup> - Python Edition
A simple program use to Encipher/Decipher text to/from Caesar Cipher.
And yes, there are more versions of this program from other programming languages.

## How this thing works
1. It slices the alphabet from the index of shift then add the sliced part to the start of the alphabet.
2. Find the index of every character in user input in the alphabet and append the character with the same index into the output. Add the character into the output if it doesn't exist in the alphabet.

## Functionalities
Encipher/Decipher text to/from Caesar Cipher. This have 2 modes:
1. Input from keyboard: Good for inputting short texts and quickly Encipher/Decipher them.
2. Input from file: Good for processing a large amount of text, result will be put into another file, you can input the file name you desire, or leave blank to use the default name (output.txt). You have to specify the directory for the output file in case you select this mode.

## Installation
<ol type="1">
  <li>
    Install Python 3.x from <a href="https://www.python.org/downloads/" target="_blank">here</a>. (Ignore if you already have Python 3.x installed)
  </li>
  <li>
    Open terminal, run:
    
```
pip install caesar_cipher_tool_pye_edition
```
  </li>
</ol>

## Usage
<ol type="1">
  <li>
    Open terminal, run:

```
cct
```
  </li>
  <li>
    Alternatively, in a Python file (*.py), you can do:
    
```
from caesar_cipher_tool_pye_edition import main
main()
```
To use the program.
  </li>
  <li>
    Similarly, you can do:
    
```
from caesar_cipher_tool_pye_edition.main import Caesar
```
To use the ciphering function.
(Syntax: Caesar({user_input}, {shift}) with user_input = user input, shift = shift, enter minus shift in order to decipher texts to use the ciphering function.)
  </li>
</ol>

## Requirement(s)
1.  Python 3.x

## Note(s)
1. While the input from file mode support pretty much any file type, anything other than plain text files (*.txt,...) could cause the program to freeze up (e.g *.exe,...) so avoid inputting those.

## License
This project is licensed under the GNU General Public License 3.0, check [LICENSE](LICENSE) for more details.
