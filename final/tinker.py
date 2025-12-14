import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import mysql.connector
from mysql.connector import Error


# Hàm lấy danh sách sinh viên
def fetch_students():
    conn = conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='lequyen5002',
        database='student_management'
    )
    if conn is None:
        return []
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM students ORDER BY StudentID")
    students = cur.fetchall()
    cur.close()
    conn.close()
    return students

# Hàm thêm sinh viên
def add_student():
    fname = entry_fname.get()
    lname = entry_lname.get()
    dob = entry_dob.get()
    gender = gender_var.get()
    major = entry_major.get()

    if not fname or not lname or not dob:
        messagebox.showwarning("Warning", "Please fill all required fields!")
        return

    try:
        datetime.strptime(dob, "%Y-%m-%d")  # Kiểm tra định dạng DOB
    except ValueError:
        messagebox.showerror("Error", "DOB must be YYYY-MM-DD")
        return

    conn = get_connection()
    cur = conn.cursor()
    sql = "INSERT INTO students (FirstName, LastName, DOB, Gender, Major, EnrollmentYear) VALUES (%s,%s,%s,%s,%s,%s)"
    cur.execute(sql, (fname, lname, dob, gender, major, 2024))
    conn.commit()
    cur.close()
    conn.close()
    messagebox.showinfo("Success", f"Student {fname} {lname} added!")
    refresh_tree()

# Hàm refresh Treeview
def refresh_tree():
    for i in tree.get_children():
        tree.delete(i)
    for student in fetch_students():
        tree.insert("", "end", values=(student['StudentID'], student['FirstName'], student['LastName'], student['DOB'], student['Gender'], student['Major']))

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Student Management System")
root.geometry("800x500")

# Form thêm sinh viên
frame_form = tk.Frame(root)
frame_form.pack(pady=10)

tk.Label(frame_form, text="First Name").grid(row=0, column=0)
entry_fname = tk.Entry(frame_form)
entry_fname.grid(row=0, column=1)

tk.Label(frame_form, text="Last Name").grid(row=0, column=2)
entry_lname = tk.Entry(frame_form)
entry_lname.grid(row=0, column=3)

tk.Label(frame_form, text="DOB (YYYY-MM-DD)").grid(row=1, column=0)
entry_dob = tk.Entry(frame_form)
entry_dob.grid(row=1, column=1)

tk.Label(frame_form, text="Gender").grid(row=1, column=2)
gender_var = tk.StringVar(value="M")
ttk.Combobox(frame_form, textvariable=gender_var, values=["M", "F", "O"]).grid(row=1, column=3)

tk.Label(frame_form, text="Major").grid(row=2, column=0)
entry_major = tk.Entry(frame_form)
entry_major.grid(row=2, column=1)

tk.Button(frame_form, text="Add Student", command=add_student).grid(row=2, column=3)

# Treeview hiển thị sinh viên
columns = ("ID", "First Name", "Last Name", "DOB", "Gender", "Major")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.pack(fill="both", expand=True, pady=20)

refresh_tree()
root.mainloop()