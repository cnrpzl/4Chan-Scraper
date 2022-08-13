from genericpath import isfile
import shutil
import requests
from bs4 import BeautifulSoup
import os.path, os
import time
import configparser 


s = requests.session()

def setupConfig():
    threadLink = input('Please input thread link: ')
    folderName = input('Please input folder name: ')
    monitorMode = input('Monitor thread? (Y/N): ')
    config = configparser.ConfigParser()
    config['SETTINGS'] = {'ThreadLink': threadLink,
    "MonitorMode": monitorMode,
    "FolderName": folderName}
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)
    return True

def loadConfig():
    if os.path.isfile('./settings.ini') != True:
        setupConfig()
        newSetup = True
    else:
        newSetup = False
    if newSetup != True:
        lastConfig = input('Use previous settings? (Y/N): ')
        if lastConfig.upper() == "N":
            setupConfig()
        else:
            print("Using last known settings...")

    config = configparser.ConfigParser()
    config.sections()
    config.read('settings.ini')
    threadNumber = config['SETTINGS']["ThreadLink"]
    monitorMode = config['SETTINGS']['MonitorMode']
    folderName = config['SETTINGS']['FolderName']
    while threadNumber == '' or monitorMode == '' or folderName == '':
        print("Invalid config, starting setup...")
        setupConfig()
        config.read('settings.ini')
        threadNumber = config['SETTINGS']["ThreadLink"]
        monitorMode = config['SETTINGS']['MonitorMode']
        folderName = config['SETTINGS']['FolderName']
    checkFolderPath(folderName)

    return threadNumber, monitorMode, folderName

def checkFolderPath(folderName):
    imageFolderPath = f'./{folderName}/'

    if os.path.isdir(imageFolderPath) != True:
        print(f'Creating new directory at {imageFolderPath}')
        os.mkdir(imageFolderPath)
    else:
        print('Storing images in previously created folder')

def getImageLinksFromThread(threadLink):
    try:
        thread = s.get(threadLink).text
    except Exception as e:
        print(e)
        return False
        
    imageLinks = []
    soup = BeautifulSoup(thread, "html.parser")
    imageElements = soup.find_all('a', class_="fileThumb")

    for link in imageElements:
        if link.has_attr('href'):
            imageLinks.append("https:" + link['href'])

    return imageLinks

def downloadImage(folder, imageLink):
    fileName = imageLink.split("/")[-1]
    if checkDuplicate(folder, fileName) != True:
        response = requests.get(imageLink, stream=True)
        with open(f'./{folder}/{fileName}', 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        print(f"{fileName} succesfully downloaded.")
    else:
        print(f'{fileName} already exists, skipping.')

def checkDuplicate(folderName, fileName):
    if os.path.isfile(f'./{folderName}/{fileName}') == True:
        return True
    else:
        return False

thread, monitor, folder = loadConfig()
if monitor.upper() == "Y":
    print("Monitor mode started. Refreshing every 180 seconds.")
    while True:
        imageLinks = getImageLinksFromThread(thread)
        for image in imageLinks:
            downloadImage(folder, image)
        print("Sleeping for 180 seconds.")
        time.sleep(180)
else:
    print("Regular mode started.")
    imageLinks = getImageLinksFromThread(thread)
    for image in imageLinks:
        downloadImage(folder, image)
