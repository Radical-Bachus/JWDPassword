import string
import secrets
from cryptography.fernet import Fernet
import pickle
import customtkinter as ctk

from tkinter import messagebox, ttk, Listbox, END, Toplevel, ACTIVE
import pyperclip
import os, sys
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


#chooses theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

# creates app window
root = ctk.CTk()
root.geometry("400x300")
root.maxsize(400,800)
root.title("JWD")

# creates screen
frame = ctk.CTkFrame(master=root)
frame.pack(pady=20, padx=40, fill="both", expand=True)

# distionaries used to store user info and passwords
M_dictionary = {}
dictionary = {}
seg_buttons = []
passwords = []
btn_uses = []


# create masterkey if key does not exist already
if not os.path.exists(resource_path("masterkey.key")):
    with open(resource_path('masterkey.key'), 'xb') as M_key:
            masterkey = Fernet.generate_key()
            M_key.write(masterkey)
else:
    with open(resource_path('masterkey.key'), 'rb') as M_key:
        masterkey = M_key.read()

# making an encryption that can only be accessed by master key
M_fernet = Fernet(masterkey)


# making second key
if not os.path.exists(resource_path("filekey.key")):
    with open(resource_path('filekey.key'), 'xb') as filekey:
        key = Fernet.generate_key()
        filekey.write(key)
else:
    with open(resource_path('filekey.key'), 'rb') as filekey:
        key = filekey.read()
 

fernet = Fernet(key)

# function to be run after signing in 
def screen2():
    # makes screen bigger
    root.geometry("400x500")
    # decrypting userinfo file for further use
    decrypt("userinfo.txt", M_fernet)
    login_label.destroy()
    login_label2 = ctk.CTkLabel(master=frame, text="Password Management",
                                                  font=ctk.CTkFont(size=20, weight="bold"))
    login_label2.pack()
    # removing old widgets 
    button_1.destroy()
    entry_1.destroy()
    entry_2.destroy()   
    button_2.forget()

    #the dual screen tabview
    tabview = ctk.CTkTabview(master=frame, width=360, height=200)
    tabview.pack(pady=10, padx=10)

    # adding 2 tabs to the tabview window
    tabview.add("Create")
    tabview.add("Search")
    tabview.tab("Create").grid_columnconfigure(0, weight=1)
    tabview.tab("Search").grid_columnconfigure(0, weight=1)


    # digits to be used in password making
    digits = [3,4,5,6,7,8,9,10,11,12]
    digits = [str(i) for i in digits]
    optionmenu = ctk.CTkOptionMenu(tabview.tab("Create"), values=digits)
    optionmenu.set("Select Digits")
    
    # entry to enter password
    entry_3 = ctk.CTkEntry(tabview.tab("Create"),placeholder_text="Enter Password Use")
    entry_3.pack(pady=2, padx=10)

    optionmenu.pack(padx=4,pady=5)


    # if a password file exists
    if os.path.exists(resource_path("profile.txt")):
        # making existing passwords appear as segmented buttons
        decrypt(resource_path("profile.txt"), fernet)

        # password and what password is used for 
        new_dict = pickle.load(open(resource_path("profile.txt"), 'rb'))
        use_dict = list(new_dict.keys())
        searches = []
        for i in range(len(use_dict)):
            Use = use_dict[i]
            #search_password = str(Use + new_dict.get(Use))
            searches.append(Use)
        # Update the listbox
        def update(data):
            my_list.delete(0, END)

            # Add toppings to listbox
            for item in data:
                my_list.insert(END, item)
                
        # Create function to check entry vs listbox
        def check(e):
            # grab what was typed
            typed = entry_4.get()

            if typed == '':
                data = searches
            else:
                data = []
                for item in searches:
                    if typed.lower() in item.lower():
                        data.append(item)

            # update our listbox with selected items
            update(data)	

        # manage password popup messagebox
        def Manage(copy):
            root = ctk.CTk()
            def messageWindow():
                def delete():
                    selected = my_list.get(ACTIVE)
                    
                    # decrypts file storing passwords
                    decrypt(resource_path("profile.txt"), fernet)
                    if os.path.exists(resource_path("profile.txt")):
                        # gets dictionary information and delete it based on button selected
                        new_dict = pickle.load(open(resource_path("profile.txt"), 'rb'))
                        new_dict.pop(selected)

                        # deletes and recreates password storing file(update)
                        os.remove(resource_path("profile.txt"))
                        pickle.dump(new_dict, open( resource_path("profile.txt"), "xb" ) )

                    idx = my_list.get(0, END).index(selected)
                    my_list.delete(idx)
                    win.destroy()

                def copy():
                    selected = my_list.get(ACTIVE)
                    if use_dict.__contains__(selected):
                        pyperclip.copy(new_dict[selected])
                        win.destroy()

                win = root
                win.title('warning')
                win.geometry("175x100")
                win.maxsize(175,101)
                message = "Copy or Delete Password"
                ctk.CTkLabel(win, text=message, ).grid(column=1, row=1, columnspan=3, pady=10)
                ctk.CTkButton(win, text='Copy', command=copy, width=9).grid(column=1, row=2, padx=5)
                ctk.CTkButton(win, text='Delete', command=delete, width=9).grid(column=2, row=2, padx=5)
                ctk.CTkButton(win, text='Cancel', command=win.destroy, width=9).grid(column=3, row=2, padx = 5)
            messageWindow()
            root.mainloop()

        entry_4 = ctk.CTkEntry(tabview.tab("Search"),placeholder_text="Search Password")
        entry_4.pack(pady=2, padx=10)
        entry_4.bind("<KeyRelease>", check)


        # connect listbox scroll event to CTk scrollbar
        # Create a listbox
        my_list = Listbox(tabview.tab("Search"), width=50)
        my_list.pack(pady=20)

        # create CTk scrollbar
        ctk_scrollbar = ctk.CTkScrollbar(my_list,height=90,button_hover_color="skyblue",command=my_list.yview)
        ctk_scrollbar.place(x=270)

        my_list.configure(yscrollcommand=ctk_scrollbar.set)




        # Add the toppings to our list
        update(searches)

        # Create a binding on the listbox onclick
        my_list.bind("<<ListboxSelect>>", Manage)
        


        for i in range(len(use_dict)):

            # accessing each use
            Use = use_dict[i]

            # adding aditional text to info for user understanding3
            password = str(new_dict.get(Use))
            Use = str(Use)
         
            # adding passwords and uses to an array for further use
            passwords.append(password)
            btn_uses.append(Use)

       
            # function thats called when user wants to delete a password
            def delete_existing(value):
                # removes additional text from password 
                edited_value = str(value).replace("Copy ","")

                # checks to see if the segmented button clicked on exists in array of passwords
                if passwords.__contains__(edited_value):
                    # copies the password to clipboard
                    pyperclip.copy(edited_value)
                else :
                    # removes additional text from use
                    edited_use = str(value).replace("Delete ","")
                    print(edited_use)
                    # gets the specific button selected by finding its use index
                    index = btn_uses.index(edited_use)

                    # destroys the button at said use index
                    seg_buttons[index].destroy()

                    # decrypts file storing passwords
                    decrypt(resource_path("profile.txt"), fernet)
                    # if file exists that stores passwords
                    if os.path.exists(resource_path("profile.txt")):
                        # get dictionary information and delete it based on button selected
                        new_dict = pickle.load(open(resource_path("profile.txt"), 'rb'))
                        new_dict.pop(edited_use)

                        # deletes and recreates password storing file(update)
                        os.remove(resource_path("profile.txt"))
                        pickle.dump(new_dict, open( resource_path("profile.txt"), "xb" ) )
        # loops through every button that exists
        for i in range(len(seg_buttons)):
            # runs function to check if button was selected for deletion of copy password
            seg_buttons[i]._command = delete_existing


    # function to be called when user creates password
    def create_pword():
        tabview.set("Search")
        # # gets passwords use
        Use = entry_3.get()

        # gets all letters and numbers and stores it in variable
        alphabet = string.ascii_letters + string.digits 

        # chooses one of each character at random up to password length 
        # amount of times to create random password
        password = ''.join(secrets.choice(alphabet) for i in range(int(optionmenu.get())))
        #stores password info in dictonary and sets use equal to it
        dictionary[Use] = password

        my_list.insert(END, Use)
        searches.append(Use)


        # function called when user wants to delete a password they recently created
        def callback_delete(value):
            # if password option was clicked 
            if value.__contains__(password):
                #copy password to clipboard
                pyperclip.copy(password)
            # if use(e.g email) was clicked
            elif value.__contains__(Use):
                # remove unwanted text from button clicked
                edited_use = str(value).replace("Delete ","")
                
                decrypt(resource_path("profile.txt"), fernet)
                if os.path.exists(resource_path("profile.txt")):
                    # gets dictionary information and delete it based on button selected
                    new_dict = pickle.load(open(resource_path("profile.txt"), 'rb'))
                    new_dict.pop(edited_use)

                    # deletes and recreates password storing file(update)
                    os.remove(resource_path("profile.txt"))
                    pickle.dump(new_dict, open( resource_path("profile.txt"), "xb" ) )



        # checsk to see if password storing file is encrypted
        try:
            pickle.load(open(resource_path("profile.txt"), 'rb'))
        except:
            decrypt(resource_path("profile.txt"), fernet)
        
        # attempts to add dictionary information with passwords and uses to text file
        try:
            pickle.dump(dictionary, open(resource_path("profile.txt"), "xb" ) )
            encrypt(resource_path("profile.txt"), fernet)
        # write user info in file if file does exist    
        except:
            new_dict = pickle.load(open(resource_path("profile.txt"), 'rb'))
            new_dict[Use] = password
            pickle.dump(new_dict, open(resource_path("profile.txt"), "wb" ) )
            encrypt(resource_path("profile.txt"), fernet)
    
        
        


    # the button thats clicked when user wants to create new password
    button_3 = ctk.CTkButton(tabview.tab("Create"), text="Save", command=create_pword)
    button_3.pack(pady=5, padx=5)

    # button 2 is packs after for ui look
    button_2.pack()

# function called when user attempts to login
def button1_callback():
    # if user information is stored in a file
    if os.path.exists(resource_path("userinfo.txt")):
        # decrypts user information file
        decrypt(resource_path("userinfo.txt"), M_fernet)

        # accessing file information and gathers login and password info
        logininfo = pickle.load(open(resource_path("userinfo.txt"), 'rb')) 
        Login = str(entry_1.get())
        P_word = str(entry_2.get())

        # tests to see if login and password info entered matches whats stored in file
        if logininfo.get(Login) == P_word and list(logininfo.keys()).__contains__(Login):
            # takes user to second screen
            screen2()       
        else:
            # displays login info incorrrect window
            messagebox.showwarning('warning', 'LOGIN INFO INCORRECT, PLEASE TRY AGAIN!')       
    else:
        # asks for new login information if file doesnt exist
        Login = str(entry_1.get())
        P_word = str(entry_2.get())
        M_dictionary[Login] = P_word

        login_label.configure(text="New Login Information Saved\nPress enter again to Login")
    

        # stores new login info in file 
        decrypt(resource_path("userinfo.txt"), M_fernet)
        pickle.dump(M_dictionary, open(resource_path("userinfo.txt"), "xb" ) )

        # encrypts file lastly
        encrypt(resource_path("userinfo.txt"), M_fernet)




# decryption function
def decrypt(FileName, Fernet):
    try:
        # opening the encrypted file
        with open(FileName, 'rb') as enc_file:
            encrypted = enc_file.read()
        
        # decrypting the file passed into function with key passed into function
        decrypted = Fernet.decrypt(encrypted)
        
        # opening the file in write mode and
        # writing the decrypted data
        with open(FileName, 'wb') as dec_file:
            dec_file.write(decrypted)
    except:
        pass

# encryption function
def encrypt(FileName, Fernet):
    # opening the original file to encrypt
    with open(FileName, 'rb') as file:
        original = file.read()
        
    # encrypting the file passed into function with key passed into function
    encrypted = Fernet.encrypt(original)
    
    # opening the file in write mode and
    # writing the encrypted data
    with open(FileName, 'wb') as encrypted_file:
        encrypted_file.write(encrypted)

# function called when user clicks reset password button
def reset_pword():
    # checks to see if file exists then deletes it 
    if os.path.exists(resource_path("userinfo.txt")):
        os.remove(resource_path("userinfo.txt"))
        login_label.configure(text="User information resetted\nEnter New Login")

    else:
        # prints file doesnt exist if no file was found
        messagebox.showwarning('warning', 'FILE DOES NOT EXIST!') 

login_label = ctk.CTkLabel(master=frame, text="Login Page",
                                                  font=ctk.CTkFont(size=20, weight="bold"))
login_label.pack()

# if file exists user login widgets should look different (PLease login)
if os.path.exists(resource_path("userinfo.txt")):
    entry_1 = ctk.CTkEntry(master=frame,placeholder_text = "Enter User Login")
    entry_2 = ctk.CTkEntry(master=frame, show="*", placeholder_text = "Enter Login Password")
    button_1 = ctk.CTkButton(master=frame, command=button1_callback, text = "Enter")
else:
    # if file doesnt exist user info should look different (Please enter new information)
    entry_1 = ctk.CTkEntry(master=frame,placeholder_text = "Enter New User")
    entry_2 = ctk.CTkEntry(master=frame, show="*",placeholder_text = "Enter New Password")
    button_1 = ctk.CTkButton(master=frame, command=button1_callback,text ="Enter")


# add login widgets on screen
entry_1.pack(pady=10, padx=10)
entry_2.pack(pady=10, padx=10)    
button_1.pack(pady=2, padx=2)

# creates reset user information button
button_2 = ctk.CTkButton(master=frame, text="Reset User Information", command = reset_pword)
button_2.pack(pady=10, padx=10, side=ctk.RIGHT)


# makes everything above it run in a loop until application is closed
root.mainloop()

















