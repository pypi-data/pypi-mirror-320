import csv
from .core import BytesFrame

def read_csv(filepath, delimiter=","):
    """
    Read a CSV file and return a BytesFrame.
    """
    with open(filepath, 'r') as file:
        reader = csv.reader(file, delimiter=delimiter)
        header = next(reader)  # Get the column names (first row)
        data = {col: [] for col in header}
        
        for row in reader:
            for col, value in zip(header, row):
                data[col].append(value)
    
    return BytesFrame(data)
