import csv
import json

class LogParser:
    @staticmethod
    def parse_csv(file_path):
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            return [row for row in reader]

    @staticmethod
    def parse_json(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def parse_txt(file_path):
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines()]
