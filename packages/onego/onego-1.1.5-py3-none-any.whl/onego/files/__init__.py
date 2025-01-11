import os
import csv
import json
import pickle

def read(path: str, mode: str = 'r') -> str:
    if not os.path.isfile(path): return
    encoding = None if mode == 'rb' else 'utf-8'
    with open(path, mode, encoding=encoding) as file: return file.read()

def readJSON(path: str) -> dict:
    if not os.path.isfile(path): return
    with open(path, 'r', encoding='utf-8') as file: return json.load(file)

def readPickle(path: str):
    if not os.path.isfile(path): return
    with open(path, 'rb') as file: return pickle.load(file)

def readCSV(path: str):
    file = open(path, 'r', encoding='utf-8')
    reader = csv.reader(file)
    return reader, file

def write(path: str, data: str, mode: str = 'w') -> None:
    encoding = None if mode == 'wb' else 'utf-8'
    with open(path, mode, encoding=encoding) as file: return file.write(data)

def writeJSON(path: str, data: dict) -> None:
    with open(path, 'w', encoding='utf-8') as file: return json.dump(data, file)

def writePickle(path: str, data):
    with open(path, 'wb') as file: return pickle.dump(data, file)

def writeCSV(path: str, rows: list[list[str]]):
    with open(path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        for row in rows: writer.writerow(row)

def join(path: str, *paths: str): return os.path.join(path, *paths)
def makedirs(path: str): os.makedirs(path, exist_ok=True)
