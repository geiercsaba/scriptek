import tkinter as tk
from math import sqrt


class Calculator(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        master.title("Számológép")
        self.calc_entry = tk.Entry()
        self.result = 0
        self.calc_entry.grid(row=0, column=0, columnspan=4)
        self.calc_log = tk.Text(width=20, height=10)
        self.calc_log.grid(row=1, column=0, columnspan=4)

        tk.Button(text="7", command=lambda: self.button_pushed("7")).grid(row=2, column=0)
        tk.Button(text="8", command=lambda: self.button_pushed("8")).grid(row=2, column=1)
        tk.Button(text="9", command=lambda: self.button_pushed("9")).grid(row=2, column=2)
        tk.Button(text="+", command=lambda: self.button_pushed("+")).grid(row=2, column=3)
        tk.Button(text="4", command=lambda: self.button_pushed("4")).grid(row=3, column=0)
        tk.Button(text="5", command=lambda: self.button_pushed("5")).grid(row=3, column=1)
        tk.Button(text="6", command=lambda: self.button_pushed("6")).grid(row=3, column=2)
        tk.Button(text="-", command=lambda: self.button_pushed("-")).grid(row=3, column=3)
        tk.Button(text="1", command=lambda: self.button_pushed("1")).grid(row=4, column=0)
        tk.Button(text="2", command=lambda: self.button_pushed("2")).grid(row=4, column=1)
        tk.Button(text="3", command=lambda: self.button_pushed("3")).grid(row=4, column=2)
        tk.Button(text="*", command=lambda: self.button_pushed("*")).grid(row=4, column=3)
        tk.Button(text="(", command=lambda: self.button_pushed("(")).grid(row=5, column=0)
        tk.Button(text="0", command=lambda: self.button_pushed("0")).grid(row=5, column=1)
        tk.Button(text=")", command=lambda: self.button_pushed(")")).grid(row=5, column=2)
        tk.Button(text="/", command=lambda: self.button_pushed("/")).grid(row=5, column=3)
        tk.Button(text=",", command=lambda: self.button_pushed(".")).grid(row=6, column=0)
        tk.Button(text="√", command=lambda: self.button_pushed("sqrt(")).grid(row=6, column=1)
        tk.Button(text="C", command=self.clear_entry).grid(row=6, column=2)
        tk.Button(text="AC", command=self.clear_log).grid(row=6, column=3)
        tk.Button(text="Ans", command=lambda: self.calc_entry.insert(tk.END, self.result)).grid(row=7, column=2)
        tk.Button(text="=", command=self.equals_button).grid(row=7, column=3)

    def button_pushed(self, bt):
        self.calc_entry.insert(tk.END, bt)

    def clear_entry(self):
        self.calc_entry.delete("0", tk.END)

    def clear_log(self):
        self.calc_entry.delete("0", tk.END)
        self.calc_log.delete("1.0", tk.END)

    def equals_button(self):
        try:
            self.result = eval(self.calc_entry.get())
            self.calc_log.insert(tk.END, self.calc_entry.get() + f"={self.result}\n")
            self.calc_entry.delete("0", tk.END)
        except Exception as e:
            self.calc_entry.delete(0, tk.END)
            self.calc_entry.insert(tk.END, "Error")
            self.calc_log.insert(tk.END, "Error: " + str(e) + "\n")


root = tk.Tk()
mycalculator = Calculator(root)
mycalculator.mainloop()
