import requests
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter.messagebox as messagebox

API_URL = "http://ajax1.lmsoft.cz/procedure.php"
USERNAME = "coffe"
PASSWORD = "kafe"

def send_request(endpoint, params):
    response = requests.get(f"{API_URL}?cmd={endpoint}", params=params, auth=(USERNAME, PASSWORD))
    response.raise_for_status()
    return response.json()

def merge_data(all_data):
    result = {}
    for data in all_data:
        for entry in data:
            drink = entry[0]
            count = entry[1]
            try:
                count = int(count)  # Pokus o převod na int
            except ValueError:
                count = 0  # Pokud není platné číslo, nastavte na 0

            if drink not in result:
                result[drink] = 0
            result[drink] += count
    return result

def load_table_data(start_month, end_month):
    all_data = []
    try:
        if start_month == end_month:
            data = send_request("getSummaryOfDrinks", {'month': start_month})
            all_data.append(data)
        else:
            for month in range(start_month, end_month + 1):
                data = send_request("getSummaryOfDrinks", {'month': month})
                all_data.append(data)

        merged_data = merge_data(all_data)
        update_table(merged_data)
    except Exception as e:
        messagebox.showerror("Error", f"Nastala chyba: {e}")  # Opraveno

def update_table(data):
    for row in tree.get_children():
        tree.delete(row)
    for drink, count in data.items():
        tree.insert("", "end", values=(drink, count))

def filter_data():
    start_month = int(start_month_combobox.get())
    end_month = int(end_month_combobox.get())

    if start_month > end_month:
        messagebox.showwarning("Warning", "Začátek měsíce nemůže být pozdější než konec měsíce.")
        return

    load_table_data(start_month, end_month)

root = ttk.Window(themename="flatly")
root.title("Měsíční přehled")

frame = ttk.Frame(root)
frame.pack(pady=20)

start_month_combobox = ttk.Combobox(frame, values=list(range(1, 13)), state="readonly", width=15)
start_month_combobox.set("Vyberte měsíc od")
start_month_combobox.grid(row=0, column=0, padx=10)

end_month_combobox = ttk.Combobox(frame, values=list(range(1, 13)), state="readonly", width=15)
end_month_combobox.set("Vyberte měsíc do")
end_month_combobox.grid(row=0, column=1, padx=10)

def update_end_month_options(*args):
    start_month = start_month_combobox.get()

    if start_month.isdigit():  # Ověřujeme, že je to číslo
        start_month = int(start_month)

        end_month_combobox['values'] = list(range(start_month, 13))

        current_end_month = end_month_combobox.get()
        if current_end_month and current_end_month != "Vyberte měsíc do":
            if current_end_month.isdigit() and int(current_end_month) < start_month:
                end_month_combobox.current(0)
    else:
        end_month_combobox['values'] = list(range(1, 13))
        end_month_combobox.set("Vyberte měsíc do")

start_month_combobox.bind("<<ComboboxSelected>>", update_end_month_options)

filter_button = ttk.Button(frame, text="Zobrazit přehled", bootstyle=SUCCESS, command=filter_data)
filter_button.grid(row=0, column=2, padx=10)

columns = ("Nápoj", "Počet")
tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
tree.heading("Nápoj", text="Nápoj")
tree.heading("Počet", text="Počet")
tree.column("Nápoj", anchor=CENTER)
tree.column("Počet", anchor=CENTER)
tree.pack(pady=20)

style = ttk.Style()
style.configure("Treeview.Heading", font=('Helvetica', 12, 'bold'), background="#007BFF", foreground="white")
style.configure("Treeview", rowheight=30, font=('Helvetica', 11))
style.map("Treeview", background=[('selected', '#007BFF')])

root.mainloop()
