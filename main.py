# (BIT502), Luis Fernando Andreo Baronceli, student number: 5024576, and assessment 3.
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msgbox
import sqlite3

class MembershipManager:
    def __init__(self, root):
        self.root = root
        self.root.geometry("650x300")
        self.root.title("Membership Manager")
        self.db_conn = sqlite3.connect('members.db')
        self.cursor = self.db_conn.cursor()
        self.create_table()
        self.create_menu()
        self.current_page = None

    def reset_main_window(self):
        # Destroy the current page if it exists
        if self.current_page is not None:
            self.current_page.destroy()
        if hasattr(self, 'details_frame'):
            self.details_frame.destroy()
        
    def create_main_page(self):
      self.reset_main_window()  # Reset the main window
      self.current_page = ttk.Frame(self.root)
      self.current_page.grid(row=0, column=0, sticky="nsew")

      label_welcome = ttk.Label(self.current_page, text="Welcome to City Gym", font=("Helvetica", 20))
      label_welcome.grid(row=0, column=0, padx=20, pady=20)

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Memberships (
                                MemberID INTEGER PRIMARY KEY NOT NULL,
                                First_Name TEXT NOT NULL,
                                Last_Name TEXT NOT NULL,
                                Address TEXT NOT NULL,
                                Mobile TEXT NOT NULL,
                                Membership_Type TEXT NOT NULL,
                                Membership_Duration TEXT NOT NULL,
                                Direct_Debit BOOLEAN NOT NULL,
                                Extra_1 BOOLEAN NOT NULL,
                                Extra_2 BOOLEAN NOT NULL,
                                Extra_3 BOOLEAN NOT NULL,
                                Extra_4 BOOLEAN NOT NULL,
                                Payment_Frequency TEXT NOT NULL
                                )''')
        self.db_conn.commit()

    def search_form(self):
      self.create_search_frame()
      self.load_members()
      self.create_member_details_frame()
        
    def show_statistics(self):
      # Total number of members
      self.cursor.execute("SELECT COUNT(MemberID) FROM Memberships")
      total_members = self.cursor.fetchone()[0]

      # Total members for each membership type
      self.cursor.execute("SELECT Membership_Type, COUNT(MemberID) FROM Memberships GROUP BY Membership_Type")
      membership_types = self.cursor.fetchall()

      # Total members that have selected each extra
      extras = ['Extra_1', 'Extra_2', 'Extra_3', 'Extra_4']
      total_extras = {}
      for extra in extras:
          self.cursor.execute(f"SELECT COUNT(MemberID) FROM Memberships WHERE {extra} = 1")
          total_extras[extra] = self.cursor.fetchone()[0]

      # Total members that have selected direct debit
      self.cursor.execute("SELECT COUNT(MemberID) FROM Memberships WHERE Direct_Debit = 1")
      total_direct_debit = self.cursor.fetchone()[0]

      # Display statistics on the root window
      stats_window = tk.Toplevel(self.root)
      stats_window.title("Statistics")

      # Total number of members
      label_total_members = ttk.Label(stats_window, text=f"Total Members: {total_members}")
      label_total_members.pack()

      # Total members for each membership type
      label_membership_types = ttk.Label(stats_window, text="Total Members for Each Membership Type:")
      label_membership_types.pack()
      for membership_type, count in membership_types:
          label = ttk.Label(stats_window, text=f"{membership_type}: {count}")
          label.pack()

      # Total members that have selected each extra
      label_total_extras = ttk.Label(stats_window, text="Total Members for Each Extra:")
      label_total_extras.pack()
      for extra, count in total_extras.items():
          label = ttk.Label(stats_window, text=f"{extra}: {count}")
          label.pack()

      # Total members that have selected direct debit
      label_total_direct_debit = ttk.Label(stats_window, text=f"Total Members with Direct Debit: {total_direct_debit}")
      label_total_direct_debit.pack()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Main Page", command=self.create_main_page)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        member_menu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Membership", menu=member_menu)
        member_menu.add_command(label="View Members", command=self.view_members)
        member_menu.add_command(label="Add Members", command=self.add_member)
        member_menu.add_command(label="Search & Edit", command=self.search_form)

        stats_menu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Statistics", menu=stats_menu)
        stats_menu.add_command(label="Show Statistics", command=self.show_statistics)

        help_menu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.about)

    def create_search_frame(self):

      self.search_frame = ttk.LabelFrame(self.root, text="Member Search:")
      self.search_frame.grid(column=0, row=0, padx=10, pady=10)

      # Label for name search entry
      label_name = ttk.Label(self.search_frame, text="Name:")
      label_name.grid(row=0, column=0, padx=5, pady=5, sticky="w")

      self.search_var_name = tk.StringVar()
      self.search_entry_name = ttk.Entry(self.search_frame, textvariable=self.search_var_name, width=30)
      self.search_entry_name.grid(row=0, column=1, padx=5, pady=5)
      self.search_var_name.trace_add("write", self.search_members)

      # Label for membership type search entry
      label_membership = ttk.Label(self.search_frame, text="Membership Type:")
      label_membership.grid(row=1, column=0, padx=5, pady=5, sticky="w")

      self.search_var_membership = tk.StringVar()
      self.search_entry_membership = ttk.Entry(self.search_frame, textvariable=self.search_var_membership, width=30)
      self.search_entry_membership.grid(row=1, column=1, padx=5, pady=5)
      self.search_var_membership.trace_add("write", self.search_members)

      self.member_listbox = tk.Listbox(self.search_frame, height=10, width=30)
      self.member_listbox.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
      self.member_listbox.bind("<<ListboxSelect>>", self.show_selected_member)

    def create_member_details_frame(self):
        self.details_frame = ttk.LabelFrame(self.root, text="Member Details")
        self.details_frame.grid(column=1, row=0, padx=10, pady=10, sticky="news")

        self.member_info_labels = {}
        labels = ["Name", "Address", "Mobile", "Membership", "Duration"]
        for i, label_text in enumerate(labels):
            label = ttk.Label(self.details_frame, text=label_text + ":")
            label.grid(row=i, column=0, padx=5, pady=5, sticky="w")
            info_label = ttk.Label(self.details_frame, text="")
            info_label.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            self.member_info_labels[label_text] = info_label
        button_edit = ttk.Button(self.details_frame, text="Edit", command=self.edit_member)
        button_edit.grid()

    def load_members(self):
        self.member_listbox.delete(0, tk.END)
        self.cursor.execute("SELECT First_Name, Last_Name FROM Memberships")
        members = self.cursor.fetchall()
        for member in members:
            full_name = f"{member[0]} {member[1]}"
            self.member_listbox.insert(tk.END, full_name)

    def search_members(self, *args):
      query_name = f"%{self.search_var_name.get()}%"
      query_membership = f"%{self.search_var_membership.get()}%"
      self.cursor.execute("SELECT First_Name, Last_Name FROM Memberships WHERE (First_Name LIKE ? OR Last_Name LIKE ?) AND Membership_Type LIKE ?",
                          (query_name, query_name, query_membership))
      members = self.cursor.fetchall()
      self.member_listbox.delete(0, tk.END)
      if not members:  # If no members found
          msgbox.showinfo("No Results", "No members found.")
      else:
          for member in members:
              full_name = f"{member[0]} {member[1]}"
              self.member_listbox.insert(tk.END, full_name)

    def show_selected_member(self, event):
        try:
            selected_index = self.member_listbox.curselection()[0]
            self.cursor.execute("SELECT * FROM Memberships")
            members = self.cursor.fetchall()
            member = members[selected_index]
            member_info = {
                "Name": f"{member[1]} {member[2]}",
                "Address": member[3],
                "Mobile": member[4],
                "Membership": member[5],
                "Duration": member[6]
            }
            for key, value in member_info.items():
                self.member_info_labels[key].config(text=value)
        except IndexError:
            pass

    def edit_member(self):
      selected_index = self.member_listbox.curselection()
      if selected_index:
          selected_index = selected_index[0]
          self.cursor.execute("SELECT * FROM Memberships")
          members = self.cursor.fetchall()
          selected_member = members[selected_index]

          # Create a new window for editing member details
          edit_window = tk.Toplevel(self.root)
          edit_window.title("Edit Member")

          # Create labels and entry fields for each member detail
          labels = ["First Name", "Last Name", "Address", "Mobile", "Membership Type",
                    "Membership Duration", "Direct Debit", "24/7 Access", "Personal Training",
                    "Diet Consultation", "Online Video Access", "Payment Frequency"]

          entry_fields = {}
          for i, label_text in enumerate(labels):
              label = ttk.Label(edit_window, text=label_text + ":")
              label.grid(row=i, column=0, padx=5, pady=5, sticky="w")

              entry_var = tk.StringVar()
              entry_var.set(selected_member[i + 1])  # Skip MemberID
              entry_field = ttk.Entry(edit_window, textvariable=entry_var, width=30)
              entry_field.grid(row=i, column=1, padx=5, pady=5, sticky="w")

              entry_fields[label_text] = entry_var

          # Update member details in the database upon clicking the "Save" button
          def save_changes():
              updated_values = [entry_fields[label].get() for label in labels]
              self.cursor.execute('''UPDATE Memberships SET
                                  First_Name=?, Last_Name=?, Address=?, Mobile=?,
                                  Membership_Type=?, Membership_Duration=?, Direct_Debit=?,
                                  Extra_1=?, Extra_2=?, Extra_3=?, Extra_4=?, Payment_Frequency=?
                                  WHERE MemberID=?''',
                                  (*updated_values, selected_member[0]))
              self.db_conn.commit()
              msgbox.showinfo("Success", "Member details updated successfully.")
              self.load_members()
              edit_window.destroy()

          # Create a button to save changes
          save_button = ttk.Button(edit_window, text="Save Changes", command=save_changes)
          save_button.grid(row=len(labels) + 1, column=0, columnspan=2, padx=5, pady=10)
      else:
          msgbox.showerror("Error", "Please select a member to edit.")

    def view_members(self):
        # Create a new window for viewing members
        view_window = tk.Toplevel(root)
        view_window.title("View Members")

        # Create a Treeview widget
        tree = ttk.Treeview(view_window, columns=("First Name", "Last Name", "Address", "Mobile", "Membership Type", "Membership Duration"))

        # Define column headings
        tree.heading("#0", text="ID")
        tree.heading("#1", text="First Name")
        tree.heading("#2", text="Last Name")
        tree.heading("#3", text="Address")
        tree.heading("#4", text="Mobile")
        tree.heading("#5", text="Membership Type")
        tree.heading("#6", text="Membership Duration")

        # Fetch members from the database
        self.cursor.execute("SELECT * FROM Memberships")
        members = self.cursor.fetchall()

        # Insert members into the treeview
        for member in members:
            tree.insert("", "end", values=member)

        # Pack the treeview widget
        tree.pack(expand=True, fill="both")

    def add_member(self):
        basic = "Basic"
        regular = "Regular"
        premium = "Premium"
        three_months = "3 months"
        twelve_months = "12 months"
        twenty_four_months = "24 months"
        weekly = "Weekly"
        monthly = "Monthly"
        optional_1 = "24/7 Access"
        optional_2 = "Personal training"
        optional_3 = "Diet consultation"
        optional_4 = "Online video access"

        add_member_window = tk.Toplevel(self.root)
        add_member_window.title("Add New Member")

        member_type = tk.StringVar(add_member_window, basic)
        member_duration = tk.StringVar(add_member_window, three_months)
        direct_debit = tk.BooleanVar(add_member_window, False)
        extra1 = tk.BooleanVar(add_member_window, False)
        extra2 = tk.BooleanVar(add_member_window, False)
        extra3 = tk.BooleanVar(add_member_window, False)
        extra4 = tk.BooleanVar(add_member_window, False)
        payment_frequency = tk.StringVar(add_member_window, weekly)

        def reset_fields():
            entry_first_name.delete(0, tk.END)
            entry_last_name.delete(0, tk.END)
            entry_address.delete(0, tk.END)
            entry_mobile.delete(0, tk.END)
            member_type.set(basic)
            member_duration.set(three_months)
            direct_debit.set(False)
            extra1.set(False)
            extra2.set(False)
            extra3.set(False)
            extra4.set(False)
            payment_frequency.set(weekly)
            label_total_cost_base.config(text="--")
            label_total_cost_extras.config(text="--")
            label_total_cost_discount.config(text="--")
            label_total_cost_total.config(text="--")
            label_total_cost_payment.config(text="--") 

        def calculate():
            # Membership costs
            membership_cost = 0
            selected_type = member_type.get()
            if selected_type == basic:
                membership_cost += 10
            elif selected_type == regular:
                membership_cost += 15
            elif selected_type == premium:
                membership_cost += 20

            # Duration discount
            selected_duration = member_duration.get()
            if selected_duration == twelve_months:
                membership_cost -= 2
            elif selected_duration == twenty_four_months:
                membership_cost -= 5

            # Extras
            extra_cost = 0
            if extra1.get():
                extra_cost += 1
            if extra2.get():
                extra_cost += 20
            if extra3.get():
                extra_cost += 20
            if extra4.get():
                extra_cost += 2

            # Direct debit discount
            discount = 0
            if direct_debit.get():
                discount -= (membership_cost + extra_cost) * 0.01

            # Total cost
            total_cost = membership_cost + extra_cost + discount

            # Update labels
            label_total_cost_base.config(text=f"${membership_cost:.2f}")
            label_total_cost_extras.config(text=f"{extra_cost:.2f}") 
            label_total_cost_discount.config(text=f"{discount:.2f}")
            label_total_cost_total.config(text=f"${total_cost:.2f}")

               # Payment Frequency
            selected_frequency = payment_frequency.get()
            if selected_frequency == monthly:
                total_cost = 2 + membership_cost + extra_cost + discount
                monthly_cost = total_cost * 4
                label_total_cost_payment.config(text=f"${monthly_cost:.2f}")
            else:
                total_cost = membership_cost + extra_cost + discount
                label_total_cost_payment.config(text=f"${total_cost:.2f}")


        def save_member():
            if not all([entry_first_name.get(), entry_last_name.get(), entry_address.get(), entry_mobile.get()]):
                # Display an error message or handle it as needed
                msgbox.showerror("Error", "Please fill in all required fields.")
                return

            # Validate first name and last name don't contain digits
            first_name = entry_first_name.get()
            last_name = entry_last_name.get()

            if not first_name.isalpha():
                msgbox.showerror("Error", "First name must not contain digits.")
                return

            if not last_name.isalpha():
                msgbox.showerror("Error", "Last name must not contain digits.")
                return

            # Validate mobile phone is a digit
            mobile = entry_mobile.get()
            if not mobile.isdigit():
                msgbox.showerror("Error", "Mobile phone must contain only digits.")
                return
            
            first_name = entry_first_name.get()
            last_name = entry_last_name.get()
            address = entry_address.get()
            mobile = entry_mobile.get()
            membership_type = member_type.get()
            membership_duration = member_duration.get()
            direct_debit_value = direct_debit.get()
            extra1_value = extra1.get()
            extra2_value = extra2.get()
            extra3_value = extra3.get()
            extra4_value = extra4.get()
            payment_frequency_value = payment_frequency.get()

            self.cursor.execute('''INSERT INTO Memberships (First_Name, Last_Name, Address, Mobile, Membership_Type, 
                                Membership_Duration, Direct_Debit, Extra_1, Extra_2, Extra_3, Extra_4, Payment_Frequency)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                (first_name, last_name, address, mobile, membership_type, membership_duration,
                                direct_debit_value, extra1_value, extra2_value, extra3_value, extra4_value,
                                payment_frequency_value))
            self.db_conn.commit()

            msgbox.showinfo("Success", "New member added successfully.")
            self.load_members()
            add_member_window.destroy()

        label_first_name = ttk.Label(add_member_window, text="First Name:")
        label_last_name = ttk.Label(add_member_window, text="Last Name:")
        label_address = ttk.Label(add_member_window, text="Address:")
        label_mobile = ttk.Label(add_member_window, text="Mobile:")
        label_membership_type = ttk.Label(add_member_window, text="Membership Plan")
        label_membership_duration = ttk.Label(add_member_window, text="Membership Duration")
        label_direct_debit = ttk.Label(add_member_window, text="Direct Debit")
        label_payment_frequency = ttk.Label(add_member_window, text="Payment Frequency")
        label_optional_extras = ttk.Label(add_member_window, text="Optional Extras:")
        label_total_header = ttk.Label(add_member_window, text="Totals")
        label_total_base = ttk.Label(add_member_window, text="Membership:")
        label_total_extras = ttk.Label(add_member_window, text="Extras:")
        label_total_discount = ttk.Label(add_member_window, text="Discount:")
        label_total_total = ttk.Label(add_member_window, text="Total:")
        label_total_payment = ttk.Label(add_member_window, text="Regular payment:")
        label_total_cost_base = ttk.Label(add_member_window, text = "--")
        label_total_cost_extras = ttk.Label(add_member_window, text = "--")
        label_total_cost_discount = ttk.Label(add_member_window, text = "--")
        label_total_cost_total = ttk.Label(add_member_window, text = "--")
        label_total_cost_payment = ttk.Label(add_member_window, text = "--")

        entry_first_name = ttk.Entry(add_member_window)
        entry_last_name = ttk.Entry(add_member_window)
        entry_address = ttk.Entry(add_member_window)
        entry_mobile = ttk.Entry(add_member_window)

        radio_member_1 = ttk.Radiobutton(add_member_window, text=basic, variable=member_type, value=basic)
        radio_member_2 = ttk.Radiobutton(add_member_window, text=regular, variable=member_type, value=regular)
        radio_member_3 = ttk.Radiobutton(add_member_window, text=premium, variable=member_type, value=premium)
        radio_duration_1 = ttk.Radiobutton(add_member_window, text=three_months, variable=member_duration, value=three_months)
        radio_duration_2 = ttk.Radiobutton(add_member_window, text=twelve_months, variable=member_duration, value=twelve_months)
        radio_duration_3 = ttk.Radiobutton(add_member_window, text=twenty_four_months, variable=member_duration, value=twenty_four_months)
        radio_payment_1 = ttk.Radiobutton(add_member_window, text=weekly, variable=payment_frequency, value=weekly)
        radio_payment_2 = ttk.Radiobutton(add_member_window, text=monthly, variable=payment_frequency, value=monthly)

        checkbutton_direct_debit = ttk.Checkbutton(add_member_window, text="", variable=direct_debit, onvalue=True, offvalue=False)
        checkbutton_extra1 = ttk.Checkbutton(add_member_window, text=optional_1, variable=extra1, onvalue=True, offvalue=False)
        checkbutton_extra2 = ttk.Checkbutton(add_member_window, text=optional_2, variable=extra2, onvalue=True, offvalue=False)
        checkbutton_extra3 = ttk.Checkbutton(add_member_window, text=optional_3, variable=extra3, onvalue=True, offvalue=False)
        checkbutton_extra4 = ttk.Checkbutton(add_member_window, text=optional_4, variable=extra4, onvalue=True, offvalue=False)

        button_reset = ttk.Button(add_member_window, text="Reset", command=reset_fields)
        button_calculate = ttk.Button(add_member_window, text="Calculate", command=calculate)
        button_cancel = ttk.Button(add_member_window, text="Cancel", command=add_member_window.destroy)
        button_submit = ttk.Button(add_member_window, text="Submit", command=save_member)

        label_first_name.grid(row=0, column=0, sticky="w")
        label_last_name.grid(row=1, column=0, sticky="w")
        label_address.grid(row=2, column=0, sticky="w")
        label_mobile.grid(row=3, column=0, sticky="w")
        label_membership_type.grid(row=4, column=0, sticky="w")
        label_membership_duration.grid(row=7, column=0, sticky="w")
        label_direct_debit.grid(row=10, column=0, sticky="w")
        label_payment_frequency.grid(row=16, column=0, sticky="w")
        label_total_cost_base.grid(row = 19, column = 1, sticky = "w")
        label_total_cost_extras.grid(row = 20, column = 1, sticky = "w")
        label_total_cost_discount.grid(row = 21, column = 1, sticky = "w")
        label_total_cost_total.grid(row = 22, column = 1, sticky = "w")
        label_total_cost_payment.grid(row = 23, column = 1, sticky = "w")
        entry_first_name.grid(row=0, column=1, sticky="w")
        entry_last_name.grid(row=1, column=1, sticky="w")
        entry_address.grid(row=2, column=1, sticky="w")
        entry_mobile.grid(row=3, column=1, sticky="w")
        radio_member_1.grid(row=4, column=1, sticky="w")
        radio_member_2.grid(row=5, column=1, sticky="w")
        radio_member_3.grid(row=6, column=1, sticky="w")
        radio_duration_1.grid(row=7, column=1, sticky="w")
        radio_duration_2.grid(row=8, column=1, sticky="w")
        radio_duration_3.grid(row=9, column=1, sticky="w")
        checkbutton_direct_debit.grid(row=10, column=1, sticky="w")
        label_optional_extras.grid(row=11, column=0, sticky="w")
        checkbutton_extra1.grid(row=11, column=1, sticky="w")
        checkbutton_extra2.grid(row=12, column=1, sticky="w")
        checkbutton_extra3.grid(row=13, column=1, sticky="w")
        checkbutton_extra4.grid(row=14, column=1, sticky="w")
        radio_payment_1.grid(row=16, column=1, sticky="w")
        radio_payment_2.grid(row=17, column=1, sticky="w")
        label_total_header.grid(row=18, column=0, sticky="w")
        label_total_base.grid(row=19, column=0, sticky="w")
        label_total_extras.grid(row=20, column=0, sticky="w")
        label_total_discount.grid(row=21, column=0, sticky="w")
        label_total_total.grid(row=22, column=0, sticky="w")
        label_total_payment.grid(row=23, column=0, sticky="w")
        button_reset.grid(row=25, column=0, pady=5)
        button_calculate.grid(row=25, column=1, pady=5)
        button_cancel.grid(row=25, column=2, pady=5)
        button_submit.grid(row=25, column=3, pady=5)

    def about(self):
        msgbox.showinfo("About", "Membership Manager\nVersion 1.0")

if __name__ == "__main__":
    root = tk.Tk()
    app = MembershipManager(root)
    app.create_main_page()
    root.mainloop()
