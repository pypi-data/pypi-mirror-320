# Importing libraries
import os
import shutil
import csv
import subprocess
import sys

def install_package(package_name):
    try:
        # Try to import the package
        __import__(package_name)
        print(f"'{package_name}' is already installed.")
    except ImportError:
        # If the package is not installed, install it
        print(f"'{package_name}' is not installed. Installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

# Install pandas
install_package("pandas")

# import pandas
import pandas as pd
from pathlib import Path
import getpass

#print("Pandas installed and imported successfully!")


def navigate_to_desktop():
    # Get the path
    cwd = os.getcwd()
    print(f"Path: {cwd}")

    # Check for Desktop folder
    parts = cwd.split(os.sep)  
    if "Desktop" in parts:
        desktop_index = parts.index("Desktop")
        desktop_path = os.sep.join(parts[:desktop_index + 1])
    else:
        # Create  Desktop folder
        potential_desktop = os.path.join(cwd, "Desktop")
        if os.path.exists(potential_desktop):
            desktop_path = potential_desktop
        else:
            print("Desktop not found.")
            return None

    # Move to Desktop folder
    try:
        os.chdir(desktop_path)
        print(f"Moving into the Desktop folder: {os.getcwd()}")
        return os.getcwd()  
    except Exception as e:
        print(f"Error occured: {e}")
        return None

def organizefiles():
    
    # Get path for Desktop folder
    desktop_path = navigate_to_desktop()

   # Moving into Desktop folder
    os.chdir(desktop_path)


    # Reorder the files in alphabetic order
    file_list = os.listdir()
    file_list.sort()

    docs = ['.txt', '.odt' ]
    images = ['.jpg', '.png', '.jpeg']
    audio = ['.mp3']

    # Open the CSV file to record the files I move
    with open('recap.csv', 'a') as csvfile:
        
    # For loop to iterate through the elements in the 'files' folder
        for file in file_list:
            
    # Separating the name and extension for each file
            name, ext = os.path.splitext(file)
        
    # Gathering necessary information using os.stat
            stats = os.stat(file)
            if ext in docs:
                types = 'docs'
            elif ext in audio:
                types = 'audio'
            elif ext in images:
                types = 'images'
            else:
                types = 'extension not supported'
    # Output
            print(f"{name} type: {types} size: {stats.st_size}B")


            if os.path.isdir(name):
                continue
        
            if f"{name}" == "recap":
                continue

            csvfile.write(f"{name},{types},{stats.st_size}(B)\n")
            

    # Creating subfolders if they don't exist
            for directory in ['audio', 'docs', 'images']:
                if not os.path.exists(directory):
                    os.mkdir(directory)

    # Moving the files in their subfolders
            if types in ['audio', 'docs', 'images']:
                shutil.move(file, types)

            
    file_name = pd.read_csv('recap.csv')

    headerList = ['name', 'type', 'size']

    # Convert the DataFrame to a CSV file
    file_name.to_csv("recap.csv", header=headerList, index=False)


organizefiles()
if __name__ == "__main__":
    print('Ready to organize your Desktop...')
    organizefiles()
