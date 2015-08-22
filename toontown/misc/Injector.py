from Tkinter import *
from direct.stdpy import thread
import os

def inject():
	global text
	exec (text.get(1.0, "end"), globals())

def openInjector():    
	global text

	root = Tk()
	root.resizable(False, False)
	root.geometry('700x500')
	root.title('Funny Farm Injector')
		
	frame = Frame(root)
	frame.pack(fill='y')
	text = Text(frame, width=70, height=18)
	text.pack(side='left')

	yscroll = Scrollbar(frame)
	yscroll.pack(fill='y', side='right')
	yscroll.config(command=text.yview)
	text.config(yscrollcommand=yscroll.set)
	
	injectBtn = Button(text='Inject Code', height=12, width=90, bd=3, command=inject)
	injectBtn.place(x=30, y=300)
	injectBtn.pack()

	if os.path.isfile('C:/Windows/Fonts/Minnie.ttf'):
		injectBtn['width'] = 52
		injectBtn['height'] = 11
		injectBtn['font'] = 'Minnie'

	thread.start_new_thread(root.mainloop,())