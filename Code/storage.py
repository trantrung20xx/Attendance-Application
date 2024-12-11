import tkinter as tk

root = tk.Tk()

# Label với các kiểu relief khác nhau
label_flat = tk.Label(root, text="Flat", relief="flat", width=20, height=2)
label_flat.pack(padx=10, pady=5)

label_raised = tk.Label(root, text="Raised", relief="raised", width=20, height=2)
label_raised.pack(padx=10, pady=5)

label_sunken = tk.Label(root, text="Sunken", relief="sunken", width=20, height=2)
label_sunken.pack(padx=10, pady=5)

label_solid = tk.Label(root, text="Solid", relief="solid", width=20, height=2)
label_solid.pack(padx=10, pady=5)

label_groove = tk.Label(root, text="Groove", relief="groove", width=20, height=2)
label_groove.pack(padx=10, pady=5)

label_ridge = tk.Label(root, text="Ridge", relief="ridge", width=20, height=2)
label_ridge.pack(padx=10, pady=5)

root.mainloop()
