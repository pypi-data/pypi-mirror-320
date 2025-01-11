#1 make a simple calculator

command1 = input("Enter command---> ")
if command1 == "/calc":
        calc1 = float (input("Please enter the first number: "))
        calc2 = float (input("Please enter the second number: "))
        calc3 = input("What action do you want to do? (+,-,/,*): ")
        if calc3 == "+":
            answer1 = (calc1 + calc2)
            print(str(answer1))
            print ("It's decided!")
            
        if calc3 == "-":
            answer1 = (calc1 - calc2)
            print(str(answer1))
            print ("It's decided!")
                
        if calc3 == "/":
            answer1 = (calc1 / calc2)
            print(str(answer1))
            print ("It's decided!")

        if calc3 == "*":
            answer1 = (calc1 * calc2)
            print(str(answer1))
            print ("It's decided!")

#2 make a snake game
from tkinter import *
from random import randint

class Game:

    def __init__(self, canvas):
        self.canvas = canvas
        self.snake_coords = [[14, 14]]
        self.apple_coords = [randint(0, 29) for i in range(2)]
        self.vector = {"Up":(0,-1), "Down":(0, 1), "Left": (-1,0), "Right": (1, 0)}
        self.direction = self.vector["Right"]
        self.canvas.focus_set()
        self.canvas.bind("<KeyPress>", self.set_direction)
        self.GAME()

    def set_apple(self):
        self.apple_coords = [randint(0, 29) for i in range(2)]

        if self.apple_coords in self.snake_coords:
            self.set_apple()

    def set_direction(self, event):

        if event.keysym in self.vector:
            self.direction = self.vector[event.keysym]

    def draw(self):
        self.canvas.delete(ALL)
        x_apple, y_apple = self.apple_coords
        self.canvas.create_rectangle(x_apple*10, y_apple*10, (x_apple+1)*10, (y_apple+1)*10, fill="red", width=0)
        for x, y in self.snake_coords:
            self.canvas.create_rectangle(x*10, y*10, (x+1)*10, (y+1)*10, fill="green", width=0)
    @staticmethod
    def coord_check(coord):
        return 0 if coord > 29 else 29 if coord < 0 else coord
           
    def GAME(self):
        self.draw()
        x,y = self.snake_coords[0]
        x += self.direction[0]; y += self.direction[1]
        x = self.coord_check(x)
        y = self.coord_check(y)
        if x == self.apple_coords[0] and y == self.apple_coords[1]:
            self.set_apple()
        elif [x, y] in self.snake_coords:
            self.snake_coords = []
        else:
            self.snake_coords.pop()
        self.snake_coords.insert(0, [x,y])
        self.canvas.after(100, self.GAME)
        
        
root = Tk()
canvas = Canvas(root, width=300, height=300, bg="black")
canvas.pack()
game = Game(canvas)
root.mainloop()
#3 and simple notebook!
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog


def chenge_theme(theme):
    text_fild['bg'] = view_colors[theme]['text_bg']
    text_fild['fg'] = view_colors[theme]['text_fg']
    text_fild['insertbackground'] = view_colors[theme]['cursor']
    text_fild['selectbackground'] = view_colors[theme]['select_bg']


def chenge_fonts(fontss):
    text_fild['font'] = fonts[fontss]['font']


def notepad_exit():
    answer = messagebox.askokcancel('Exit', 'You sure?')
    if answer:
        root.destroy()


def open_file():
    file_path = filedialog.askopenfilename(title='Choose', filetypes=(('Text vtv (*.vtv)', '*.vtv'), ('All files', '*.*')))
    if file_path:
        text_fild.delete('1.0', END)
        text_fild.insert('1.0', open(file_path, encoding='utf-8').read())


def save_file():
    file_path = filedialog.asksaveasfilename(filetypes=(('Text vtv (*.vtv)', '*.vtv'), ('All files', '*.*')))
    f = open(file_path, 'w', encoding='utf-8')
    text = text_fild.get('1.0', END)
    f.write(text)
    f.close()


root = Tk()
root.title('VTV Notebook')
root.geometry('600x700')


main_menu = Menu(root)


file_menu = Menu(main_menu, tearoff=0)
file_menu.add_command(label='Open', command=open_file)
file_menu.add_command(label='Save', command=save_file)
file_menu.add_separator()
file_menu.add_command(label='Close', command=notepad_exit)
root.config(menu=file_menu)


view_menu = Menu(main_menu, tearoff=0)
view_menu_sub = Menu(view_menu, tearoff=0)
font_menu_sub = Menu(view_menu, tearoff=0)
view_menu_sub.add_command(label='Dark', command=lambda: chenge_theme('dark'))
view_menu_sub.add_command(label='Light', command=lambda: chenge_theme('light'))
view_menu.add_cascade(label='Theme', menu=view_menu_sub)

font_menu_sub.add_command(label='Arial', command=lambda: chenge_fonts('Arial'))
font_menu_sub.add_command(label='Comic Sans MS', command=lambda: chenge_fonts('CSMS'))
font_menu_sub.add_command(label='Times New Roman', command=lambda: chenge_fonts('TNR'))
view_menu.add_cascade(label='Font...', menu=font_menu_sub)
root.config(menu=view_menu)


main_menu.add_cascade(label='File', menu=file_menu)
main_menu.add_cascade(label='View', menu=view_menu)
root.config(menu=main_menu)

f_text = Frame(root)
f_text.pack(fill=BOTH, expand=1)

view_colors = {
    'dark': {
        'text_bg': 'black', 'text_fg': 'lime', 'cursor': 'brown', 'select_bg': '#8D917A'
    },
    'light': {
        'text_bg': 'white', 'text_fg': 'black', 'cursor': '#A5A5A5', 'select_bg': '#FAEEDD'
    }
}

fonts = {
    'Arial': {
        'font':'Arial 14 bold'
    },
    'CSMS': {
        'font': ('Comic Sans MS', 14, 'bold')
    },
    'TNR': {
        'font': ('Times New Roman', 14, 'bold')
    }
}

text_fild = Text(f_text,
                 bg='black',
                 fg='lime',
                 padx=10,
                 pady=10,
                 wrap=WORD,
                 insertbackground='brown',
                 selectbackground='#8D917A',
                 spacing3=10,
                 width=30,
                 font='Arial 14 bold'
                 )
text_fild.pack(expand=1, fill=BOTH, side=LEFT)

scroll = Scrollbar(f_text, command=text_fild.yview)
scroll.pack(side=LEFT, fill=Y)
text_fild.config(yscrollcommand=scroll.set)

root.mainloop()