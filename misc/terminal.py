import tkinter as tk

'''
Instantiation: 

root = tk.Tk()

entered_text = tk.StringVar()

term = Terminal(root, entered_text)
'''

class Terminal():
    def __init__(self, root, input_buffer_tk) -> None:
        self.root = root
        self.input_buffer_tk = input_buffer_tk
        self.input_buffer = ""
        self.text_widget = tk.Text(root, borderwidth=0, highlightthickness=0)
        self.text_widget.pack(pady=0)
        self.text_widget.config(state=tk.DISABLED)
        self.text_widget.tag_config("red", foreground="red")
        self.text_widget.tag_config("yellow", foreground="red")
        self.input_field = tk.Text(root, height=3, borderwidth=0, highlightthickness=0)
        self.input_field.pack(pady=0)
        self.input_field.bind('<Return>', self.on_enter_key)
        self.input_field.pack_forget()

    def toggle_input_field(self):
        if self.input_field.winfo_ismapped():
            self.input_field.pack_forget()
        else:
            self.input_field.pack()

    def on_enter_key(self, event):
        self.input_buffer_tk.set(self.input_field.get("1.0", 'end-1c'))
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert("end", self.input_buffer_tk.get() + "\n")
        self.input_buffer = self.input_buffer_tk.get()
        self.text_widget.config(state=tk.DISABLED)
        self.input_field.delete("1.0", tk.END)
        self.input_field.pack_forget()
        self.input_field.delete("1.0", tk.END)

        return "break"

    def get_input(self) -> str:
        self.toggle_input_field()
        self.root.wait_variable(self.input_buffer_tk)

        ret_val = self.input_buffer
        self.input_buffer = ""

        return ret_val
    
    def print(self, str):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert("end", str)
        self.text_widget.config(state=tk.DISABLED)

    def print_yellow(self, str):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert("end", str, "blue")
        self.text_widget.config(state=tk.DISABLED)

    def print_yellow(self, str):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert("end", str, "red")
        self.text_widget.config(state=tk.DISABLED)