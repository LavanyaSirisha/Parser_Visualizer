from collections import deque
from collections import OrderedDict
from functions import *
from tkinter import *
import tkinter as tk
from tkinter import ttk
from firstfollow import *
import firstfollow
from firstfollow import production_list, nt_list as ntl, t_list as tl
# import matplotlib
# matplotlib.use('Agg')

nt_list, t_list=[], []
Data = []
class State:

    _id=0
    def __init__(self, closure):
        self.closure=closure
        self.no=State._id
        State._id+=1

class Item(str):
    def __new__(cls, item, lookahead=list()):
        self=str.__new__(cls, item)
        self.lookahead=lookahead
        return self

    def __str__(self):
        return super(Item, self).__str__()+", "+'|'.join(self.lookahead)
        

def closure(items):

    def exists(newitem, items):

        for i in items:
            if i==newitem and sorted(set(i.lookahead))==sorted(set(newitem.lookahead)):
                return True
        return False


    global production_list

    while True:
        flag=0
        for i in items: 
            
            if i.index('.')==len(i)-1: continue

            Y=i.split('->')[1].split('.')[1][0]

            if i.index('.')+1<len(i)-1:
                lastr=list(firstfollow.compute_first(i[i.index('.')+2])-set(chr(1013)))
                
            else:
                lastr=i.lookahead
            
            for prod in production_list:
                head, body=prod.split('->')
                
                if head!=Y: continue
                
                newitem=Item(Y+'->.'+body, lastr)

                if not exists(newitem, items):
                    items.append(newitem)
                    flag=1
        if flag==0: break

    return items

def goto(items, symbol):

    global production_list
    initial=[]

    for i in items:
        if i.index('.')==len(i)-1: continue

        head, body=i.split('->')
        seen, unseen=body.split('.')


        if unseen[0]==symbol and len(unseen) >= 1:
            initial.append(Item(head+'->'+seen+unseen[0]+'.'+unseen[1:], i.lookahead))

    return closure(initial)


def calc_states():

    def contains(states, t):

        for s in states:
            if len(s) != len(t): continue

            if sorted(s)==sorted(t):
                for i in range(len(s)):
                        if s[i].lookahead!=t[i].lookahead: break
                else: return True

        return False

    global production_list, nt_list, t_list

    head, body=production_list[0].split('->')


    states=[closure([Item(head+'->.'+body, ['$'])])]
    
    while True:
        flag=0
        for s in states:

            for e in nt_list+t_list:
                
                t=goto(s, e)
                if t == [] or contains(states, t): continue

                states.append(t)
                flag=1

        if not flag: break
    
    return states 


def make_table(states):

    global nt_list, t_list

    def getstateno(t):

        for s in states:
            if len(s.closure) != len(t): continue

            if sorted(s.closure)==sorted(t):
                for i in range(len(s.closure)):
                        if s.closure[i].lookahead!=t[i].lookahead: break
                else: return s.no

        return -1

    def getprodno(closure):

        closure=''.join(closure).replace('.', '')
        return production_list.index(closure)

    SLR_Table=OrderedDict()
    
    for i in range(len(states)):
        states[i]=State(states[i])

    for s in states:
        SLR_Table[s.no]=OrderedDict()

        for item in s.closure:
            head, body=item.split('->')
            if body=='.': 
                for term in item.lookahead: 
                    if term not in SLR_Table[s.no].keys():
                        SLR_Table[s.no][term]={'r'+str(getprodno(item))}
                    else: SLR_Table[s.no][term] |= {'r'+str(getprodno(item))}
                continue

            nextsym=body.split('.')[1]
            if nextsym=='':
                if getprodno(item)==0:
                    SLR_Table[s.no]['$']='accept'
                else:
                    for term in item.lookahead: 
                        if term not in SLR_Table[s.no].keys():
                            SLR_Table[s.no][term]={'r'+str(getprodno(item))}
                        else: SLR_Table[s.no][term] |= {'r'+str(getprodno(item))}
                continue

            nextsym=nextsym[0]
            t=goto(s.closure, nextsym)
            if t != []: 
                if nextsym in t_list:
                    if nextsym not in SLR_Table[s.no].keys():
                        SLR_Table[s.no][nextsym]={'s'+str(getstateno(t))}
                    else: SLR_Table[s.no][nextsym] |= {'s'+str(getstateno(t))}

                else: SLR_Table[s.no][nextsym] = str(getstateno(t))

    return SLR_Table

def augment_grammar():

    for i in range(ord('Z'), ord('A')-1, -1):
        if chr(i) not in nt_list:
            start_prod=production_list[0]
            production_list.insert(0, chr(i)+'->'+start_prod.split('->')[0]) 
            return

def main(MainInput):

    global production_list, ntl, nt_list, tl, t_list    

    firstfollow.main(MainInput)
    print(production_list)
    Data.append("FIRST AND FOLLOW OF NON-TERMINALS")
    Data.append(" ")
    for nt in ntl:
        firstfollow.compute_first(nt)
        firstfollow.compute_follow(nt)
        Data.append("{} :".format(nt))
        Data.append("FIRST  :     "+str(firstfollow.get_first(nt)))
        Data.append("FOLLOW :     "+str(firstfollow.get_follow(nt))) 
        Data.append(" ") 
    

    augment_grammar()
    nt_list=list(ntl.keys())
    t_list=list(tl.keys()) + ['$']

    #Data.append(nt_list)
    #Data.append(t_list)

    j=calc_states()

    ctr=0
    Data.append("ITEM SETS :")
    for s in j:
        Data.append(" ")
        Data.append("Item{}:".format(ctr))
        for i in s:
            Data.append("       "+str(i))
        ctr+=1

    table=make_table(j)
    Data.append(' ')
    Data.append("CLR(1) TABLE :")
    sym_list = nt_list + t_list
    sr, rr=0, 0
    Data.append('_____________________________________________________________________')
    Data.append('     |     '+'     |     '.join(sym_list)+'        |')
    Data.append('_____________________________________________________________________')
    for i, j in table.items():
            
        Data.append(str(i)+'     |     '+'     |     '.join(list(j.get(sym,' ') if type(j.get(sym))in (str , None) else next(iter(j.get(sym,' ')))  for sym in sym_list))+'         |')
        s, r=0, 0

        for p in j.values():
            if p!='accept' and len(p)>1:
                p=list(p)
                if('r' in p[0]): r+=1
                else: s+=1
                if('r' in p[1]): r+=1
                else: s+=1      
        if r>0 and s>0: sr+=1
        elif r>0: rr+=1
    Data.append('_____________________________________________________________________')
    Data.append(str(sr)+ " s/r conflicts | "+str(rr)+ " r/r conflicts")
    Data.append(' ')


    
    return table


# CLR MAIN
root = tk.Tk()
root.geometry("600x500")
root.title("CLR Parser")
root.config(bg='#D9D8D7')
paddings = {'padx': 5, 'pady': 5}

style = ttk.Style()
style.configure("TButton", font=("Calibri", 15, "bold"), borderwidth=4)
style.configure("TLabel", font=("Calibri", 15,"bold"), borderwidth=4)
style.configure("TEntry", font=("Calibri", 15,"bold"), borderwidth=4)
style.map("TButton", foreground=[("active", "disabled", "green")],background=[("active", "black")])
#style.theme_use("classic")

frame = tk.Frame(root)
frame.configure(background='#D9D8D7')
frame.pack()

bottomframe = tk.Frame(root)
bottomframe.configure(background='#D9D8D7')
bottomframe.pack()

MainInput = []
str_Input=tk.StringVar()
Input = tk.StringVar()

ttk.Label(frame, text ="Enter the Productions :",background='#D9D8D7').pack(padx=10,pady=10,anchor=W)
InputEntry = ttk.Entry(frame,width=50,textvariable=Input)
InputEntry.pack(ipadx=10,ipady=10,padx=10,anchor=W)

table = OrderedDict()

def display():

    scrollbar1 = Scrollbar(root, bg="green")
    scrollbar1.pack( side = RIGHT, fill = Y )

    scrollbar2 = Scrollbar(root, bg="green")
    scrollbar2.pack( side = BOTTOM, fill = X )

    mylist = Listbox(root,yscrollcommand=scrollbar1.set,xscrollcommand=scrollbar2.set,background='#D9D8D7',font=("Calibri", 15,"bold"),height=100,width=0,highlightthickness=5)

    for i in Data:
        mylist.insert(END,'  '+i)
        #ttk.Label(frame, text=i,background='#D9D8D7').pack(anchor=SW)

    mylist.pack(anchor=CENTER, fill = BOTH,padx=60,pady=10,ipadx=20,ipady=20 )
    scrollbar1.config(command=mylist.yview)
    scrollbar2.config(command=mylist.xview)
        

def add_input():
    MainInput.append(Input.get())
    #ttk.Label(frame, text =Input.get()).pack()
    InputEntry.delete(0,END)
    print(Input.get(),MainInput)

def submit_input():
    global table
    print("entered submit")
    MainInput.append(Input.get())
    table = main(MainInput)
    InputEntry.delete(0,END)
    display()
    #ttk.Label(frame, text ="\n",background='#D9D8D7').pack(padx=10,pady=10,anchor=W)
    #for i in Data:
    #    ttk.Label(frame, text=i,background='#D9D8D7').pack(side=BOTTOM)
        #rc+=1

def oracle(query:str) -> list:
    global table
    Input = query + '$'
    state_log = []

    try:
        stack = ['0']
        a = list(table.items())
        # a=list()
        # Data.append("productions    : "+str(production_list))
        # Data.append('stack'+"                    "+'Input')
        # Data.append(str(*stack)+"                  "+str(*Input))
        state_log.append("productions    : " + str(production_list))
        state_log.append('stack' + "                    " + 'Input')
        state_log.append(str(''.join([*stack])) + "                  " + Input)
        

        while(len(Input) != 0):
            b = list(a[ int(stack[-1]) ] [1] [Input[0]]) # extract production rule for given input from table
            
            if (b[0][0] == "s"): # If shifting
                    #s=Input[0]+b[0][1:]
                stack.append(Input[0]) # Append input string to stack
                stack.append(b[0][1:]) # Append state of transition to stack
                Input=Input[1:] # pop leftmost entry (Input[0])
                # Data.append(str(*stack)+"                  "+str(*Input))
                state_log.append(str(''.join([*stack])) + "                  " + Input)

            elif(b[0][0]=="r" ):
                
                s=int(b[0][1:])
                    #print(len(production_list),s)
                l=len(production_list[s])-3
                    #print(l)
                prod=production_list[s]
                l*=2
                l=len(stack)-l
                stack=stack[:l]
                s=a[int(stack[-1])][1][prod[0]]
                    #print(s,b)
                stack+=list(prod[0])
                stack.append(s)
                # Data.append(str(*stack)+"                  "+str(*Input))
                state_log.append(str(''.join([*stack]))+"                  " + Input)
            
            elif(b[0][0]=="a"):
                # Data.append("    String Accepted!")
                state_log.append("    String Accepted!")
                break
    except:
        # Data.append('    String INCORRECT for given Grammar!')
        state_log.append('    String INCORRECT for given Grammar!')
    
    return state_log

index = 0

def accept_string():

    # root = tk.Tk()
    # root.geometry("600x50")
    # root.title("String Acceptance")
    # root.config(bg='#D9D8D7')
    # paddings = {'padx': 5, 'pady': 5}


    # style = ttk.Style()
    # style.configure("TButton", font=("Calibri", 15, "bold"), borderwidth=4)
    # style.configure("TLabel", font=("Calibri", 15,"bold"), borderwidth=4)
    # style.configure("TEntry", font=("Calibri", 15,"bold"), borderwidth=4)
    # style.map("TButton", foreground=[("active", "disabled", "green")],background=[("active", "black")])
    # #style.theme_use("classic")

    # # Data.append("Enter the string to be parsed")
    # # str_Input=input()+'$'
    # str_Input=tk.StringVar()

    # ttk.Label(frame, text ="Enter the Productions :",background='#D9D8D7').pack(padx=10,pady=10,anchor=W)
    # NewInputEntry = ttk.Entry(frame,width=50,textvariable=str_Input)
    # NewInputEntry.pack(ipadx=10,ipady=10,padx=10,anchor=W)

    # table=None

    # frame = tk.Tk()
    # frame.title("TextBox Input")
    # frame.geometry('400x200')
    # # Function for getting Input
    # # from textbox and printing it??
    # # at label widget

    # def printInput():
    #     inp = inputtxt.get(1.0, "end-1c")
    #     lbl.config(text = "Provided Input: "+inp)

    # # TextBox Creation
    # inputtxt = tk.Text(frame,height = 5,width = 20)
    # inputtxt.pack()

    # # Button Creation
    # printButton = tk.Button(frame,text = "Print",command = printInput)
    # printButton.pack()

    # # Label Creation
    # lbl = tk.Label(frame, text = "")
    # lbl.pack()
    # frame.mainloop()



    # root= tk.Tk()

    # canvas1 = tk.Canvas(root, width=400, height=300, relief='raised')
    # canvas1.pack()

    # label1 = ttk.Label(root, text='Calculate the Square Root')
    # label1.config(font=('helvetica', 14))
    # canvas1.create_window(200, 25, window=label1)

    # label2 = ttk.Label(root, text='Type your Number:')
    # label2.config(font=('helvetica', 10))
    # canvas1.create_window(200, 100, window=label2)

    # entry1 = ttk.Entry(root) 
    # canvas1.create_window(200, 140, window=entry1)

    # def get_square_root():
    #     x1 = entry1.get()
        
    #     label3 = ttk.Label(root, text='The Square Root of ' + x1 + ' is:', font=('helvetica', 10))
    #     canvas1.create_window(200, 210, window=label3)
        
    #     label4 = ttk.Label(root, text=float(x1)**0.5, font=('helvetica', 10, 'bold'))
    #     canvas1.create_window(200, 230, window=label4)
        
    # button1 = ttk.Button(text='Get the Square Root', command=get_square_root, bg='brown', fg='white', font=('helvetica', 9, 'bold'))
    # canvas1.create_window(200, 180, window=button1)

    # root.mainloop()


    from tkinter import ttk

    #Create an instance of Tkinter frame
    win= tk.Tk()

    #Set the geometry of Tkinter frame
    win.geometry("650x125")
    win.title("String Acceptance")
    win.config(bg='#D9D8D7')
    paddings = {'padx': 5, 'pady': 5}

    ttk.Label(win, text ="Enter the String :",background='#D9D8D7').pack(padx=10,pady=10,anchor=W)

    #Create an Entry widget to accept User Input
    global entry
    entry = Entry(win, width= 40)
    entry.focus_set()
    entry.pack()
    # TODO: Separate input strings and pass to oracle(input) to generate [ outputs... ]
    # input_list = string_input.split(sep=';')
    # print(string_input)

    def cascade_input():
        global entry
        string_inputs = entry.get().split(sep=';')
        print(string_inputs)
        
        prophecies = [ oracle(string_input) for string_input in string_inputs ]

        global index
        index = 0

        def orate(prophecy_index:int):
            display_win = tk.Tk()

            display_win.geometry("600x500")
            display_win.title("Prophecy")
            display_win.config(bg='#D9D8D7')

            scrollbar1 = Scrollbar(root, bg="green")
            scrollbar1.pack( side = RIGHT, fill = Y )

            scrollbar2 = Scrollbar(root, bg="green")
            scrollbar2.pack( side = BOTTOM, fill = X )

            mylist = Listbox(display_win,yscrollcommand=scrollbar1.set,xscrollcommand=scrollbar2.set,background='#D9D8D7',font=("Calibri", 15,"bold"),height=100,width=0,highlightthickness=5)
            
            for state in prophecies[prophecy_index]:
                mylist.insert(END, '  ' + state)
                #ttk.Label(frame, text=i,background='#D9D8D7').pack(anchor=SW)

            mylist.pack(anchor=CENTER, fill = BOTH,padx=60,pady=10,ipadx=20,ipady=20 )
            scrollbar1.config(command=mylist.yview)
            scrollbar2.config(command=mylist.xview)

            def PreviousPage():
                global index
                if index > 0: 
                    index -= 1
                    display_win.destroy()
                    print('new index:', index)
                    orate(index)

            def NextPage():
                global index
                if index < len(prophecies) - 1: 
                    index += 1
                    display_win.destroy()
                    print('new index:', index)
                    orate(index)


            ttk.Button(display_win, text = "previous", width = 30, command=PreviousPage).place(x=10,y=460)
            ttk.Button(display_win, text = "next", width = 30, command=NextPage).place(x=400,y=460)

        orate(0)
        # label.configure(text=string)
        return 

    #Initialize a Label to display the User Input
    # label=Label(win, text="", font=("Courier 22 bold"))
    # label.pack()

    #Create a Button to validate Entry Widget
    ttk.Button(win, text= "Check String Acceptance",width= 30, command= cascade_input).pack(pady=20)

    win.mainloop()













    try:
        stack=['0']
        a=list(table.items())
        Data.append("productions    : "+str(production_list))
        Data.append('stack'+"                    "+'str_Input')
        Data.append(str(*stack)+"                  "+str(*str_Input))
        while(len(str_Input)!=0):
            b=list(a[int(stack[-1])][1][str_Input[0]])
            if(b[0][0]=="s" ):
                    #s=Input[0]+b[0][1:]
                stack.append(str_Input[0])
                stack.append(b[0][1:])
                str_Input=str_Input[1:]
                Data.append(str(*stack)+"                  "+str(*str_Input))
            elif(b[0][0]=="r" ):
                s=int(b[0][1:])
                    #print(len(production_list),s)
                l=len(production_list[s])-3
                    #print(l)
                prod=production_list[s]
                l*=2
                l=len(stack)-l
                stack=stack[:l]
                s=a[int(stack[-1])][1][prod[0]]
                    #print(s,b)
                stack+=list(prod[0])
                stack.append(s)
                Data.append(str(*stack)+"                  "+str(*str_Input))
            elif(b[0][0]=="a"):
                Data.append("    String Accepted!")
                break
    except:
        Data.append('    String INCORRECT for given Grammar!')

ttk.Button(frame, text = "Add Production", command = add_input).pack(side=LEFT,padx=10,pady=10)
ttk.Button(frame, text = "Submit Productions", command = submit_input).pack(side=LEFT,padx=10,pady=10)
ttk.Button(frame, text = "Exit", command = root.destroy).pack(side=LEFT,padx=10,pady=10)
ttk.Button(bottomframe, text = "Accept String", command = accept_string).pack(side=LEFT,padx=10,pady=10)

ttk.Label(frame, text='',background='#D9D8D7').pack(anchor=S,fill=X)


root.mainloop()

# GUI textbox for string entry
# Statewise output  
'''
Data.append("Enter the string to be parsed")
Input=input()+'$'
try:
    stack=['0']
    a=list(table.items())
    Data.append("productions    : "+str(production_list))
    Data.append('stack'+"                    "+'Input')
    Data.append(str(*stack)+"                  "+str(*Input))
    while(len(Input)!=0):
        b=list(a[int(stack[-1])][1][Input[0]])
        if(b[0][0]=="s" ):
                #s=Input[0]+b[0][1:]
            stack.append(Input[0])
            stack.append(b[0][1:])
            Input=Input[1:]
            Data.append(str(*stack)+"                  "+str(*Input))
        elif(b[0][0]=="r" ):
            s=int(b[0][1:])
                #print(len(production_list),s)
            l=len(production_list[s])-3
                #print(l)
            prod=production_list[s]
            l*=2
            l=len(stack)-l
            stack=stack[:l]
            s=a[int(stack[-1])][1][prod[0]]
                #print(s,b)
            stack+=list(prod[0])
            stack.append(s)
            Data.append(str(*stack)+"                  "+str(*Input))
        elif(b[0][0]=="a"):
            Data.append("    String Accepted!")
            break
except:
    Data.append('    String INCORRECT for given Grammar!')
'''