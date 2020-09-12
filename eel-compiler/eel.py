#Gkavardinas Othonas, AM: 2620, username: cse42620
#Mpourlh Stulianh, AM: 2774, username: cse42774

import sys

#read filename from command line and open it (in form: python3 met.py test.eel)
file = sys.argv[1]
#file=input("Please input a file:\n") #other case, user inserts file name

try:
    f = open(file, 'rb')
except IOError:
    print ("Could not read file:", file)
    exit()

#initializing end of file position
eof = f.seek(0,2)
f.seek(0,0)

#declaration of global variables
token=""
value=""
lines = 0

#~~~~~~~~~~~~~~~~~~~~

#declaration of global variables for intermediate code
quadsList = []

temp_var = 0
program_name = ''

procedures = []
functions = []
is_function = False

exitlist = []

#~~~~~~~~~~~~~~~~~~~~

#declaration of global variables for symbol table
scopes = []
main_scope = {}
main_scope["main_sq"] = 0
main_scope["main_fl"] = 0

#~~~~~~~~~~~~~~~~~~~~

#declaration of global variables for semantic analysis
needsReturn = []
hasReturn = []

repeatChecker = []

#~~~~~~~~~~~~~~~~~~~~

#declaration of global variables for final code
asm_name = sys.argv[1][:-4]
asmFile = open(asm_name+".asm", 'w') #open test.asm file for writing

current_quadToASM = 0
pars = []

#~~~~~~~~~~~~~~~~~~~~

def  nextquad():
    global quad_counter
    global quadsList

    temp = str(len(quadsList))
    return temp

def genquad(op, x, y, z):
    global quadsList
    global quad_counter

    quads = [nextquad(), [op, x, y, z]]
    quadsList.append(quads)
    return quads

def newtemp():
    global temp_var

    temp = 'T_' + str(temp_var)
    temp_var += 1
    addEntity(temp, "tempvar", None)  #symbol table
    return temp

def emptylist():

    temp = []
    return temp

def makelist(x):

    temp = []
    temp.append(x)
    return temp

def merge(list1, list2):

    temp = list1 + list2
    return temp

def backpatch(mylist, z):
    global quadsList

    for p in mylist:
        for i in quadsList:
            if p == i[0]:
                i[1][3] = z

####

def lex():
    global token
    global value
    global lines
    global eof

    #states, rows of the matrix
    state0 = 0
    state1 = 1
    state2 = 2
    state3 = 3
    state4 = 4
    state5 = 5
    state6 = 6
    state7 = 7
    state8 = 8
    state9 = 9
    error = -1
    OK = -2

    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    numbers = '0123456789'
    whitespace = [' ','\t','\r']
    reserved_words = ['program','endprogram','declare','enddeclare','if','then','else','endif','while','endwhile',
                      'repeat','endrepeat','exit','switch','case','endswitch','forcase','when','endforcase','procedure',
                      'endprocedure','function','endfunction','call','return','in','inout','and','or','not','true','false',
                      'input','print']

    #words, columns of the matrix
    letter = 0
    digit = 1
    plus = 2
    minus = 3
    asterisk = 4
    slash = 5
    less = 6
    greater = 7
    equals = 8
    colon = 9
    semicolon = 10
    comma = 11
    open_round_bracket = 12
    close_round_bracket = 13
    open_square_bracket = 14
    close_square_bracket = 15
    end_of_file = 16
    end_of_line = 17
    other = 18

    #transition matrix
    T = [[state1,state2,OK,OK,OK,state6,state3,state4,OK,state5,OK,OK,OK,OK,OK,OK,OK,state0,state0],
         [state1,state1,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK],
         [error,state2,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK],
         [OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK],
         [OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK],
         [OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK],
         [OK,OK,OK,OK,state8,state7,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK],
         [state7,state7,state7,state7,state7,state7,state7,state7,state7,state7,state7,state7,state7,state7,state7,state7,state7,state0,state7],
         [state8,state8,state8,state8,state9,state8,state8,state8,state8,state8,state8,state8,state8,state8,state8,state8,error,state8,state8],
         [state8,state8,state8,state8,state8,state0,state8,state8,state8,state8,state8,state8,state8,state8,state8,state8,error,state8,state8]]

    flag_slash = False #case of line comments
    flag_star = False #case of block comments
    flag_less = False #case of < character
    flag_letter = False #case of word starts with letter

    state = state0
    word = 0
    comments = 0
    chars = ""

    while state!=OK and state!=error:
        if f.seek(0,1) == eof:
            value = ""
            token = "eoftk"
            if flag_star == True:
                print("Lex_Error: Line",comments,"-> Comments open and never get closed!")
            break

        c = f.read(1)
        c = c.decode('ascii')

        if c in alphabet:
            word = letter
            if flag_slash != True and flag_star != True: #if character isn't in comments
                flag_letter = True #word starts with letter
                chars += c
                if flag_letter == True and f.seek(0,1) == eof: #last character of file
                    value = chars
                    if chars in reserved_words:
                        token = chars+'tk'
                    else:
                        token = 'idtk'
                    #flag_letter = False
                    break
                else:
                    d = f.read(1) #check next character
                    d = d.decode('ascii')
                    f.seek(-1, 1) #go back to previous position
                    if (d not in alphabet) and (d not in numbers): #last character of the word
                        if len(chars) > 30: #check len of word
                            chars = chars[0:30]
                        if chars in reserved_words:
                            value = chars
                            token = chars + 'tk'
                        else:
                            value = chars
                            token = 'idtk'
                        flag_letter = False
                        break
        elif c in numbers:
            word = digit
            if flag_slash != True and flag_star != True: #if character isn't in comments
                chars += c
                if  f.seek(0,1) == eof: #last character of file
                    value = int(chars)
                    token = 'numbertk'
                    break
                else:
                    d = f.read(1)
                    d = d.decode('ascii')
                    f.seek(-1,1)
                    if (d in alphabet) and flag_letter == False: #if letter after number
                        #read full wrong word
                        d = f.read(1)
                        d = d.decode('ascii')
                        while d in alphabet or d in numbers:
                            d = f.read(1)
                            d = d.decode('ascii')
                        f.seek(-1,1)
                        value = ""
                        token = ""
                        print("Lex_Error: Line",lines,"-> Found letter after number!")
                        exit()
                    elif (d not in alphabet) and (d not in numbers) and flag_letter == False: #word is number
                        if int(chars) < 32767:
                            value = int(chars)
                            token = 'numbertk'
                            break
                    elif (d not in alphabet) and (d not in numbers) and flag_letter == True: #word is id
                        value = chars
                        token = 'idtk'
                        break
        elif c == '+' :
            word = plus
            if flag_slash != True and flag_star != True: #if character isn't in comments
                chars += c
                value = chars
                token = 'plustk'
        elif c == '-' :
            word = minus
            if flag_slash != True and flag_star != True:
                chars += c
                value = chars
                token = 'minustk'
        elif c == '*':
            word = asterisk
            if flag_slash != True and flag_star != True:
                chars += c
                value = chars
                token = 'asterisktk'
        elif c == '/':
            word = slash
            d = f.read(1) #check next character
            d = d.decode('ascii')
            f.seek(-1,1) #go back to previous position
            if state == state9: #close block comments
                flag_star = False
            elif d == '/' : #open line comments
                flag_slash = True
            elif d == '*': #open block comments
                flag_star = True
                comments = lines #position comments open
            elif flag_slash != True and flag_star != True: #slash character
                chars += c
                value = chars
                token = 'slashtk'
                break
        elif c == '<':
            word = less
            if flag_slash != True and flag_star != True: #if character isn't in comments
                chars += c
                d = f.read(1)
                d = d.decode('ascii')
                f.seek(-1,1)
                if d == '>' or d == '=':
                    flag_less = True #word starts with < and next character is > or =
                else: #less character
                    value = chars
                    token = 'lesstk'
                    break
        elif c == '>':
            word = greater
            if flag_slash != True and flag_star != True:
                chars += c
                if flag_less == True: #previous character was <
                    value = chars
                    token = 'notequalstk'
                    break
                else: #greater character
                    d = f.read(1)
                    d = d.decode('ascii')
                    f.seek(-1,1)
                    if d != '=':
                        value = chars
                        token = 'greatertk'
                        break
        elif c == '=':
            word = equals
            if flag_slash != True and flag_star != True:
                chars += c
                if chars == '>=': #previous character was >
                    value = chars
                    token = 'greaterequalstk'
                elif chars == '<=': #previous character was <
                    value = chars
                    token = 'lessequalstk'
                elif chars == ':=': #previous character was :
                    value = chars
                    token = 'assignmenttk'
                else: #equals character
                    value = chars
                    token = 'equalstk'
        elif c == ':':
            word = colon
            if flag_slash != True and flag_star != True:
                chars += c
                d = f.read(1)
                d = d.decode('ascii')
                f.seek(-1,1)
                if d != '=': #colon character, next character isn't equals
                    value = chars
                    token = 'colontk'
                    break
        elif c == ';':
            word = semicolon
            if flag_slash != True and flag_star != True:
                chars += c
                value = chars
                token = 'semicolontk'
        elif c == ',':
            word = comma
            if flag_slash != True and flag_star != True:
                chars += c
                value = chars
                token = 'commatk'
        elif c == '(':
            word = open_round_bracket
            if flag_slash != True and flag_star != True:
                chars += c
                value = chars
                token = 'openroundbrackettk'
        elif c == ')':
            word = close_round_bracket
            if flag_slash != True and flag_star != True:
                chars += c
                value = chars
                token = 'closeroundbrackettk'
        elif c == '[':
            word = open_square_bracket
            if flag_slash != True and flag_star != True:
                chars += c
                value = chars
                token = 'opensquarebrackettk'
        elif c == ']':
            word = close_square_bracket
            if flag_slash != True and flag_star != True:
                chars += c
                value = chars
                token = 'closesquarebrackettk'
        elif c == '\n': #new line character
            lines += 1 #increase counter for lines
            if flag_slash == True and flag_star != True: #if character is in line comments
                word = end_of_line
                flag_slash = 0 #close line comments
            else:
                word = other #new line character is whitespace character
        elif c in whitespace:
            word = other
        else: #unsupported character
            word = other
            print("Lex_Error: Line",lines,"-> Symbol `",c,"` is not valid symbol!")
            value = ""
            token = ""
            exit()

        #next state
        state = T[state][word]

######################################################

def program():
    global token
    global lines
    global value
    global program_name
    global needsReturn
    global hasReturn

    lex()
    if token=="programtk":
        lex()
        if token=="idtk":
            addScope()  #symbol table
            program_name = value  #intermediate code
            lex()
            needsReturn.append(False)  #semantic analysis
            hasReturn.append(False)  #semantic analysis
            block(program_name)  #intermediate code
            if token=="endprogramtk":
                lex()
                if token=="eoftk":
                    pass
                else:
                    print("Warning: Line",lines,"-> Text found after 'endprogram' keyword!")
                    exit()
            else:
                lex()
                if token=="eoftk":
                    print("Syntax_Error: Line",lines,"-> Missing 'endprogram' keyword!")
                    exit()
                else:
                    print("Syntax_Error: Line", lines,"-> Missing ';', between statements")
                    exit()
        else:
            print("Syntax_Error: Line",lines,"-> Missing Program id!")
            exit()
    else:
        print("Syntax_Error: Line",lines,"-> Missing 'program' keyword!")
        exit()

######################################################

def block(name):
    global needsReturn
    global hasReturn
    global lines

    global token

    declarations()
    subprograms()
    genquad("begin_block",name,"_","_")  #intermediate code
    SQ = nextquad()  #symbol table
    if name == program_name:  #symbol table
        main_scope["main_sq"] = SQ  #symbol table
    else:  #symbol table
        setSQ(SQ)  #symbol table
    statements()

    if name == program_name:
        genquad("halt","_","_","_")  #intermediate code
    if needsReturn[len(needsReturn)-1]==True and hasReturn[len(needsReturn)-1]==False:  #semantic analysis
        print("Semantic_Error: Line", lines, "-> In function ", name, " missing return statement!")  #semantic analysis
        exit()  #semantic analysis
    elif needsReturn[len(needsReturn)-1]==False and hasReturn[len(needsReturn)-1]==True:  #semantic analysis
        if name == program_name:  #semantic analysis
            print("Semantic_Error: Line", lines, "-> Found return statement in main function!")  #semantic analysis
        else:  #semantic analysis
            print("Semantic_Error: Line", lines, "-> Found return statement in procedure ", name, " !")  #semantic analysis
        exit()  #semantic analysis
    needsReturn.pop()  #semantic analysis
    hasReturn.pop()  #semantic analysis
    genquad("end_block",name,"_","_")  #intermediate code
    calculateFL()  #symbol table
    if name == program_name:  #final code
        finalCode(True)
    else:
        finalCode(False)
    removeScope()  #symbol table


######################################################

def declarations():
    global token
    global lines

    if token=="declaretk":
        lex()
        varlist()
        if token=="enddeclaretk":
            lex()
        else:
            print("Syntax_Error: Line",lines,"-> Missing enddeclare keyword!")
            exit()

#####################################################

def varlist():
    global token
    global lines
    global value

    if token=="idtk":
        checkEntityExists(value)  #semantic analysis
        addEntity(value, "variable", None)  #symbol table
        lex()
        while token=="commatk":
            lex()
            if token=="idtk":
                checkEntityExists(value)  #semantic analysis
                addEntity(value, "variable", None)  #symbol table
                lex()
            else:
                print("Syntax_Error: Line",lines,"-> Bad usage of comma, id expected!")
                exit()
    elif token=="enddeclaretk":
        pass
    else:
        print("Syntax_Error: Line",lines,"->",value,"is not an id!")
        exit()


#####################################################

def subprograms():
    global token
    global lines

    while token=="proceduretk" or token=="functiontk":
        procorfunc()

#####################################################

def procorfunc():
    global token
    global lines
    global value
    global functions
    global procedures
    global needsReturn
    global hasReturn

    if token=="proceduretk":
        needsReturn.append(False)  #semantic analysis
        hasReturn.append(False)  #semantic analysis
        lex()
        if token=="idtk":
            checkEntityExists(value)  #semantic analysis
            addEntity(value, "procorfunc", "procedure")  #symbol table
            addScope()  #symbol table
            procedures.append(value)  #intermediate code
            name = value  #intermediate code
            lex()
            procorfuncbody(name)
            if token=="endproceduretk":
                lex()
            else:
                print("Syntax_Error: Line",lines,"-> Missing 'endprocedure' word. Procedure never ends!")
                exit()
        else:
            print("Syntax_Error: Line",lines,"-> Missing procedure id!")
            exit()
    elif token=="functiontk":
        needsReturn.append(True)  #semantic analysis
        hasReturn.append(False)  #semantic analysis
        lex()
        if token=="idtk":
            checkEntityExists(value)  #semantic analysis
            addEntity(value, "procorfunc", "function")  #symbol table
            addScope()  #symbol table
            functions.append(value)  #intermediate code
            name = value #intermediate code
            lex()
            procorfuncbody(name)
            if token=="endfunctiontk":
                lex()
            else:
                print("Syntax_Error: Line",lines,"-> Missing 'endfunction' word. Function never ends!")
                exit()
        else:
            print("Syntax_Error: Line",lines,"-> Missing function id!")
            exit()

#####################################################

def procorfuncbody(name):
    formalpars()
    block(name)

#####################################################

def formalpars():
    global token
    global lines

    if token=="openroundbrackettk":
        lex()
        formalparlist()
        if token=="closeroundbrackettk":
            lex()
        else:
            print("Syntax_Error: Line",lines,"-> Missing ')' character. Brackets never close!")
            exit()
    else:
        print("Syntax_Error: Line",lines,"-> Missing '('. No brackets detected!")
        exit()

#####################################################

def formalparlist():
    global token
    global lines

    formalparitem()
    while token=="commatk":
        lex()
        formalparitem()

#####################################################

def formalparitem():
    global token
    global lines
    global value

    if token=="intk" or token=="inouttk":
        PARMODE = value
        addArgument(PARMODE)  #symbol table
        lex()
        if token=="idtk":
            checkEntityExists(value)  #semantic analysis
            addEntity(value, "parameter", PARMODE)  #symbol table
            lex()
        else:
            print("Syntax_Error: Line",lines,"-> Missing id!")
            exit()

######################################################

def statements():
    global token
    global lines

    statement()
    while token=="semicolontk":
        lex()
        statement()

######################################################

def statement():
    global token
    global lines

    if token=="idtk":
        assignment_stat()
    elif token=="iftk":
        if_stat()
    elif token=="whiletk":
        while_stat()
    elif token=="repeattk":
        repeat_stat()
    elif token=="exittk":
        exit_stat()
    elif token=="switchtk":
        switch_stat()
    elif token=="forcasetk":
        forcase_stat()
    elif token=="calltk":
        call_stat()
    elif token=="returntk":
        return_stat()
    elif token=="inputtk":
        input_stat()
    elif token=="printtk":
        print_stat()

######################################################

def assignment_stat():
    global token
    global lines
    global value

    searchEntity(value, "VAR")  #symbol table
    NAME = value  #intermediate code
    lex()
    if token=="assignmenttk":
        lex()
        E_place = expression()  #intermediate code
        genquad(":=",E_place,"_",NAME)  #intermediate code
    else:
        print("Syntax_Error: Line",lines,"-> Missing assignment symbol!")
        exit()

#######################################################

def if_stat():
    global token
    global lines

    lex()
    B = condition()  #intermediate code
    B_true = B[0]  #intermediate code
    B_false = B[1]  #intermediate code
    if token=="thentk":
        lex()
        backpatch(B_true,nextquad())  #intermediate code
        statements()
        if token=="endiftk":
            backpatch(B_false,nextquad())  #intermediate code
            lex()
        elif token=="elsetk":
            ifList = makelist(nextquad())  #intermediate code
            genquad("jump","_","_","_")  #intermediate code
            backpatch(B_false,nextquad())  #intermediate code
            elsepart()
            backpatch(ifList,nextquad())  #intermediate code
            if token=="endiftk":
                lex()
        else:
            print("Syntax_Error: Line",lines,"-> Missing 'endif' word. If command never ends!")
            exit()
    else:
        print("Syntax_Error: Line",lines,"-> Missing 'then' word!")
        exit()

########################################################

def elsepart():
    global token
    global lines

    lex()
    statements()

########################################################

def repeat_stat():
    global token
    global lines
    global exitlist
    global repeatChecker

    repeatChecker.append(False)  #semantic analysis
    lex()
    Bquad = nextquad()  #intermediate code
    statements()
    if token=="endrepeattk":
        if repeatChecker[len(repeatChecker)-1] == False:  #semantic analysis
            print("Semantic_Error: Line", lines, "-> No exit statement inside repeat statement!")  #semantic analysis
            exit()  #semantic analysis
        repeatChecker.pop()
        lex()
        genquad("jump","_","_",Bquad)  #intermediate code
        tmplist = makelist(nextquad())  #intermediate code
        exitlist = merge(exitlist,tmplist)  #intermediate code
        backpatch(exitlist, nextquad())  #intermediate code
    else:
        print("Syntax_Error: Line",lines,"-> Missing 'endrepeat' word. Repeat command never ends!")
        exit()

########################################################

def exit_stat():
    global token
    global lines
    global exitlist
    global repeatChecker

    exitlist.append(nextquad())  #intermediate code
    genquad("jump", "_", "_", "_")  #intermediate code

    if len(repeatChecker) == 0:  #semantic analysis
        print("Semantic_Error: Line", lines, "-> Found exit statement, out of repeat statement!")  #semantic analysis
        exit()  #semantic analysis
    elif len(repeatChecker) > 0:  #semantic analysis
        repeatChecker[len(repeatChecker)-1] = True  #semantic analysis

    lex()

########################################################

def while_stat():
    global token
    global lines

    lex()
    Bquad = nextquad()  #intermediate code
    B = condition()  #intermediate code
    B_true = B[0]  #intermediate code
    B_false = B[1]  #intermediate code
    backpatch(B_true,nextquad())  #intermediate code
    statements()
    genquad("jump","_","_",Bquad)  #intermediate code
    backpatch(B_false,nextquad())  #intermediate code
    if token=="endwhiletk":
        lex()
    else:
        print("Syntax_Error: Line",lines,"-> Missing 'endwhile' word. While command never ends!")
        exit()

#########################################################

def switch_stat():
    global token
    global lines

    lex()
    exitlist = emptylist()  #intermediate code
    EXP_1 = expression()  #intermediate code
    if token=="casetk":
        lex()
        EXP_2 = expression()  #intermediate code
        R_true = makelist(nextquad())  #intermediate code
        genquad("=",EXP_1,EXP_2,"_")  #intermediate code
        R_false = makelist(nextquad())  #intermediate code
        genquad("jump","_","_","_")  #intermediate code
        if token=="colontk":
            lex()
            backpatch(R_true, nextquad())  #intermediate code
            statements()
            tlist = makelist(nextquad())  #intermediate code
            genquad("jump","_","_","_")  #intermediate code
            exitlist = merge(exitlist,tlist)  #intermediate code
            backpatch(R_false, nextquad())  #intermediate code
            while True:
                if token=="casetk":
                    lex()
                    EXP_2 = expression()  #intermediate code
                    R_true = makelist(nextquad())  #intermediate code
                    genquad("=",EXP_1,EXP_2,"_")  #intermediate code
                    R_false = makelist(nextquad())  #intermediate code
                    genquad("jump","_","_","_")  #intermediate code
                    if token=="colontk":
                        lex()
                        backpatch(R_true, nextquad())  #intermediate code
                        statements()
                        tlist = makelist(nextquad())  #intermediate code
                        genquad("jump","_","_","_")  #intermediate code
                        exitlist = merge(exitlist,tlist)  #intermediate code
                        backpatch(R_false, nextquad())  #intermediate code
                    else:
                        print("Syntax_Error: Line",lines,"-> Missing ':' character!")
                        exit()
                elif token=="endswitchtk":
                    lex()
                    backpatch(exitlist, nextquad())  #intermediate code
                    break
                else:
                    print("Syntax_Error: Line",lines,"-> Missing 'endswitch'. Switch command never ends!")
                    exit()
        else:
            print("Syntax_Error: Line",lines,"-> Missing ':' character!")
            exit()
    else:
        print("Syntax_Error: Line",lines,"-> Missing 'case' word!")
        exit()

##########################################################

def forcase_stat():
    global token
    global lines

    lex()
    flag = newtemp()  #intermediate code
    firstquad = nextquad()  #intermediate code
    genquad(":=","0","_",flag)  #intermediate code
    if token=="whentk":
        lex()
        COND = condition()  #intermediate code
        COND_true = COND[0]  #intermediate code
        COND_false = COND[1]  #intermediate code
        if token=="colontk":
            lex()
            backpatch(COND_true, nextquad())  #intermediate code
            statements()
            genquad(":=","1","_",flag)  #intermediate code
            backpatch(COND_false, nextquad())  #intermediate code
            while True:
                if token=="whentk":
                    lex()
                    COND = condition()  #intermediate code
                    COND_true = COND[0]  #intermediate code
                    COND_false = COND[1]  #intermediate code
                    if token=="colontk":
                        lex()
                        backpatch(COND_true, nextquad())  #intermediate code
                        statements()
                        genquad(":=","1","_",flag)  #intermediate code
                        backpatch(COND_false, nextquad())  #intermediate code
                    else:
                        print("Syntax_Error: Line",lines,"-> Missing ':' character!")
                        exit()
                elif token=="endforcasetk":
                    genquad("=",flag,"1",firstquad)  #intermediate code
                    lex()
                    break
                else:
                    print("Syntax_Error: Line",lines,"-> Missing 'endforcase'. Forcase command never ends!")
                    exit()
        else:
            print("Syntax_Error: Line",lines,"-> Missing ':' character!")
            exit()
    else:
        print("Syntax_Error: Line",lines,"-> Missing 'when' word!")
        exit()

##########################################################

def call_stat():
    global token
    global lines
    global value

    lex()
    if token=="idtk":
        searchEntity(value, "PROC")  #semantic analysis
        NAME = value  #intermediate code
        lex()
        actualpars(NAME)  #intermediate code
        genquad("call",NAME,"_","_")  #intermediate code
    else:
        print("Syntax_Error: Line",lines,"-> Missing call id!")
        exit()

##########################################################

def actualpars(id_name):
    global token
    global lines
    global is_function

    if token=="openroundbrackettk":
        lex()
        if token!="closeroundbrackettk":
            actualparlist(id_name)
        if token=="closeroundbrackettk":
            lex()
        else:
            print("Syntax_Error: Line",lines,"-> Missing ')' character. Brackets never close!")
            exit()
        if is_function == True:  #intermediate code
            return_value = newtemp()  #intermediate code
            genquad("par",return_value,"ret","_")  #intermediate code
            genquad("call",id_name,"_","_")  #intermediate code
            is_function = False  #intermediate code
            return return_value  #intermediate code
    else:
        print("Syntax_Error: Line",lines,"-> Missing '('. No brackets detected!")
        exit()

##########################################################

def actualparlist(id_name):
    global token
    global lines

    number_of_pars = 0  #semantic analysis
    PARS = []

    PARMODE = actualparitem()
    PARS.append(PARMODE)
    number_of_pars += 1  #semantic analysis
    while token=="commatk":
        lex()
        PARMODE = actualparitem()
        PARS.append(PARMODE)
        number_of_pars += 1  #semantic analysis
    checkArguments(id_name, PARS)

##########################################################

def actualparitem():
    global token
    global lines
    global value

    PARMODE = ""  #semantic analysis

    if token=="intk":
        lex()
        EXP = expression()  #intermediate code
        genquad("par",EXP,"in","_")  #intermediate code
        PARMODE = "in"  #semantic analysis
    elif token=="inouttk":
        lex()
        if token=="idtk":
            searchEntity(value, "VAR")  #symbol table
            NAME = value  #intermediate code
            lex()
            genquad("par",NAME,"inout","_")  #intermediate code
        else:
            print("Syntax_Error: Line",lines,"-> Missing id!")
            exit()
        PARMODE = "inout"  #semantic analysis
    else:
        print("Syntax_Error: Line",lines,"-> Missing 'in' or 'inout' word!")
        exit()
    return PARMODE  #semantic analysis

###########################################################

def return_stat():
    global token
    global lines
    global hasReturn

    hasReturn[len(hasReturn)-1] = True  #semantic analysis
    lex()
    E_place = expression()  #intermediate code
    genquad("ret",E_place,"_","_")  #intermediate code

    return E_place  #intermediate code

###########################################################

def print_stat():
    global token
    global lines

    lex()
    E_place = expression()  #intermediate code
    genquad("out", E_place, "_", "_")  #intermediate code

##########################################################

def input_stat():
    global token
    global lines
    global value

    lex()
    if token=="idtk":
        searchEntity(value, "VAR")  #symbol table
        id_place = value  #intermediate code
        lex()
        genquad("inp", id_place, "_", "_")  #intermediate code
    else:
        print("Syntax_Error: Line",lines,"-> Missing id name!")
        exit()

##########################################################

def condition():
    global token
    global lines

    Q1 = boolterm()  #intermediate code
    B_true = Q1[0]  #intermediate code
    B_false = Q1[1]  #intermediate code
    while token=="ortk":
        lex()
        backpatch(B_false, nextquad())  #intermediate code
        Q2 = boolterm()  #intermediate code
        B_true = merge(B_true, Q2[0])  #intermediate code
        B_false = Q2[1]  #intermediate code
    return [B_true, B_false]  #intermediate code

###########################################################

def boolterm():
    global token
    global lines

    R1 = boolfactor()  #intermediate code
    Q_true = R1[0]  #intermediate code
    Q_false = R1[1]  #intermediate code
    while token=="andtk":  #intermediate code
        lex()
        backpatch(Q_true, nextquad())  #intermediate code
        R2 = boolfactor()  #intermediate code
        Q_false = merge(Q_false, R2[1])  #intermediate code
        Q_true = R2[0]  #intermediate code
    return [Q_true, Q_false]  #intermediate code

###########################################################

def boolfactor():
    global token
    global lines

    if token=="nottk":
        lex()
        if token=="opensquarebrackettk":
            lex()
            B = condition()  #intermediate code
            R_true = B[0]  #intermediate code
            R_false = B[1]  #intermediate code
            if token=="closesquarebrackettk":
                lex()
            else:
                print("Syntax_Error: Line",lines,"-> Missing ']' character. Brackets never close!")
                exit()
            return [R_false, R_true]  #intermediate code
        else:
            print("Syntax_Error: Line",lines,"-> Missing brackets!")
            exit()
    elif token=="opensquarebrackettk":
        lex()
        B = condition()  #intermediate code
        R_true = B[0]  #intermediate code
        R_false = B[1]  #intermediate code
        if token=="closesquarebrackettk":
            lex()
        else:
            print("Syntax_Error: Line",lines,"-> Missing ']' character. Brackets never close!")
            exit()
        return [R_true, R_false]  #intermediate code
    elif token=="plustk" or token=="minustk" or token=="numbertk" or token=="idtk" or token=="openroundbrackettk":
        E1_place = expression()  #intermediate code
        RELOP = relational_oper()  #intermediate code
        E2_place = expression()  #intermediate code
        R_true = makelist(nextquad())  #intermediate code
        genquad(RELOP, E1_place, E2_place, "_")  #intermediate code
        R_false = makelist(nextquad())  #intermediate code
        genquad("jump","_","_","_")  #intermediate code
        return [R_true, R_false]  #intermediate code
    elif token=="truetk":
        lex()
        R_true = makelist(nextquad())  #intermediate code
        genquad("jump","_","_","_")  #intermediate code
        return [R_true, []]  #intermediate code
    elif token=="falsetk":
        lex()
        R_false = makelist(nextquad())  #intermediate code
        genquad("jump","_","_","_")  #intermediate code
        return [[], R_false]  #intermediate code
    else:
        print("Syntax_Error: Line",lines,"-> Missing bool factor!")
        exit()

############################################################

def expression():
    global token
    global lines

    SIGN = optional_sign()  #intermediate code
    if SIGN == "-":  #intermediate code
        T1_place = "-"+str(term())  #intermediate code
    else:
        T1_place = str(term())  #intermediate code

    while token=="plustk" or token=="minustk":
        SIGN = add_oper()  #intermediate code
        T2_place = str(term())  #intermediate code
        w = newtemp()  #intermediate code
        genquad(SIGN,T1_place,T2_place,w)  #intermediate code
        T1_place = w  #intermediate code
    E_place=T1_place  #intermediate code
    return E_place  #intermediate code

############################################################

def term():
    global token
    global lines

    F1_place = factor()  #intermediate code
    while token=="asterisktk" or token=="slashtk":
        OPER = mul_oper()
        F2_place = factor()  #intermediate code
        w = newtemp()  #intermediate code
        genquad(OPER,F1_place,F2_place,w)  #intermediate code
        F1_place = w  #intermediate code
    T_place = F1_place  #intermediate code
    return T_place  #intermediate code

############################################################

def factor():
    global token
    global lines
    global value

    F_place=""  #intermediate code

    if token=="numbertk":
        F_place = value  #intermediate code
        lex()
    elif token=="openroundbrackettk":
        lex()
        E_place = expression()  #intermediate code
        if token=="closeroundbrackettk":
            lex()
            F_place = E_place  #intermediate code
        else:
            print("Syntax_Error: Line",lines,"-> Missing ')' character. Brackets never close!")
            exit()
    elif token=="idtk":
        id_name = value  #intermediate code
        lex()
        return_value = idtail(id_name)  #intermediate code
        if return_value == "IS_ID":  #intermediate code
            searchEntity(id_name, "VAR")  #symbol table
            F_place = id_name  #intermediate code
        else:
            searchEntity(id_name, "FUNC")  #symbol table
            F_place = return_value  #intermediate code
    else:
        print("Syntax_Error: Line",lines,"-> No number, or expression or id typed!")
        exit()
    return F_place  #intermediate code

#############################################################

def idtail(id_name):
    global token
    global lines
    global is_function

    if token=="openroundbrackettk":
        is_function = True  #intermediate code
        return_value = actualpars(id_name)  #intermediate code
        return return_value  #intermediate code
    else:
        return "IS_ID"  #intermediate code

#############################################################

def relational_oper():
    global token
    global lines
    global value

    if token=="equalstk" or token=="lessequalstk" or token=="greaterequalstk" or token=="greatertk" or token=="lesstk" or token=="notequalstk":
        RELOP = value  #intermediate code
        lex()
    else:
        print("Syntax_Error: Line",lines,"-> Missing '=' or '<=' or '>=' or '>' or '<' or '<>' operator symbol!")
        exit()
    return RELOP  #intermediate code

############################################################

def add_oper():
    global token
    global lines
    global value

    if token=="plustk" or token=="minustk":
        SIGN = value  #intermediate code
        lex()
    else:
        print("Syntax_Error: Line",lines,"-> Missing '+' '-' operator symbol!")
        exit()
    return SIGN  #intermediate code

############################################################

def mul_oper():
    global token
    global lines
    global value

    if token=="asterisktk" or token=="slashtk":
        OPER = value  #intermediate code
        lex()
    else:
        print("Syntax_Error: Line",lines,"-> Missing '*' or '/' operator symbol!")
        exit()
    return OPER  #intermediate code

############################################################

def optional_sign():
    global token
    global lines

    if token=="plustk" or token=="minustk":
        SIGN = add_oper()  #intermediate code
        return SIGN  #intermediate code
    else:
        return ""  #intermediate code

############################################################

def productIntFile(): #write intermediate code in file (in form: test.int)
    global quadsList

    int_name = sys.argv[1][:-4]
    f = open(int_name+".int", "w") #open test.int file for writing

    for i in range(len(quadsList)): #write in file contents of quadsList
        f.write(str(quadsList[i][0]) +":"+str(quadsList[i][1][0])+","+str(quadsList[i][1][1])+","+str(quadsList[i][1][2])+","+str(quadsList[i][1][3])+"\n")

    f.close() #close test.int file

############################################################

def productCFile(): #product code in C (in form: test.c)
    varList = [] #list for variables
    variables = "" #string with variables
    contentsInMain = [] #contents for main block
    L_counter = 1 #counter for Labels

    int_name = sys.argv[1][:-4]
    f = open(int_name+".int", "r") #open test.int for reading

    for line in f: #read line by line

        line = line.replace(":"," ",1) #replace : character with " "
        line = line.replace(","," ") #replace , character with " "
        line = line.replace("\n","") #replace \n character with " "

        words = line.split(" ") #split line in " " character, result in list words

        #in any case save contents in List contentsInMain and variables in List varList
        if words[1] == ":=":
            contentsInMain.append("\tL_" + str(L_counter) + ": " + str(words[4]) + "=" + str(words[2]) + ";\n")
            varList.append(words[4])
        elif words[1] == "+":
            contentsInMain.append("\tL_" + str(L_counter) + ": " + str(words[4]) + "=" + str(words[2]) + "+" + str(words[3]) + ";\n")
            varList.append(words[4])
        elif words[1] == "-":
            contentsInMain.append("\tL_" + str(L_counter) + ": " + str(words[4]) + "=" + str(words[2]) + "-" + str(words[3]) + ";\n")
            varList.append(words[4])
        elif words[1] == "*":
            contentsInMain.append("\tL_" + str(L_counter) + ": " + str(words[4]) + "=" + str(words[2]) + "*" + str(words[3]) + ";\n")
            varList.append(words[4])
        elif words[1] == "/":
            contentsInMain.append("\tL_" + str(L_counter) + ": " + str(words[4]) + "=" + str(words[2]) + "/" + str(words[3]) + ";\n")
            varList.append(words[4])
        elif words[1] == "<":
            contentsInMain.append("\tL_" + str(L_counter) + ": " + "if (" + str(words[2]) + "<" + str(words[3]) + ") goto L_" + str(int(words[4])) + ";\n")
            varList.append(words[2])
        elif words[1] == ">":
            contentsInMain.append("\tL_" + str(L_counter) + ": " + "if (" + str(words[2]) + ">" + str(words[3]) + ") goto L_" + str(int(words[4])) + ";\n")
            varList.append(words[2])
        elif words[1] == "<=":
            contentsInMain.append("\tL_" + str(L_counter) + ": " + "if (" + str(words[2]) + "<=" + str(words[3]) + ") goto L_" + str(int(words[4])) + ";\n")
            varList.append(words[2])
        elif words[1] == ">=":
            contentsInMain.append("\tL_" + str(L_counter) + ": " + "if (" + str(words[2]) + ">=" + str(words[3]) + ") goto L_" + str(int(words[4])) + ";\n")
            varList.append(words[2])
        elif words[1] == "=":
            contentsInMain.append("\tL_" + str(L_counter) + ": " + "if (" + str(words[2]) + "==" + str(words[3]) + ") goto L_" + str(int(words[4])) + ";\n")
            varList.append(words[2])
        elif words[1] == "<>":
            contentsInMain.append("\tL_" + str(L_counter) + ": " + "if (" + str(words[2]) + "!=" + str(words[3]) + ") goto L_" + str(int(words[4])) + ";\n")
            varList.append(words[2])
        elif words[1] == "out":
            contentsInMain.append("\tL_" + str(L_counter) + ": " + "printf(\"%d\\n\", " + words[2] + ");\n")
        elif words[1] == "inp":
            contentsInMain.append("\tL_" + str(L_counter) + ": " + "scanf(\"%d\", &" + words[2] + ");\n")
        elif words[1] == "jump":
            contentsInMain.append("\tL_" + str(L_counter) + ": " + "goto L_" + str(int(words[4])) + ";\n")
        elif words[1] == "halt":
            contentsInMain.append("\tL_" + str(L_counter) + ": {}\n")
            contentsInMain.append("}")
        else:
            L_counter -= 1 #ignore begin_block, end_block
        L_counter += 1 #increase counter for Labels

    f.close() #close test.int file

    if varList != []:
        for i in range(0,len(set(varList))-2): #create string with variables in form "var,var,var,...,var;"
            variables += list(set(varList))[i]
            variables += ","
        variables += varList[len(set(varList))-1]
        variables += ";"

    c_name = sys.argv[1][:-4]
    cFile = open(c_name+".c", 'w') #open test.c file for writing

    cFile.write("#include <stdio.h>\n")
    cFile.write("\n")
    cFile.write("int main()\n")
    cFile.write("{\n")
    if varList != []:
        cFile.write("\tint " + variables + "\n") #write string with variables at the beginning of the main block
    cFile.write("\tL_0: \n")

    for c in contentsInMain: #write the contents from contentsInMain List in main block
        cFile.write(c)

    cFile.close() #close test.c file

############################################################
#SYMBOL TABLE!!
def addScope(): #create and init a scope and add it to the list scopes
    global scopes

    scope = {}
    scope["entities"] = []
    scope["nestingLevel"] = len(scopes)
    scope["current_offset"] = 12
    scopes.append(scope)

def calculateFL(): #calculate value of Frame Length and add it in the right field
    global scopes

    FL = 12
    for entity in scopes[len(scopes)-1]["entities"]:
        if entity["entity_type"] != "procorfunc":
            FL += 4
    if len(scopes) == 1:
        main_scope["main_fl"] = FL
    else:
        entitiesLength = len(scopes[len(scopes)-2]["entities"])
        scopes[len(scopes)-2]["entities"][entitiesLength-1]["frame_length"] = FL

def removeScope(): #remove a scope, and also mark the creation of a proc or func
    global scopes #this compiler doesen't support recursion, so I need to track if a function is ready for use

    entitiesLength = len(scopes[len(scopes)-2]["entities"])
    if entitiesLength > 0:
        scopes[len(scopes)-2]["entities"][entitiesLength - 1]["READY"] = True

    scopes.pop()

def addEntity(entity_name, entity_type, par3): #create and init an entity and insert it in the entities list of the current scope
    global scopes #par3 is here only for a few cases

    entity = {}
    entity["entity_name"] = entity_name
    entity["entity_type"] = entity_type

    if entity_type == "variable":
        entity["offset"] = scopes[len(scopes)-1]["current_offset"]
        scopes[len(scopes)-1]["current_offset"] += 4
    elif entity_type == "procorfunc":
        entity["function_type"] = par3
        entity["arguments"] = []
        entity["start_quad"] = 0
        entity["frame_length"] = 0
        entity["READY"] = False
    elif entity_type == "parameter":
        entity["parMode"] = par3
        entity["offset"] = scopes[len(scopes)-1]["current_offset"]
        scopes[len(scopes)-1]["current_offset"] += 4
    elif entity_type == "tempvar":
        entity["offset"] = scopes[len(scopes)-1]["current_offset"]
        scopes[len(scopes)-1]["current_offset"] += 4

    scopes[len(scopes)-1]["entities"].append(entity)

def addArgument(parMode): #create and init an argument and add it in the list of a proc or func entity
    global scopes

    argument = {}
    argument["parMode"] = parMode

    entitiesLength = len(scopes[len(scopes)-2]["entities"])
    if entitiesLength > 0:
        scopes[len(scopes)-2]["entities"][entitiesLength-1]["arguments"].append(argument)


def searchEntity(name, TYPE): #check if a variable is valid, if not ERROR happens.
    global scopes #special case here TYPE == "PROCORFUNC", doesen't check but just returns the entity
    global lines #special case here TYPE == "VAR" doesen't refer only to variables

    for scope in reversed(scopes):
        for entity in scope["entities"]:
            if name == entity["entity_name"]:
                if TYPE == "VAR":
                    if entity["entity_type"] in ["variable", "parameter", "tempvar"]:
                        return entity
                elif TYPE == "PROC" and entity["READY"] == True:
                    if entity["entity_type"] == "procorfunc" and entity["function_type"] == "procedure":
                        return entity
                elif TYPE == "FUNC" and entity["READY"] == True:
                    if entity["entity_type"] == "procorfunc" and entity["function_type"] == "function":
                        return entity
                elif TYPE == "PROCORFUNC":
                    return entity
    print("Semantic_Error: Line", lines+1, "-> Entity type:", TYPE, "", name, " not found!")
    exit()

def checkEntityExists(name): #checks for duplicates of an entity
    global scopes #it happens only in the current scope
    global lines #it uses only the name of the entity, eg. var A with name X, and func B with name X cannot exist in the same scope

    for entity in scopes[len(scopes)-1]["entities"]:
        if name == entity["entity_name"]:
            print("Semantic_Error: Line", lines, "-> Entity ", name, " already exists!")
            exit()

def setSQ(start_quad): #setter for Start Quad
    global scopes

    entitiesLength = len(scopes[len(scopes)-1]["entities"])
    if entitiesLength > 0:
        scopes[len(scopes)-1]["entities"][entitiesLength-1]["start_quad"] = start_quad

def checkArguments(id_name, pars): #checks if a proc or func is defined with a list of pars
    global lines

    entity = searchEntity(id_name, "PROCORFUNC")

    if len(entity["arguments"]) != len(pars):
        print("Semantic_Error: Line", lines, "-> In ", entity["entity_type"], " ", entity["entity_name"], " wrong number of arguments!")
        exit()
    i = 0
    for parameter in pars:
        if entity["arguments"][i]["parMode"] != parameter:
            print("Semantic_Error: Line", lines, "-> In ", entity["entity_type"], " ", entity["entity_name"], " wrong type of arguments!")
            exit()
        i += 1

#Functions used for Final Code
def getScopeDistance(variable): #returns the distance of a variable. This function is used in gnlvcode()
    global scopes

    distance = -1
    for scope in reversed(scopes):
        distance += 1
        for entity in scope["entities"]:
            if entity["entity_name"] == variable:
                return distance

def getEntityField(entity_name, field): #getter for entity fields
    global scopes #we have 2 special cases here, (1)return a whole entity, (2)return the scope that cointains the entity

    for scope in reversed(scopes):
        for entity in scope["entities"]:
            if entity["entity_name"] == entity_name:
                if field == "scope":
                    return scope
                elif field == "entity":
                    return entity
                else:
                    return entity[field]

def checkVariableType(variable): #does some important job for loadvr and storerv functions
    global scopes #determines the type of a variable and returns it as a string

    if str(variable).lstrip("-").isdigit():
        return "immediate"

    variableScope = getEntityField(variable, "scope")

    if variableScope["nestingLevel"] == 0:
        return "global"

    variableType = getEntityField(variable, "entity_type")
    variableEntity = getEntityField(variable, "entity")


    if variableType == "variable":
        if variableScope["nestingLevel"] == scopes[len(scopes)-1]["nestingLevel"]:
            return "varCurr"
        elif variableScope["nestingLevel"] < scopes[len(scopes)-1]["nestingLevel"]:
            return "varNoCurr"
    elif variableType == "parameter":
        if variableEntity["parMode"] == "in":
            if variableScope["nestingLevel"] == scopes[len(scopes)-1]["nestingLevel"]:
                return "parInCurr"
            elif variableScope["nestingLevel"] < scopes[len(scopes)-1]["nestingLevel"]:
                return "parInNoCurr"
        elif variableEntity["parMode"] == "inout":
            if variableScope["nestingLevel"] == scopes[len(scopes)-1]["nestingLevel"]:
                return "parInoutCurr"
            elif variableScope["nestingLevel"] < scopes[len(scopes)-1]["nestingLevel"]:
                return "parInoutNoCurr"
    elif variableType == "tempvar":
        return "tempvar"


def createCall(callEntity, callee_scope): #very important function.
    global pars #This function is responsible for setting the parameters and calling a proc or func
    global current_quadToASM

    LABEL = current_quadToASM - len(pars) + 1 #setting the parameters
    firstLABEL = LABEL
    i = 0
    for par in pars:
        if LABEL == firstLABEL: #the first time set some more things
            addToASM("L" + str(LABEL) + ":")
            addToASM("\t addi $fp, $sp, " + str(callEntity["frame_length"]))
        else:
            addToASM("L" + str(LABEL) + ":")
        LABEL += 1

        if par[1] == "in":
            loadvr(par[0]["entity_name"], 0)
            addToASM("\t sw $t0, -" + str(12+4*i) + "($fp)")
            i += 1
        elif par[1] == "inout":
            parScope = getEntityField(par[0]["entity_name"], "scope")
            callScope = getEntityField(callEntity["entity_name"], "scope")
            if parScope["nestingLevel"] == callScope["nestingLevel"]:
                A = par[0]["entity_type"] == "variable"
                B = par[0]["entity_type"] == "parameter" and par[0]["parMode"] == "in"
                if A or B:
                    addToASM("\t addi $t0, $sp, -" + str(par[0]["offset"]))
                    addToASM("\t sw $t0, -" + str(12+4*i) + "($fp)")
                    i += 1
                A = par[0]["entity_type"] == "parameter" and par[0]["parMode"] == "inout"
                if A:
                    addToASM("\t lw $t0, -" + str(par[0]["offset"]) + "($sp)")
                    addToASM("\t sw $t0, -" + str(12+4*i) + "($fp)")
                    i += 1
            else:
                A = par[0]["entity_type"] == "variable"
                B = par[0]["entity_type"] == "parameter" and par[0]["parMode"] == "in"
                if A or B:
                    gnlvcode(par[0]["entity_name"])
                    addToASM("\t sw $t0, -" + str(12+4*i) + "($fp)")
                    i += 1
                A = par[0]["entity_type"] == "parameter" and par[0]["parMode"] == "inout"
                if A:
                    gnlvcode(par[0]["entity_name"])
                    addToASM("\t lw $t0, ($t0)")
                    addToASM("\t sw $t0, -" + str(12+4*i) + "($fp)")
                    i += 1
        elif par[1] == "ret":
            addToASM("\t addi $t0, $sp, -" + str(par[0]["offset"]))
            addToASM("\t sw $t0, -8($fp)")

    addToASM("L" + str(LABEL) + ":") #calls the proc or func
    callerScope = getEntityField(callEntity["entity_name"], "scope")
    if callee_scope == callerScope["nestingLevel"]:
        addToASM("\t lw $t0, -4($sp)")
        addToASM("\t sw $t0, -4($fp)")
    else:
        addToASM("\t sw $sp, -4($fp)")
    addToASM("\t addi $sp $sp, " + str(callEntity["frame_length"]))
    addToASM("\t jal " + callEntity["entity_name"])
    addToASM("\t addi $sp $sp, -" + str(callEntity["frame_length"]))

############################################################
#FINAL CODE
def gnlvcode(v): #brings a variable to a register
    addToASM("\t lw  $t0, -4($sp)")
    scopeDistance = getScopeDistance(v)
    scopeDistance -= 1
    while scopeDistance > 0:
        addToASM("\t lw  $t0, -4($t0)")
        scopeDistance -= 1
    entityOffset = getEntityField(v, "offset")
    addToASM("\t addi $t0, $t0, -" + str(entityOffset))

def loadvr(v, r): #loads a value to a specific register
    vType = checkVariableType(v)

    entityOffset = getEntityField(v, "offset")

    if vType == "immediate":
        addToASM("\t li  $t" + str(r) + ", " + str(v))
    elif vType == "global":
        addToASM("\t lw  $t" + str(r) + " -" + str(entityOffset) + "($s0)")
    elif vType in ["varCurr", "parInCurr", "tempvar"]:
        addToASM("\t lw  $t" + str(r) + " -" + str(entityOffset) + "($sp)")
    elif vType == "parInoutCurr":
        addToASM("\t lw  $t0 -" + str(entityOffset) + "($sp)")
        addToASM("\t lw  $t" + str(r) + ", ($t0)")
    elif vType == "varNoCurr" or vType == "parInNoCurr":
        gnlvcode(v)
        addToASM("\t lw  $t" + str(r) + ", ($t0)")
    elif vType == "parInoutNoCurr":
        gnlvcode(v)
        addToASM("\t lw  $t0, ($t0)")
        addToASM("\t lw  $t" + str(r) + ", ($t0)")

def storerv(r, v): #stores a value to a specific register
    vType = checkVariableType(v)

    entityOffset = getEntityField(v, "offset")

    if vType == "global":
        addToASM("\t sw  $t" + str(r) + " -" + str(entityOffset) + "($s0)")
    elif vType in ["varCurr", "parInCurr", "tempvar"]:
        addToASM("\t sw  $t" + str(r) + " -" + str(entityOffset) + "($sp)")
    elif vType == "parInoutCurr":
        addToASM("\t lw  $t0 -" + str(entityOffset) + "($sp)")
        addToASM("\t sw  $t" + str(r) + ", ($t0)")
    elif vType == "varNoCurr" or vType == "parInNoCurr":
        gnlvcode(v)
        addToASM("\t sw  $t" + str(r) + ", ($t0)")
    elif vType == "parInoutNoCurr":
        gnlvcode(v)
        addToASM("\t lw  $t0, ($t0)")
        addToASM("\t sw  $t" + str(r) + ", ($t0)")

def addToASM(string): #writes to the Global ASM file
    global asmFile

    asmFile.write(string+"\n")

def finalCode(isMain): #main function for producing the final code
    global quadsList #it is called when a piece ofintermediate code is set, and the symbol table for this code is ready
    global current_quadToASM #this moment, is an instance before we remove the current scope
    global main_scope
    global pars

    current_scope = 0

    if current_quadToASM == 0:
        addToASM("L0:")
        addToASM("\t j Lmain")

    for quad_number in range(current_quadToASM, len(quadsList)):

        q = quadsList[current_quadToASM] #set this variable = q to shorten it

        if q[1][0] == "jump":
            addToASM("L" + str(int(q[0])+1) + ":")
            addToASM("\t j L" + str(int(q[1][3])+1))
        elif q[1][0] in ["<", ">", "<=", ">=", "=", "<>"]:
            addToASM("L" + str(int(q[0])+1) + ":")
            loadvr(q[1][1], 1)
            loadvr(q[1][2], 2)
            opi = ["<", ">", "<=", ">=", "=", "<>"].index(q[1][0])
            op = ["blt", "bgt", "ble", "bge", "beq", "bne"][opi]
            addToASM("\t " + op + " $t1, $t2, L" + str(int(q[1][3])+1))
        elif q[1][0] == ":=":
            addToASM("L" + str(int(q[0])+1) + ":")
            loadvr(q[1][1], 1)
            storerv(1, q[1][3])
        elif q[1][0] in ["+", "-", "*", "/"]:
            addToASM("L" + str(int(q[0])+1) + ":")
            loadvr(q[1][1], 1)
            loadvr(q[1][2], 2)
            opi = ["+", "-", "*", "/"].index(q[1][0])
            op = ["add", "sub", "mul", "div"][opi]
            addToASM("\t " + op + " $t1, $t1, $t2")
            storerv(1, q[1][3])
        elif q[1][0] == "out":
            addToASM("L" + str(int(q[0])+1) + ":")
            loadvr(q[1][1], 1)
            addToASM("\t move $a0, $t1")
            addToASM("\t li $v0, 1")
            addToASM("\t syscall")
        elif q[1][0] == "inp":
            addToASM("L" + str(int(q[0])+1) + ":")
            addToASM("\t li $v0, 5")
            addToASM("\t syscall")
            addToASM("\t move $t1 $v0")
            storerv(1, q[1][1])
        elif q[1][0] == "ret":
            addToASM("L" + str(int(q[0])+1) + ":")
            loadvr(q[1][1], 1)
            addToASM("\t lw $t0, -8($sp)")
            addToASM("\t sw $t1, ($t0)")
        elif q[1][0] == "par": #we store the parameters in a list of listes in form [entity,mode]
            pars.append([searchEntity(q[1][1], "VAR"), q[1][2]])
        elif q[1][0] == "call":
            callEntity = searchEntity(q[1][1], "PROCORFUNC") #create the call and empty the pars list
            createCall(callEntity, current_scope)
            pars = []
        elif q[1][0] == "begin_block": #we need to know if main function begins here
            if isMain == False:
                addToASM("L" + str(int(q[0])+1) + ":")
                addToASM(str(q[1][1]) + ":")
                addToASM("\t sw $ra, ($sp)")
            else:
                addToASM("Lmain:")
                addToASM("L" + str(int(q[0])+1) + ":")
                addToASM("\t addi $sp, $sp, " + str(main_scope["main_fl"]))
                addToASM("\t move $s0, $sp")
            current_scope += 1;
        elif q[1][0] == "end_block":
            if isMain == False:
                addToASM("L" + str(int(q[0])+1) + ":")
                addToASM("\t lw $ra, ($sp)")
                addToASM("\t jr $ra")
            current_scope -= 1;
        elif q[1][0] == "halt":
            addToASM("L" + str(int(q[0])+1) + ":")

        current_quadToASM += 1 #This counter sets the labels

############################################################

#call program function
program()
productIntFile()
productCFile()
