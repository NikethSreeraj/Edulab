import tkinter as tk


def main():
    root = tk.Tk()
    root.title("Edulab")
    root.geometry("900x600")

    title = tk.Label(
        root,
        text="Edulab",
        font=("Segoe UI", 28, "bold")
    )
    title.pack(pady=40)

    subtitle = tk.Label(
        root,
        text="Educational tools, simulations and learning",
        font=("Segoe UI", 13)
    )
    subtitle.pack()

    root.mainloop()


if __name__ == "__main__":
    main()