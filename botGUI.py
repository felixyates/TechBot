import tkinter as tk
import tkinter.messagebox

gui = tk.Tk()
gui.title('TechBot GUI')
gui.geometry('100x100')  
gui.resizable(False, False)  

def starting():
    tkinter.messagebox.showinfo( "Starting bot", "Whoopee!! As long as we don't have any errors, this will be awesome!")

def killing():
    tkinter.messagebox.showinfo("Killing bot", "How could you do this?? :(")

tkinter.Button(gui, text='Start Bot',command=starting).pack()
tkinter.Button(gui, text='Kill Bot',command=killing).pack()

gui.mainloop()