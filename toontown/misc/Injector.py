from tkinter import *
import threading
import os

class Injector(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def inject(self):
        global text
        exec (text.get(1.0, "end"), globals())

    def openInjector(self):
        global text
        self.root.resizable(False, False)
        self.root.geometry('700x500')
        self.root.title('Funny Farm Injector')

        frame = Frame(self.root)
        frame.pack(fill='y')
        text = Text(frame, width=70, height=18)
        text.pack(side='left')

        yscroll = Scrollbar(frame)
        yscroll.pack(fill='y', side='right')
        yscroll.config(command=text.yview)
        text.config(yscrollcommand=yscroll.set)

        injectBtn = Button(text='Inject Code', height=12, width=90, bd=3, command=self.inject)
        injectBtn.place(x=30, y=300)
        injectBtn.pack()

        if os.path.isfile('C:/Windows/Fonts/Minnie.ttf'):
            injectBtn['width'] = 52
            injectBtn['height'] = 11
            injectBtn['font'] = 'Minnie'

    def run(self):
        self.root = Tk()
        self.openInjector()
        self.root.mainloop()
