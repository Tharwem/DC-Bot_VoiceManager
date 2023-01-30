from colorama import Fore
import datetime


def __timestamp() -> str:
    return Fore.BLACK+str(datetime.datetime.now())[:-7]


def __info() -> str:
    return Fore.BLUE+'INFO'


def __filename(filename: str) -> str:
    return Fore.MAGENTA+filename


def __data(data: str) -> str:
    return Fore.RED+data


def info(filename: str, data: str):
    print(f'{__timestamp()}{__info()}      {__filename(filename)} {__data(data)}')

