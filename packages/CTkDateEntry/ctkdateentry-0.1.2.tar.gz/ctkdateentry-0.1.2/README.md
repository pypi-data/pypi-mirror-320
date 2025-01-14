# CTkDateEntry

**CTkDateEntry** is a Python library that extends the use of `customtkinter` to provide custom widgets such as a customtkinter DateEntry with a calendar `CTkCalendar` with selectable dates. It was designed to make it easier to create more modern and interactive graphical user interfaces (GUIs).

## Example:

Debug CTkDateEntry

![img_1](https://github.com/user-attachments/assets/d0be5cc6-7ab2-4135-b85a-64a1a386a097)

## What's New in Version 0.1.2 :

Creation of the CTkStringVar class, to insert indicative text into the CTkDateEtry entr

### Example:

```
import customtkinter as ctk
from ctkdateentry import CTkDateEntry, CTkStringVar
from tkinter import *

root = ctk.CTk()

root.geometry('200x200')
root.title('CTkDateEntry')
ctk.set_appearance_mode('light')
ctk.set_default_color_theme('dark-blue')

var = CTkStringVar(root, value='Enter a Date') #Variable that will be inserted in CTkDateEntry

date_entry = CTkDateEntry(root,
    width=150,
    variable =var,
    justify ='left',
    font=('Roboto', 14, 'bold'))
date_entry.pack(pady=50)

root.mainloop()
```

## Open Calendar CTkDateEntry

![CTkDateEntry_Dark-blue-removebg-preview](https://github.com/user-attachments/assets/08036e50-bf76-454c-be02-9571f0e37777)![CTkDateEntry_Light-removebg-preview](https://github.com/user-attachments/assets/993baf0d-7cfa-4a03-b8e0-dccf5d0090ff)

## Adjustments:

Adjustments to some parameters to make CTkDateEntry more customizable: font, text_color, fg_color, corner_radius, hover, and others.

exemplo:

## Features

- **CTkDateEntry**: A custom DateEntry based on Customtkinter to facilitate date selection in graphical interfaces.

## Themes

- **CTkDateEntry**: When customtkinter themes are applied to the graphical interface, they are automatically applied to CTkDateEntry, meaning there is no need to use a separate Theme Style

## Usage

Here's a simple example of how to use the `CTkDateEntr` widget:

```
import customtkinter as ctk
from ctkdateentry import CTkDateEntry

root = ctk.CTk()

root.geometry('200x200')
root.title('CTkDateEntry ')
calendar = CTkDateEntry(root)
calendar.pack(pady=50)

root.mainloop()
```
