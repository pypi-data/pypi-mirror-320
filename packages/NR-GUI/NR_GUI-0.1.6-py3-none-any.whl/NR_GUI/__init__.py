import tkinter as tk
import os
import gdown
import sys
ICON_SELECTED = False



root = tk.Tk()



def ChangeIcon(PNG_LOCATION):
    global ICON_SELECTED
    try:
        icon = tk.PhotoImage(file=f"{PNG_LOCATION}")
        root.iconphoto(True, icon)
        ICON_SELECTED = True

    except:
        print("There is no png found")
        os.system('pause')
        sys.exit()
    
def ShutDown():
    sys.exit()

def Button(Title, Command, LocationX: float, LocationY: float, ScaleX: float, ScaleY: float):
    Title = tk.Button(root, text=(f"{Title}"), command=Command)
    Title.place(x=LocationX, y=LocationY, width=ScaleX, height=ScaleY)



def Text(Title, LocationX: float, LocationY: float, ScaleX: float, ScaleY: float):
    
    Title = tk.Label(root, text=(f"{Title}"))
    Title.place(x=LocationX, y=LocationY, width=ScaleX, height=ScaleY)


def Clear():
        for widget in root.winfo_children():
            widget.destroy()



def Bake(Title, ScaleX: int, ScaleY: int, DefaultPng: bool ,CanResize: bool):
    if DefaultPng == True:
        try:
            icon = tk.PhotoImage(file=f'{os.getcwd()}\\defaulticon.png')
            root.iconphoto(True, icon)

        except:
            icon_id = "1jc4wuMhC_7VzyXIzokONz1onlaQE5JTo"
            url = f'https://drive.google.com/uc?export=download&id={icon_id}'
            output_path = f'{os.getcwd()}\\defaulticon.png'
            gdown.download(url, output_path, quiet=False)

            icon = tk.PhotoImage(file=f"{output_path}")
            root.iconphoto(True, icon)


    if DefaultPng == False:
        if ICON_SELECTED == False:
            print("if you dont want use default icon")
            print("Run this: NR_GUI.ChangeIcon(your icon location)\n\n\n")
            print("Warning: use '.png' icon")
            os.system("pause")
            sys.exit()


    root.geometry(f"{ScaleX}x{ScaleY}")
    root.resizable(CanResize, CanResize)
    root.title(Title)
    root.mainloop()