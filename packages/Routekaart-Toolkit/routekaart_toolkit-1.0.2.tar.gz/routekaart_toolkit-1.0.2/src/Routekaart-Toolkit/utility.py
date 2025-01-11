import os
from shutil import rmtree


def create_empty_folder(path:str):
    if os.path.exists(path):
        rmtree(path)
    os.mkdir(path)


def proceedConfirmation(force:bool):
    if force: return
    if input('Do you want to procceed? [Y/N] ').upper() != 'Y': exit()