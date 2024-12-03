from SymbolTable import SymbolTable
from Ascii import char_cat
from StateDiagram import *

class Scanner:
    # def __init__(self, file, s_table:SymbolTable, char_cat=char_cat):
    #     '''main initializer, uses file input'''
    #     lines = file.readlines()
    #     l: list[str] = len(lines)
    #     self.lines = dict(zip(range(l), lines))
    #     self.st = s_table
    #     self.char_cat = char_cat

    def __init__(self, inputString, st:SymbolTable, char_cat=char_cat):
        '''Debug initializer, uses string input'''
        self.st = st
        self.char_cat = char_cat

        # Add space before and after each delimiter
        # c = 0
        # while c < len(inputString)-1:
        #     if inputString[c] in self.st.types['del']:
        #         inputString = inputString[:c] + ' ' + inputString[c] + ' ' + inputString[c+1:]
        #         c+=2
        #         continue
        #     c+=1
        
        lines = [inputString]
        l: list[str] = len(lines)
        self.lines = dict(zip(range(l), lines))
        self.tokens = []


    def scan_word(self, word: str) -> tuple[str, str]: # might raise a KeyError or ValueError
        # see if the word was already found
        for key in self.st.types.keys():
            if word.strip() in self.st.types[key]:
                return (word, key)

        # if the word wasn't already found
        forward = word[0]
        if forward == '$': # Variabale
            result = variable_diagram.scan(word)

        elif forward in self.char_cat.uppercase_chars:
            result = class_diagram.scan(word)

        elif forward in self.char_cat.digits: # Numberic
            try:
                result = integer_diagram.scan(word)
            except:
                result = float_diagram.scan(word)
            
        elif forward == '"': # String literal
            result = string_diagram.scan(word)
    
        return result
    

    def scan_group(self, group: str) -> list[tuple[str, str]]:
        group += '#' # acts like 'other', not considered by any State Diagram
        results = []
        first, forward = 0, 0
        while first < len(group) and group != '#': 
            if group[first] in self.st.types['del']:
                # to buffer the potential delimiter
                target = group[first]
                temp = self.scan_word(target)
                results.append(temp)
                self.tokens.append(temp)
                # print(group, target) # Debug
                try:
                    group = group[:first] + group[first+1:]
                except IndexError:
                    break

            elif group and group[first] in self.st.types['opr']:
                # to buffer the entire operator token
                forward += 1
                print(group, forward)
                while (group[forward] in self.st.types['opr']) and (group[forward] != '#'): 
                    forward += 1
                else: # backtrack
                    target = group[first:forward]
                    temp = self.scan_word(target)
                    results.append(temp)
                    self.tokens.append(temp)
                    group = group[:first] + group[forward:]

            elif group and (group[first] == '$' or group[first] in self.char_cat.non_special):

                # to buffer the entire variable token.
                forward += 1
                while (group[forward] in self.char_cat.non_special | set({'.'})) and (group[forward] != '#'):
                    forward += 1
                    # print(group, forward) # Debug
                else: # backtrack
                    target = group[first:forward] # from first to one before forward
                    temp = self.scan_word(target)
                    results.append(temp)
                    self.tokens.append(temp)
                    group = group[:first] + group[forward:]

            elif group and group[first] == '"':
                # to buffer the entire string token
                forward += 1
                while group[forward] in self.char_cat.all_chars - '"': 
                    forward += 1
                else: # no backtrack
                    target = group[first:forward+1]
                    temp = self.scan_word(target)
                    results.append(temp)
                    self.tokens.append(temp)
                    group = group[:first] + group[forward:]
            
            forward = first
                    
        # group = group[:len(group)-1] # Error here
        # print(group)
        return results


    # COMPLETED
    def tokenize(self, word: str) -> list[tuple[str, str]]:
    # def tokenize(self, word: str, file_out) -> list[tuple[str, str]]:
        '''Might raise Key or Value errors'''
        # see if the word was a single token:
        try:
            results = [self.scan_word(word)] 
        except UnboundLocalError:
            try: 
                results = self.scan_group(group=word)
            except UnboundLocalError:
                raise UnboundLocalError("Token not recognized") # change error massage for readability
        except KeyError:
            results = self.scan_group(group=word)
            
            
        
        for r in results:
            print(r)
            self.st.types[r[1]].add(r[0]) # add the token to the Symbol Table
            # Add this to scan_word, also change tokens to be added in scan_group
        return results


    def run(self):
    # def run(self, file_out):
        for i, line in self.lines.items():
            words = line.split() 
                # also splits inside the strings! musn't do that.
                # must concat all members from "* to *"
            for word in words:
                # To catch the exception raised in StateDiagram.scan()
                try:
                    result = self.tokenize(word)
                except KeyError as e:
                    print(f"Error detected at line {i}\n    --> {e}: {word}")
                except ValueError as e:
                    print(f"Error detected at line {i}\n    --> {e}: {word}")
                except UnboundLocalError as e:
                    print(f"Error detected at line {i}\n    --> {e}: {word}")

                finally:
                    # Debug
                    # print(result)
                    # or perhaps fill a file with the result.
                    pass



# Debug

# code = "[ 123.234]]] for[INT ] $I]"
code = "[=<]"

st = SymbolTable()
with open("SymbolTable.out", 'a') as outpuf:
    scanner = Scanner(code, st=st)
    scanner.run()

    for k, v in scanner.st.types.items():
        print(k, v)
    
    for t in scanner.tokens:
        print(t)


