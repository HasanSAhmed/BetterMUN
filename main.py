from tkinter import ttk
import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.simpledialog
import time
import math
import os    
import ttkbootstrap as tb


window = tb.Window(themename="pulse")
window.title("BetterMUN")
window.geometry("700x400")
window.resizable(False, False)


backgroundColor = "White"
textColor = "#132257"
textFont = ("Calibri", 12)


# Configure default styles for all widgets
window.option_add("*Background", backgroundColor)
window.option_add("*Foreground", textColor)
window.option_add("*Font", textFont)
window.option_add("*Entry.Background", backgroundColor)
window.option_add("*Entry.Foreground", textColor)
window.option_add("*Button.Background", backgroundColor)
window.option_add("*Button.Foreground", textColor)
window.option_add("*Label.Background", backgroundColor)
window.option_add("*Label.Foreground", textColor)
window.option_add("*Frame.Background", backgroundColor)
window.option_add("*Toplevel.Background", backgroundColor)
window.option_add("*Listbox.Background", backgroundColor)
window.option_add("*Listbox.Foreground", textColor)
window.option_add("*Text.Background", backgroundColor)
window.option_add("*Text.Foreground", textColor)


# Assign conference list to blank list on start
conferenceList = []


# History Lists
conferenceHistory = [] # Roll Call, Debate Opened/Closed/Paused, Motion Passed/Failed
motionHistory = [] # Motion Name, Majority, Speakers, Time Created, Elapsed Time


# Lists of each name and status of delegates
delegateList = []
statusList = []


# Immediately load existing conferences from file
with open("conferences.txt", "r") as file:
    content = file.readlines()
    conferenceList = eval(content[0][22:])


def packAll(frame):
    frame.pack()
    for widget in frame.winfo_children():
        widget.pack(pady = 5)


# Works with initializeWindow to center windows on screen
def centerWindow(window, width=600, height=400):
    screenWidth = window.winfo_screenwidth()
    screenHeight = window.winfo_screenheight()
    x = (screenWidth / 2) - (width / 2)
    y = (screenHeight / 2) - (height / 2)
    window.geometry(f"{width}x{height}+{int(x)}+{int(y)}")


# Initializes TopLevel windows to be on top and transient to main window to avoid overlapping
def initializeWindow(win, title, winWidth=600, winHeight=400):
    win.title(title)
    win.configure(bg=backgroundColor)
    win.transient(window)
    win.grab_set()
    win.resizable(False, False)


    centerWindow(win, winWidth, winHeight)


# Sets up mouse wheel scrolling for scrollable areas
def onMouseWheel(event, canvas):
    delta = -1 * (event.delta // 120)
    canvas.yview_scroll(delta, "units")


def bindMouseWheel(widget, canvas):
    widget.bind_all("<MouseWheel>", lambda e: onMouseWheel(e, canvas))
    widget.bind_all("<Button-4>", lambda: canvas.yview_scroll(-1, "units"))
    widget.bind_all("<Button-5>", lambda: canvas.yview_scroll(1, "units"))


# Creates a scrollable area with a canvas, scrollbar, and scrollable frame
def createScrollableArea(parent, bg="white", width=0, height=0):
    containerBg = bg
    canvas = tk.Canvas(parent, bg=containerBg, highlightthickness=0, width=width, height=height)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)


    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")


    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)


    scrollableFrame = tk.Frame(canvas, bg=containerBg)
    scrollableFrame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )


    canvas.create_window((0, 0), window=scrollableFrame, anchor="nw")
    bindMouseWheel(parent, canvas)


    return canvas, scrollableFrame, scrollbar


# Public definitions for row management
def refreshRows(eLab, scrollFrame, rowsList, widgets, rowOffset, col, stick, xPad, yPad):
    eLab.config(text="")  # Clear error on refresh
    for widget in scrollFrame.winfo_children():
        widget.grid_forget()


    # Place updated rows in scrollableFrame
    for i, row in enumerate(rowsList):
        baseRow = i * 3


        for y, widget in enumerate(widgets):
            row[widget].grid(in_=scrollFrame, row=baseRow + rowOffset[y], column=col[y], sticky=stick[y], padx=xPad[y], pady=yPad[y])


        scrollFrame.grid_columnconfigure(0, weight=1)


def deleteRow(index, list, widgets, refreshFunc):
    row = list[index]
    for x in (widgets):
        row[x].destroy()
    list.pop(index)


    # This isn't actually an error...
    refreshFunc


# Called when the user closes the main window
def quitApp():
    global currentConf, stopwatchRunning, startTime, totalPausedTime, isPaused, pauseStartTime


    # Automatically close debate if it's still running
    if stopwatchRunning:
        stopwatchRunning = False
        isPaused = False
        startTime = None
        totalPausedTime = 0
        pauseStartTime = None


        # Add to history
        conferenceHistory.append(["Debate Closed", time.strftime("%d-%m-%Y at %H:%M")])


    # Write the conference list to file
    with open("conferences.txt", "w") as confs:
        confs.writelines(f"Previous Conferences: {conferenceList}")


    # If the user has a conference open, save it properly
    try:
        with open(f"{currentConf}.txt", "w") as delegates:
            delegates.writelines(f"delegateList: {delegateList}\nstatusList: {statusList}\nHistory: {conferenceHistory}\nMotions: {motionHistory}")
    except:
        pass


    messagebox.showinfo("Closing...", "Saving file...")
    window.destroy()


# Frames for main window...
# 1. Dashboard
dashboard = tk.Frame(window, bg=backgroundColor)
tk.Label(dashboard, text="Welcome to BetterMUN", bg=backgroundColor, fg=textColor, font=textFont).pack(pady=10)
tk.Label(dashboard, text="Revolutionizing Model United Nations\nOne Motion At a Time", bg=backgroundColor, fg=textColor, font=textFont)
tk.Button(dashboard, text="Create New Conference", command=lambda: createNewConference(),
          bg=backgroundColor, fg=textColor, font=textFont, relief="raised", bd=2)
tk.Button(dashboard, text="Continue Previous Conference", command=lambda: continuePrevConference(),
          bg=backgroundColor, fg=textColor, font=textFont, relief="raised", bd=2)
packAll(dashboard)


# 2. Main Menu
mainMenu = tk.Frame(window, bg=backgroundColor)
tk.Label(mainMenu, text="BetterMUN Main Menu", bg=backgroundColor, fg=textColor, font=textFont).pack(pady=10)
tk.Button(mainMenu, text="Roll Call", command=lambda: rollCall(),
          bg=backgroundColor, fg=textColor, font=textFont, relief="raised", bd=2)
tk.Button(mainMenu, text="Open/Close/Pause Debate", command=lambda: ocpDebate(),
          bg=backgroundColor, fg=textColor, font=textFont, relief="raised", bd=2)
tk.Button(mainMenu, text="Motions/Voting/Speakers List", command=lambda: motionsPage(),
          bg=backgroundColor, fg=textColor, font=textFont, relief="raised", bd=2)
tk.Button(mainMenu, text="Conference History", command=lambda: ConferenceHistory(),
          bg=backgroundColor, fg=textColor, font=textFont, relief="raised", bd=2)


# Program definitions:
def createNewConference():
  global newConferenceWindow


  newConferenceWindow = tk.Toplevel(window)
  initializeWindow(newConferenceWindow, "New Conference")


  tk.Label(newConferenceWindow, text="Conference Name:", font=textFont).pack()


  #Conference Name
  conferenceName = tk.Entry(newConferenceWindow, font=textFont)
  conferenceName.pack()


  tk.Label(
      newConferenceWindow,
      text="Conference Type:\n(General Assembly, Security Council, etc.)", font=textFont).pack()


  # Conference Type
  conferenceType = tk.Entry(newConferenceWindow, font=textFont)
  conferenceType.pack()


  tk.Button(newConferenceWindow,
      text="Create", command=lambda: checkCompletion(), font=textFont).pack()


  #Insures all fields are filled out before submitting and that there are no duplicate names
  def checkCompletion():
    global conferenceList


    # Check if entry is filled for each row
    if conferenceName.get() == "" or conferenceType.get() == "":
        errorLabel = tk.Label(newConferenceWindow, text="Please fill out all fields...", font=textFont)
        errorLabel.pack()
    # Check for duplicate conference names
    elif any(conferenceName.get().strip() == conf[0] for conf in conferenceList):
        errorLabel = tk.Label(newConferenceWindow, text="Conference name already exists...", font=textFont)
        errorLabel.pack()
    else:
        conferenceList.append([conferenceName.get().strip(), conferenceType.get()])


        # Create a new file for the conference
        with open(f"{conferenceName.get().strip()}.txt", "a") as newConf:
            newConf.writelines("delegateList: []\nstatusList: []\nHistory: []\nMotions: []")


        global currentConf
        currentConf = conferenceName.get().strip()


        newConferenceWindow.destroy()


        # Switch to main menu frame
        dashboard.pack_forget()
        packAll(mainMenu)


def continuePrevConference():
    if len(conferenceList) < 1:
        messagebox.showerror("Error", "No previous conferences...")
    else:
        prevConferencesWindow = tk.Toplevel(window)
        initializeWindow(prevConferencesWindow, "Previous Conferences")


        # Loads scrollable area for window
        canvas, scrollableFrame, scrollbar = createScrollableArea(prevConferencesWindow)
        conferenceRows = []


        errorLabel = tk.Label(prevConferencesWindow, text="", font=textFont)
        errorLabel.grid(row=1, column=0, columnspan=2, sticky="w", padx=15, pady=(5,15))


        saveBtn = tk.Button(prevConferencesWindow, text="Save", cursor="hand2", font=textFont)
        saveBtn.grid(row=2, column=1, sticky="w", padx=(0,15), pady=(0,15))


        def refreshConfs():
            refreshRows(errorLabel, scrollableFrame, conferenceRows, ['nameLabel', 'nameEntry', 'typeLabel', 'typeEntry', 'openButton', 'delButton'],
            [0, 1, 0, 1, 2, 2], [0, 0, 1, 1, 0, 1],
            ['w', 'ew', 'w', 'ew', 'ew', 'w'],
            [(0,5), (0,5), (0,5), (0,5), (0,5), (0,5)],
            [(0, 10), (0, 10), (0, 10), (0, 10), (0, 20), (0, 10)])


            # Update delete and open button commands with correct indices
            for i, row in enumerate(conferenceRows):
                row['delButton'].configure(command=lambda i=i: deleteConference(i))
                row['openButton'].configure(command=lambda i=i: openPrev(i))


        def deleteConference(index):
            global conferenceList


            deleteRow(index, conferenceRows, ['nameLabel', 'nameEntry', 'typeLabel', 'typeEntry', 'openButton', 'delButton'], refreshConfs())


            # Delete the file associated with the conference
            os.remove(f"{conferenceList[index][0]}.txt")
            conferenceList.pop(index)


        def openPrev(index):
            global conferenceList
            global delegateList
            global statusList
            global conferenceHistory
            global motionHistory
            global currentConf


            # Retrieve the conference details from the file
            with open(f"{conferenceList[index][0]}.txt", "r") as file:
                content = file.readlines()
                delegateList = eval(content[0][14:])
                statusList = eval(content[1][11:])
                conferenceHistory = eval(content[2][9:])
                motionHistory = eval(content[3][9:])


            # Set the current conference to the one being opened, so that it can be saved properly
            currentConf = conferenceList[index][0]


            # Switch to main menu frame
            prevConferencesWindow.destroy()
            dashboard.pack_forget()
            packAll(mainMenu)


        # Appends widgets for each conference to the conferenceRows list
        def addConference(name="", type=""):
            errorLabel.config(text="")  # Clear error on add


            nameLabel = tk.Label(scrollableFrame, text="Conference Name", font=textFont)
            nameEntry = tk.Entry(scrollableFrame, font=textFont)
            nameEntry.insert(0, name)


            typeLabel = tk.Label(scrollableFrame, text = "Conference Type", font=textFont)
            typeEntry = tk.Entry(scrollableFrame, font=textFont)
            typeEntry.insert(0, type)


            openBtn = tk.Button(scrollableFrame, text="Open", font=textFont)
            deBtn = tk.Button(scrollableFrame, text="Remove", font=textFont)


            conferenceRows.append({
                'nameLabel': nameLabel,
                'nameEntry': nameEntry,
                'typeLabel': typeLabel,
                'typeEntry': typeEntry,
                'openButton': openBtn,
                'delButton': deBtn
            })


            # Refresh rows to place new widgets accordingly
            refreshConfs()


        def saveConference():
            global conferenceList


            check = True
            tempList = []
            nameList = []


            for row in conferenceRows:
                # Check if entry is filled for each row
                if row['nameEntry'].get() == "" or row['typeEntry'].get() == "":
                    errorLabel.config(text="Please fill out required fields...")
                    check = False
                else:
                    # Append a tuple instead of a list (so that it is hashable)
                    tempList.append((row['nameEntry'].get(), row['typeEntry'].get()))
                    nameList.append(row['nameEntry'].get().strip())
                    continue


            # Check for duplicate conference names
            if len(nameList) != len(set(nameList)):
                errorLabel.config(text="Duplicate names are not allowed...")
                check = False


            if check:
                # Save conferences to system
                tempList = []


                for row in conferenceRows:
                    name = row['nameEntry'].get().strip()
                    type = row['typeEntry'].get().strip()
                    if name and type:
                        tempList.append([name, type])
                        # Update the file name
                        os.rename(f"{conferenceList[conferenceRows.index(row)][0]}.txt", f"{name}.txt")


                conferenceList = tempList
                errorLabel.config(text="Delegates have been saved!")  


        saveBtn.configure(command=saveConference)


        # Add all previous conferences to the list
        for y in range(len(conferenceList)):
            addConference(conferenceList[y][0].strip(), conferenceList[y][1])


# Main program definitions:


presentDelegates = []


def rollCall():
    delListWin = tk.Toplevel(window)
    initializeWindow(delListWin, "Delegate List")


    # Loads scrollable area for window
    canvas, scrollableFrame, scrollbar = createScrollableArea(delListWin)
    delegateRows = []


    errorLabel = tk.Label(delListWin, text="", font=textFont)
    errorLabel.grid(row=1, column=0, columnspan=2, sticky="w", padx=15, pady=(5,15))


    addBtn = tk.Button(delListWin, text="Add Delegate", cursor="hand2", font=textFont)
    saveBtn = tk.Button(delListWin, text="Save Delegates", cursor="hand2", font=textFont)
    addBtn.grid(row=2, column=0, sticky="w", padx=(15, 10), pady=(0,15))
    saveBtn.grid(row=2, column=1, sticky="w", padx=(0,15), pady=(0,15))


    def refreshDelegates():
        refreshRows(errorLabel, scrollableFrame, delegateRows, ['label', 'entry', 'status', 'button'],
            [0, 1, 1, 1], [0, 0, 1, 2], ['w', 'ew', 'ew', 'w'],
            [(0,5), (0,5), (0,5), (0,5)], [(0, 10), (0, 10), (0, 10), (0, 10)])


        # Update delete button commands with correct indices
        for i, row in enumerate(delegateRows):
            row['button'].configure(command=lambda i=i: deleteDelegate(i))


    def deleteDelegate(index):
        # Conference must have at least two delegates
        if len(delegateRows) <= 2:
            errorLabel.config(text="Must have at least two delegates.")
        else:
            deleteRow(index, delegateRows, ['label', 'entry', 'status', 'button'], refreshDelegates())


    # Adds a new delegate row to the list
    def addDelegate(name="", status="Delegate Status..."):
        errorLabel.config(text="")
        label = tk.Label(scrollableFrame, text="Delegate Name", font=textFont)
        entry = tk.Entry(scrollableFrame, font=textFont)
        entry.insert(0, name)
        options = ttk.Combobox(scrollableFrame, state="readonly", values=['Present', 'Present and Voting', 'Absent'], font=textFont)
        options.set(status)
        deBtn = tk.Button(scrollableFrame, text="Delete", font=textFont)


        delegateRows.append({
            'label': label,
            'entry': entry,
            'status': options,
            'button': deBtn
        })


        # Refresh rows to place new widgets accordingly
        refreshDelegates()


    def saveDelegates():
        check = True
        tempList = []


        for row in delegateRows:
            if row['entry'].get() == "" or row['status'].get() == "Delegate Status...":
                errorLabel.config(text="Please fill out required details for each delegate...")
                check = False
            else:
                tempList.append(row['entry'].get())


        if len(tempList) != len(set(tempList)):
            errorLabel.config(text="Duplicate names are not allowed...")
            check = False


        if check:
            # Save delegates to system
            tempList1 = []
            tempList2 = []


            for row in delegateRows:
                name = row['entry'].get().strip()
                status = row['status'].get().strip()
                if name:
                    tempList1.append(name)
                if status:
                    tempList2.append(status)


            global delegateList, statusList, presentDelegates
            delegateList = tempList1
            statusList = tempList2
            presentDelegates = []


            # Assigns present delegates to a list
            for q in range(len(statusList)):
                if statusList[q] == "Present and Voting" or statusList[q] == "Present":
                    presentDelegates.append(delegateList[q])


            # Add to history
            conferenceHistory.append(["Roll Call Completed",
                time.strftime("%d-%m-%Y at %H:%M")])
            delListWin.destroy()


    addBtn.configure(command=addDelegate)
    saveBtn.configure(command=saveDelegates)


    # Add all delegates to the list
    if len(delegateList) > 1:
        for y in range(len(delegateList)):
            addDelegate(delegateList[y], statusList[y])
    else:
        # Add minimum of two delegates
        for i in range(2):
            addDelegate()


# Open/Close/Pause Debate
# set initial states for stopwatch
startTime = None
isPaused = False
stopwatchRunning = False
totalPausedTime = 0
pauseStartTime = None


# formats seconds into hours:minutes:seconds display
def formatTime(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


debateOpened = False


def ocpDebate():
    global startTime, isPaused, stopwatchRunning, totalPausedTime, pauseStartTime, debateOpened


    # Make sure delegates are present before allowing debate to be opened
    if presentDelegates == []:
        messagebox.showerror("Error", "No delegates are present. Please complete roll call first...")
        return


    ocpDebateWindow = tk.Toplevel(window)
    initializeWindow(ocpDebateWindow, "Open/Close/Pause Debate")
    ocpDebateWindow.grid_columnconfigure(0, weight=1)


    # Display labels
    tk.Label(ocpDebateWindow, text="Control Debate Status from here.", font=textFont).grid(row=0, column=0, pady=10)
    tk.Label(ocpDebateWindow, text="To start, click Open Debate", font=textFont).grid(row=1, column=0, pady=5)


    debateStatus = tk.Label(ocpDebateWindow, text="", font=textFont)
    debateStatus.grid(row=5, column=0, pady=10)


    displayLabel = tk.Label(ocpDebateWindow, text="Elapsed Time: 00:00:00", font=textFont)
    displayLabel.grid(row=6, column=0, pady=5)


    # Functions
    def updateButtonStates():
        if not stopwatchRunning:
            openBtn.config(state="normal", text="Open Debate")
            pauseBtn.config(state="disabled")
            closeBtn.config(state="disabled")
        elif isPaused:
            openBtn.config(state="normal", text="Resume Debate")
            pauseBtn.config(state="disabled")
            closeBtn.config(state="normal")
        else:
            openBtn.config(state="disabled", text="Open Debate")
            pauseBtn.config(state="normal")
            closeBtn.config(state="normal")


    def openDebate():
        global startTime, totalPausedTime, pauseStartTime, isPaused, stopwatchRunning, debateOpened


        if isPaused:
            if pauseStartTime is not None:
                totalPausedTime += time.time() - pauseStartTime
                pauseStartTime = None

            isPaused = False
            debateStatus.config(text="Debate is resumed.")
        else:
            if startTime is None:
                startTime = time.time()
                totalPausedTime = 0

            stopwatchRunning = True
            debateStatus.config(text="Debate is open.")


        debateOpened = True


        # Add to history
        conferenceHistory.append(["Debate Opened", time.strftime("%d-%m-%Y at %H:%M")])
        updateStopwatch()
        updateButtonStates()


    def pauseDebate():
        global isPaused, pauseStartTime, debateOpened


        # Only allow pausing if debate is open and not already paused
        if stopwatchRunning and not isPaused:
            isPaused = True
            debateOpened = False


            pauseStartTime = time.time()
            debateStatus.config(text="Debate is paused.")


            # Add to history
            conferenceHistory.append(["Debate Paused", time.strftime("%d-%m-%Y at %H:%M")])
            updateButtonStates()


    def closeDebate():
        global stopwatchRunning, startTime, totalPausedTime, isPaused, pauseStartTime, debateOpened


        # Reset all stopwatch variables
        stopwatchRunning = False
        isPaused = False
        debateOpened = False


        startTime = None
        totalPausedTime = 0
        pauseStartTime = None
        debateStatus.config(text="Debate is closed.")
        displayLabel.config(text="Elapsed Time: 00:00:00")


        # Add to history
        conferenceHistory.append(["Debate Closed", time.strftime("%d-%m-%Y at %H:%M")])
        updateButtonStates()


    def updateStopwatch():
        if stopwatchRunning and startTime is not None and not isPaused:
            elapsed = time.time() - startTime - totalPausedTime
            displayLabel.config(text=f"Elapsed Time: {formatTime(elapsed)}")
            ocpDebateWindow.after(100, updateStopwatch)


        elif stopwatchRunning and isPaused and pauseStartTime:
            # This is not an error, causes no runtime errors
            elapsed = pauseStartTime - startTime - totalPausedTime
            displayLabel.config(text=f"Elapsed Time: {formatTime(elapsed)}")


    # Buttons
    openBtn = tk.Button(ocpDebateWindow, text="Open Debate", command=openDebate, font=textFont)
    openBtn.grid(row=2, column=0, pady=5)


    pauseBtn = tk.Button(ocpDebateWindow, text="Pause Debate", command=pauseDebate, font=textFont)
    pauseBtn.grid(row=3, column=0, pady=5)


    closeBtn = tk.Button(ocpDebateWindow, text="Close Debate", command=closeDebate, font=textFont)
    closeBtn.grid(row=4, column=0, pady=5)


    # Initial UI state setup
    if stopwatchRunning and startTime is not None:
        if isPaused:
            elapsed = pauseStartTime - startTime - totalPausedTime if pauseStartTime else 0
            displayLabel.config(text=f"Elapsed Time: {formatTime(elapsed)}")
            debateStatus.config(text="Debate is paused.")
        else:
            elapsed = time.time() - startTime - totalPausedTime
            displayLabel.config(text=f"Elapsed Time: {formatTime(elapsed)}")
            debateStatus.config(text="Debate is open.")
            updateStopwatch()
    else:
        debateStatus.config(text="Debate is closed.")
        displayLabel.config(text="Elapsed Time: 00:00:00")


    updateButtonStates()


# Motions/Voting/Speakers List
motionsList = []
speakersList = []
currentMotion = None
speakerExtraTime = {}  # stores extra time devoted to speakers


def motionsPage():
    global motionsWindow, debateOpened


    if not debateOpened:
        messagebox.showerror("Error", "Debate is not open. Please open debate before making motions...")
        return


    # close existing motions window if it exists
    try:
        # Not an error
        if motionsWindow and motionsWindow.winfo_exists():
            motionsWindow.destroy()
    except:
        pass


    # create main motions window
    motionsWindow = tk.Toplevel(window)
    initializeWindow(motionsWindow, "Motions")
    motionsWindow.grid_columnconfigure(0, weight=1)


    # main title and labels
    tk.Label(motionsWindow, text="Motions", font=textFont).grid(row=0, column=0, pady=10)
    tk.Label(motionsWindow, text="Previous Motions:", font=textFont).grid(row=1, column=0, sticky="w", padx=20, pady=(10,5))


    # frame to hold the motions listbox
    motionsFrame = tk.Frame(motionsWindow)
    motionsFrame.grid(row=2, column=0, sticky="ew", padx=20, pady=5)
    motionsFrame.grid_columnconfigure(0, weight=1)


    # listbox to show all motions
    motionsListbox = tk.Listbox(motionsFrame, height=8, font=textFont)
    motionsListbox.grid(row=0, column=0, sticky="ew")


    # display previously submitted motions in listbox if any
    def refreshMotionsList():
        motionsListbox.delete(0, tk.END)
        if len(motionsList) > 0:
            for i, motionData in enumerate(motionsList):
                motionText = f"{i+1}. {motionData['motion']}"
                motionsListbox.insert(tk.END, motionText)
        else:
            motionsListbox.insert(tk.END, "No motions submitted yet")


    refreshMotionsList()


    # buttons for main actions
    btnFrame = tk.Frame(motionsWindow)
    btnFrame.grid(row=3, column=0, pady=20)


    tk.Button(btnFrame, text="Enter New Motion", command=lambda: enterNewMotion(), font=textFont).grid(row=0, column=0, padx=10)
    tk.Button(btnFrame, text="Go to Voting", command=lambda: votingPage(), font=textFont).grid(row=0, column=1, padx=10)


def enterNewMotion():
    # create window for entering new motions
    newMotionWindow = tk.Toplevel(window)
    initializeWindow(newMotionWindow, "New Motion")
    newMotionWindow.grid_columnconfigure(0, weight=1)


    # title and labels for motion entry
    tk.Label(newMotionWindow, text="Enter New Motion", font=textFont).grid(row=1, column=0, pady=5)


    tk.Label(newMotionWindow, text="Motion Name:", font=textFont).grid(row=2, column=0, pady=5)
    motionEntry = tk.Entry(newMotionWindow, font=textFont)
    motionEntry.grid(row=3, column=0, pady=5, padx=20, sticky="ew")


    # error label for validation messages
    errorLabel = tk.Label(newMotionWindow, text="", font=textFont)
    errorLabel.grid(row=4, column=0, pady=5)


    # submit and return buttons
    tk.Button(newMotionWindow, text="Submit Motion", command=lambda: submitMotion(), font=textFont).grid(row=5, column=0, pady=10)
    tk.Button(newMotionWindow, text="Return to Motions", command=lambda: [newMotionWindow.destroy()], font=textFont).grid(row=6, column=0, pady=5)


    # validates and submits the new motion
    def submitMotion():
        motion = motionEntry.get().strip()


        if motion == "":
            errorLabel.config(text="Please fill out all fields")
            return


        # add motion to the list as dictionary
        motionsList.append({
            'motion': motionEntry.get(),
        })


        # close windows and refresh motions page
        motionsWindow.destroy()
        newMotionWindow.destroy()
        motionsPage()


def votingPage():
    # create voting window
    votingWindow = tk.Toplevel(window)
    initializeWindow(votingWindow, "Voting Page")
    votingWindow.grid_columnconfigure(0, weight=1)


    # title and instruction labels
    tk.Label(votingWindow, text="Voting Page", font=textFont).grid(row=0, column=0, pady=10)
    tk.Label(votingWindow, text="Select Motion to Vote on:", font=textFont).grid(row=1, column=0, pady=5)


    # listbox to display available motions
    motionList = tk.Listbox(votingWindow, height=6, font=textFont)
    motionList.grid(row=2, column=0, sticky="ew", padx=20, pady=10)


    # populate listbox with motions
    for i, motionData in enumerate(motionsList):
        motionText = f"{i+1}. {motionData['motion']}"
        motionList.insert(tk.END, motionText)


    # show message if no motions available
    if len(motionsList) == 0:
        motionList.insert(tk.END, "No motions submitted yet")


    # error label for validation
    errorLabel = tk.Label(votingWindow, text="", font=textFont)
    errorLabel.grid(row=3, column=0, pady=5)


    # voting action buttons
    btnFrame = tk.Frame(votingWindow)
    btnFrame.grid(row=4, column=0, pady=20)


    tk.Button(btnFrame, text="Vote on Selected Motion", command=lambda: vote(), font=textFont).grid(row=0, column=0, padx=10)
    tk.Button(btnFrame, text="Return to Motions", command=lambda: [votingWindow.destroy(), motionsPage()], font=textFont).grid(row=0, column=1, padx=10)


    def vote():
        selection = motionList.curselection()
        if not selection:
            errorLabel.config(text="Please select a motion to vote on")
            return


        if len(motionsList) == 0:
            errorLabel.config(text="No motions available to vote on")
            return


        selectedIndex = selection[0]
        selectedMotion = motionsList[selectedIndex]
        numPresent = len(presentDelegates)


        # get vote count from user input (not an error)
        votes = tk.simpledialog.askinteger("Vote", f"Enter number of 'Yes' votes for:\n'{selectedMotion['motion']}':")


        if votes is None:
            return


        if votes < 0 or votes > numPresent:
            errorLabel.config(text=f"Invalid number of votes. Must be between 0 and {numPresent}")
            return


        # calculate required majorities
        simpleMajority = (numPresent // 2) + 1
        twoThirdsMajority = math.ceil(2/3 * numPresent)


        simplePasses = votes >= simpleMajority
        twoThirdsPasses = votes >= twoThirdsMajority


        global currentMotion
        currentMotion = motionsList.pop(selectedIndex)


        # determine voting outcome based on majorities
        global voteRes


        if twoThirdsPasses and simplePasses:
            resultMsg = f"VOTE PASSED (Both majorities)!\n\nMotion: {selectedMotion['motion']}\nYes votes: {votes}/{numPresent}\nSimple majority: {simpleMajority}\n2/3 majority: {twoThirdsMajority}\n\nProceeding to Speakers List..."
            votingWindow.destroy()
            currentMotion = selectedMotion
            showVoteResult(resultMsg, "speakers")


            # Add to history
            conferenceHistory.append(["Motion Passed", time.strftime("%d-%m-%Y at %H:%M")])

            # store majority type for history
            voteRes = "Simple and 2/3 Majority"


        elif simplePasses and not twoThirdsPasses:
            resultMsg = f"VOTE PASSED (Simple majority only)!\n\nMotion: {selectedMotion['motion']}\nYes votes: {votes}/{numPresent}\nSimple majority: {simpleMajority}\n2/3 majority: {twoThirdsMajority}\n\nChoose your next action:"
            votingWindow.destroy()
            currentMotion = selectedMotion
            showVoteResult(resultMsg, "choice")

            # Add to history
            conferenceHistory.append(["Motion Passed", time.strftime("%d-%m-%Y at %H:%M")])

            # store majority type for history
            voteRes = "Simple Majority"


        else:
            resultMsg = f"VOTE FAILED!\n\nMotion: {selectedMotion['motion']}\nYes votes: {votes}/{numPresent}\nSimple majority: {simpleMajority}\n2/3 majority: {twoThirdsMajority}\n\nReturning to Motions..."
            votingWindow.destroy()
            showVoteResult(resultMsg, "motions")


            # add to history
            conferenceHistory.append(["Motion Failed", time.strftime("%d-%m-%Y at %H:%M")])

            # add failed motion to motion history
            motionHistory.append([selectedMotion['motion'], "Failed", "N/A", time.strftime("%d-%m-%Y at %H:%M"), "N/A"])


def showVoteResult(resultMsg, outcome):
    # display voting results and provide next action options
    resultWindow = tk.Toplevel(window)
    initializeWindow(resultWindow, "Vote Result")
    resultWindow.grid_columnconfigure(0, weight=1)


    tk.Label(resultWindow, text="Vote Result", font=textFont).grid(row=0, column=0, pady=10)
    tk.Label(resultWindow, text=resultMsg, justify="left", font=textFont).grid(row=1, column=0, pady=20, padx=20)


    btnFrame = tk.Frame(resultWindow)
    btnFrame.grid(row=2, column=0, pady=20)


    # show different buttons based on voting outcome
    if outcome == "speakers":
        tk.Button(btnFrame, text="Continue to Speakers List", command=lambda: [resultWindow.destroy(), speakersListPage()], font=textFont).grid(row=0, column=0, padx=10)
    elif outcome == "choice":
        tk.Button(btnFrame, text="Return to Motions", command=lambda: [resultWindow.destroy(), motionsPage()], font=textFont).grid(row=0, column=0, padx=10)
        tk.Button(btnFrame, text="Continue to Speakers List", command=lambda: [resultWindow.destroy(), speakersListPage()], font=textFont).grid(row=0, column=1, padx=10)
    else:
        tk.Button(btnFrame, text="Return to Motions", command=lambda: [resultWindow.destroy(), motionsPage()], font=textFont).grid(row=0, column=0, padx=10)


def speakersListPage():
    # Create window for managing speakers list
    speakersWindow = tk.Toplevel(window)
    initializeWindow(speakersWindow, "Speakers List")


    canvas, scrollableFrame, scrollbar = createScrollableArea(speakersWindow)
    speakerRows = []


    errorLabel = tk.Label(speakersWindow, text="", font=textFont)
    errorLabel.grid(row=1, column=0, columnspan=3, sticky="w", padx=15, pady=(5,15))


    btnFrame = tk.Frame(speakersWindow)
    btnFrame.grid(row=2, column=0, columnspan=3, pady=(0,15))


    addBtn = tk.Button(btnFrame, text="Add Speaker", cursor="hand2", font=textFont)
    addBtn.grid(row=0, column=0, padx=10)


    saveBtn = tk.Button(btnFrame, text="Submit Speakers", cursor="hand2", font=textFont)
    saveBtn.grid(row=0, column=1, padx=10)


    timerBtn = tk.Button(btnFrame, text="Create Timer", cursor="hand2", state="disabled", font=textFont)
    timerBtn.grid(row=0, column=2, padx=10)


    returnBtn = tk.Button(btnFrame, text="Return to Motions", cursor="hand2", font=textFont)
    returnBtn.grid(row=0, column=3, padx=10)


    # refresh speaker rows display
    def refreshSpeakers():
        refreshRows(errorLabel, scrollableFrame, speakerRows, ['label', 'entry', 'button'],
            [0, 1, 1], [0, 0, 2], ['w', 'ew', 'w'],
            [(0,5), (0,5), (0,5)], [(0, 10), (0, 10), (0, 10)])


        for i, row in enumerate(speakerRows):
            row['button'].configure(command=lambda i=i: deleteSpeaker(i))


    # remove speaker from list
    def deleteSpeaker(index):
        if len(speakerRows) <= 1:
            errorLabel.config(text="Must have at least one speaker.")
        else:
            deleteRow(index, speakerRows, ['label', 'entry', 'button'], refreshSpeakers())


    # add new speaker to list
    def addSpeaker(name=""):
        if len(speakerRows) == len(presentDelegates):
            errorLabel.config(text="Maximum Number of speakers must be equal to number of present delegates.")
        else:
            errorLabel.config(text="")
            label = tk.Label(scrollableFrame, text="Speaker Name", font=textFont)
            entry = tk.Entry(scrollableFrame, font=textFont)
            entry.insert(0, name)
            deBtn = tk.Button(scrollableFrame, text="Delete", font=textFont)


            speakerRows.append({
                'label': label,
                'entry': entry,
                'button': deBtn
            })
            refreshSpeakers()


    # validate and save speakers list
    def submitSpeakers():
        check = True
        tempList = []


        for row in speakerRows:
            if row['entry'].get().strip() == "":
                errorLabel.config(text="Please fill out name for each speaker...")
                check = False
            else:
                tempList.append(row['entry'].get().strip())


        if len(tempList) != len(set(tempList)):
            errorLabel.config(text="Duplicate names are not allowed...")
            check = False


        if check:
            global speakersList
            speakersList = tempList
            errorLabel.config(text="Speakers list has been submitted!")
            timerBtn.config(state="normal")


    # proceed to timer creation if speakers are submitted
    def createSpeakerTimer():
        if len(speakersList) == 0:
            errorLabel.config(text="Please submit speakers list first")
            return
        speakersWindow.destroy()
        createTimerWindow()


    addBtn.configure(command=addSpeaker)
    saveBtn.configure(command=submitSpeakers)
    timerBtn.configure(command=createSpeakerTimer)
    returnBtn.configure(command=lambda: [speakersWindow.destroy(), motionsPage()])


    # start with one speaker
    addSpeaker()


def createTimerWindow():
    # window to set up speaking time for each speaker
    timerSetupWindow = tk.Toplevel(window)
    initializeWindow(timerSetupWindow, "Create Timer")
    timerSetupWindow.grid_columnconfigure(1, weight=1)


    tk.Label(timerSetupWindow, text="Create Timer", font=textFont).grid(row=0, column=0, columnspan=2, pady=10)
    tk.Label(timerSetupWindow, text="Speaking Time Per Speaker:", font=textFont).grid(row=1, column=0, columnspan=2, pady=5)


    tk.Label(timerSetupWindow, text="Minutes:", font=textFont).grid(row=2, column=0, sticky="e", padx=(0,5), pady=5)
    minutesEntry = tk.Entry(timerSetupWindow, width=10, font=textFont)
    minutesEntry.grid(row=2, column=1, sticky="w", padx=(5,0), pady=5)


    tk.Label(timerSetupWindow, text="Seconds:", font=textFont).grid(row=3, column=0, sticky="e", padx=(0,5), pady=5)
    secondsEntry = tk.Entry(timerSetupWindow, width=10, font=textFont)
    secondsEntry.grid(row=3, column=1, sticky="w", padx=(5,0), pady=5)


    # validates that input is a number
    def validateInteger(newValue):
        if newValue == "":
            return True
        try:
            int(newValue)
            return True
        except ValueError:
            return False


    validateCmd = timerSetupWindow.register(validateInteger)
    minutesEntry.config(validate="key", validatecommand=(validateCmd, "%P"))
    secondsEntry.config(validate="key", validatecommand=(validateCmd, "%P"))


    tk.Label(timerSetupWindow, text=f"Number of Speakers: {len(speakersList)}", font=textFont).grid(row=4, column=0, columnspan=2, pady=10)


    errorLabel2 = tk.Label(timerSetupWindow, text="", font=textFont)
    errorLabel2.grid(row=5, column=0, columnspan=2, pady=5)


    btnFrame2 = tk.Frame(timerSetupWindow)
    btnFrame2.grid(row=6, column=0, columnspan=2, pady=20)


    tk.Button(btnFrame2, text="Start Timer", command=lambda: startSpeakerTimer(), font=textFont).grid(row=0, column=0, padx=10)
    tk.Button(btnFrame2, text="Return", command=lambda: [timerSetupWindow.destroy(), speakersListPage()], font=textFont).grid(row=0, column=1, padx=10)


    # validate time input and start the timer
    def startSpeakerTimer():
        minutes = minutesEntry.get()
        seconds = secondsEntry.get()


        if minutes == "" and seconds == "":
            errorLabel2.config(text="Please fill out speaking time")
            return


        totalMinutes = int(minutes) if minutes else 0
        totalSeconds = int(seconds) if seconds else 0


        if totalSeconds >= 60:
            errorLabel2.config(text="Seconds must be less than 60")
            return


        if totalMinutes == 0 and totalSeconds == 0:
            errorLabel2.config(text="Speaking time must be greater than 0")
            return


        totalTimeSeconds = totalMinutes * 60 + totalSeconds
        timerSetupWindow.destroy()
        runSpeakerTimer(totalTimeSeconds)


def runSpeakerTimer(speakingTime):
    # main timer window for tracking speaker time
    timerWindow = tk.Toplevel(window)
    initializeWindow(timerWindow, "Speaker Timer")
    timerWindow.grid_columnconfigure(0, weight=1)


    currentSpeakerIndex = 0
    timeLeft = speakingTime
    timerRunning = False


    # format time for display in minutes:seconds
    def formatTimerTime(seconds):
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"


    tk.Label(timerWindow, text="Speaker Timer", font=textFont).grid(row=0, column=0, pady=10)


    currentSpeakerLabel = tk.Label(timerWindow, text=f"Current Speaker: {speakersList[currentSpeakerIndex]}", font=textFont)
    currentSpeakerLabel.grid(row=1, column=0, pady=10)


    timeLabel = tk.Label(timerWindow, text=f"Time Left: {formatTimerTime(timeLeft)}", font=textFont)
    timeLabel.grid(row=2, column=0, pady=20)


    btnFrame3 = tk.Frame(timerWindow)
    btnFrame3.grid(row=3, column=0, pady=20)


    startBtn = tk.Button(btnFrame3, text="Start", command=lambda: startTimer(), font=textFont)
    startBtn.grid(row=0, column=0, padx=5)


    pauseBtn = tk.Button(btnFrame3, text="Pause", command=lambda: pauseTimer(), state="disabled", font=textFont)
    pauseBtn.grid(row=0, column=1, padx=5)


    nextBtn = tk.Button(btnFrame3, text="Next Speaker", command=lambda: nextSpeaker(), font=textFont)
    nextBtn.grid(row=0, column=2, padx=5)


    devoteBtn = tk.Button(btnFrame3, text="Devote Time", command=lambda: devoteTime(), font=textFont)
    devoteBtn.grid(row=0, column=3, padx=5)


    finishBtn = tk.Button(btnFrame3, text="Finish", command=lambda: speakersExhausted(), font=textFont)
    finishBtn.grid(row=0, column=4, padx=5)


    # updates timer display every second
    def updateTimer():
        nonlocal timeLeft
        if timerRunning and timeLeft > 0:
            timeLeft -= 1
            timeLabel.config(text=f"Time Left: {formatTimerTime(timeLeft)}")
            if timeLeft == 0:
                timeLabel.config(text="Time's Up!")
                pauseBtn.config(state="disabled")
                startBtn.config(state="disabled")
                devoteBtn.config(state="disabled")
            else:
                timerWindow.after(1000, updateTimer)


    # start the timer countdown
    def startTimer():
        nonlocal timerRunning
        timerRunning = True
        startBtn.config(state="disabled")
        pauseBtn.config(state="normal")
        updateTimer()


    # pause the timer
    def pauseTimer():
        nonlocal timerRunning
        timerRunning = False
        startBtn.config(state="normal")
        pauseBtn.config(state="disabled")


    # finish speakers list and save to history
    def speakersExhausted():
        global currentMotion
        global voteRes


        # add completed motion to history
        motionHistory.append([currentMotion, voteRes, f"{len(speakersList)} speakers", time.strftime("%d-%m-%Y at %H:%M"), formatTime(speakingTime)])


        timerWindow.destroy()
        motionsWindow.destroy()
        motionsPage()


    # allow speaker to devote remaining time to another speaker
    def devoteTime():
        pauseTimer()
        devoteTimeWindow = tk.Toplevel(window)
        initializeWindow(devoteTimeWindow, "Devote Time to Another Speaker")
        devoteTimeWindow.grid_columnconfigure(0, weight=1)


        tk.Label(devoteTimeWindow, text="Devote Time to Another Speaker", font=textFont).grid(row=0, column=0, pady=10)


        # show current speaker and remaining time
        currentSpeaker = speakersList[currentSpeakerIndex]
        tk.Label(devoteTimeWindow, text=f"Current Speaker: {currentSpeaker}", font=textFont).grid(row=1, column=0, pady=5)
        tk.Label(devoteTimeWindow, text=f"Remaining Time: {formatTimerTime(timeLeft)}", font=textFont).grid(row=2, column=0, pady=5)


        # create list of all speakers except the current one
        availableSpeakers = [speaker for speaker in speakersList if speaker != currentSpeaker]


        speakersDropdown = ttk.Combobox(devoteTimeWindow, values=availableSpeakers, state="readonly", font=textFont)
        speakersDropdown.grid(row=3, column=0, pady=10, sticky="ew", padx=20)
        speakersDropdown.set("Select Speaker to Devote Time to")


        errorLabel = tk.Label(devoteTimeWindow, text="", fg="red", font=textFont)
        errorLabel.grid(row=4, column=0, pady=5)


        # transfer time to selected speaker
        def devoteTimeToSpeaker():
            global speakerExtraTime
            nonlocal timeLeft
            selectedSpeaker = speakersDropdown.get()


            if selectedSpeaker == "Select Speaker to Devote Time to" or selectedSpeaker == "":
                errorLabel.config(text="Please select a speaker")
                return


            # store the time being devoted
            devotedTime = timeLeft


            # add the devoted time to the selected speaker's extra time
            if selectedSpeaker in speakerExtraTime:
                speakerExtraTime[selectedSpeaker] += devotedTime
            else:
                speakerExtraTime[selectedSpeaker] = devotedTime


            # find the selected speaker's index
            selectedIndex = speakersList.index(selectedSpeaker)


            # if the speaker has already spoken, add them to the end of the list
            if selectedIndex <= currentSpeakerIndex:
                speakersList.append(selectedSpeaker)


            # reset current speaker's time to 0
            timeLeft = 0
            timeLabel.config(text="Time Devoted - Click Next Speaker")


            # update button states
            startBtn.config(state="disabled")
            pauseBtn.config(state="disabled")


            devoteTimeWindow.destroy()
            nextSpeaker()


        btnFrame = tk.Frame(devoteTimeWindow)
        btnFrame.grid(row=5, column=0, pady=15)


        tk.Button(btnFrame, text="Devote Time", command=lambda: devoteTimeToSpeaker(), font=textFont).grid(row=0, column=0, padx=10)
        tk.Button(btnFrame, text="Cancel", command=lambda: [devoteTimeWindow.destroy(), startTimer() if timeLeft > 0 else None], font=textFont).grid(row=0, column=1, padx=10)


    # move to next speaker in queue
    def nextSpeaker():
        nonlocal currentSpeakerIndex, timeLeft, timerRunning
        global speakerExtraTime


        if currentSpeakerIndex < len(speakersList) - 1:
            currentSpeakerIndex += 1
            currentSpeaker = speakersList[currentSpeakerIndex]
            currentSpeakerLabel.config(text=f"Current Speaker: {currentSpeaker}")


            # calculate total time (base time + any extra time devoted to this speaker)
            extraTime = speakerExtraTime.get(currentSpeaker, 0)
            totalTime = speakingTime + extraTime
            timeLeft = totalTime


            # clear the extra time for this speaker since they're now speaking
            if currentSpeaker in speakerExtraTime:
                del speakerExtraTime[currentSpeaker]


            # show extra time if applicable
            if extraTime > 0:
                timeLabel.config(text=f"Time Left: {formatTimerTime(timeLeft)} (includes {formatTimerTime(extraTime)} extra)")
            else:
                timeLabel.config(text=f"Time Left: {formatTimerTime(timeLeft)}")


            timerRunning = False
            startBtn.config(state="normal")
            pauseBtn.config(state="disabled")
        else:
            # all speakers have finished
            currentSpeakerLabel.config(text="All speakers finished!")
            timeLabel.config(text="Session Complete")
            timerRunning = False
            startBtn.config(state="disabled")
            pauseBtn.config(state="disabled")
            nextBtn.config(state="disabled")
            devoteBtn.config(state="disabled")


# Conference History
def ConferenceHistory():
    historyWin = tk.Toplevel(window)
    initializeWindow(historyWin, "Conference History", 800, 400)


    # Sets up scrollable area vertically for window
    canvas, scrollableFrame, scrollbar = createScrollableArea(historyWin)


    # Create text widgets for displaying messages
    conferenceHistText = tk.Label(scrollableFrame, width=50, font=textFont)
    motionsText = tk.Label(scrollableFrame, width=50, font=textFont)


     # Initializes a table with field names and entries from a list
    # Initializes a table with field names and entries from a list
    def createTable(dataList, fieldNames, textWidget, noneText):
        if dataList:
            table = ttk.Treeview(scrollableFrame, columns=fieldNames, show='headings', height=len(dataList))


            # Format the columns
            for field in fieldNames:
                table.column(field, anchor=tk.W, width=150)
                table.heading(field, text=field, anchor=tk.W)


            # Configure alternating row colors
            table.tag_configure('oddrow', background='#E8E8E8')
            table.tag_configure('evenrow', background='#FFFFFF')


            # Insert all rows with alternating row colors
            for i, row in enumerate(dataList):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                table.insert('', 'end', values=row, tags=(tag,))


            # Pack Treeview to fill horizontally but height is fixed by height option (no vertical expansion)
            table.pack(fill=tk.X, padx=5, pady=5)
        else:
            # Show text when no data
            textWidget.config(text=noneText)
            textWidget.pack()


    # Edit motions history so that it shows only the motions name as well as the speakers list in a string format
    modifiedMotionHistory = []


    for item in motionHistory:
        # Extract motion value from dict
        motionValue = item[0].get('motion', '') if isinstance(item[0], dict) else item[0]


        # Keep other elements as is
        newItem = [
            motionValue,
            item[1],
            item[2],
            item[3],
            item[4]
        ]


        modifiedMotionHistory.append(newItem)


    tk.Label(scrollableFrame, text="Conference History:", font=textFont).pack()
    createTable(conferenceHistory, ['Action', 'Time'], conferenceHistText, "No actions have been recorded yet...")


    tk.Label(scrollableFrame, text="Motions History:", font=textFont).pack()
    createTable(modifiedMotionHistory, ['Motion', 'Majority', '# of Speakers', 'Time Created', 'Time per Speaker'], motionsText, "No motions have been recorded yet...")


window.protocol("WM_DELETE_WINDOW", quitApp)


tk.mainloop()
