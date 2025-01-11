import csv

class BytesFrame:
    def __init__(self, data):
        """
        Initialize the BytesFrame with a dictionary of lists.
        Example: data = {'name': ['Alice', 'Bob'], 'age': [25, 30]}
        """
        self.data = data  # Store the data as a dictionary of lists
        self.columns = list(data.keys())  # Get the list of columns
    
    def head(self, n=5):
        """
        Return the first n rows as a new BytesFrame.
        """
        result = {col: self.data[col][:n] for col in self.columns}
        return BytesFrame(result)

    def select(self, columns):
        """
        Select specific columns from the BytesFrame.
        Example: df.select(['name', 'age'])
        """
        if not all(col in self.columns for col in columns):
            raise ValueError("Some columns are not in the BytesFrame.")
        
        result = {col: self.data[col] for col in columns}
        return BytesFrame(result)

    def mean(self, column):
        """
        Compute the mean of a given column.
        """
        if column not in self.columns:
            raise ValueError(f"Column '{column}' not found.")
        
        values = [float(x) for x in self.data[column]]
        return sum(values) / len(values)
    
    def apply(self, func, column=None):
        """
        Apply a function to a specific column or all columns.
        Example:
            df.apply(lambda x: x.upper(), column='name')
        """
        if column:
            if column not in self.columns:
                raise ValueError(f"Column '{column}' not found.")
            self.data[column] = [func(x) for x in self.data[column]]
        else:
            for col in self.columns:
                self.data[col] = [func(x) for x in self.data[col]]
        return self

    def filter(self, func):
        """
        Filter rows based on a condition.
        Example:
            df.filter(lambda row: row['age'] > 25)
        """
        filtered_data = {col: [] for col in self.columns}
        for i in range(len(self.data[self.columns[0]])):
            row = {col: self.data[col][i] for col in self.columns}
            if func(row):
                for col in self.columns:
                    filtered_data[col].append(self.data[col][i])
        
        return BytesFrame(filtered_data)

    def groupby(self, column, agg_func):
        """
        Group the data by a column and apply an aggregation function.
        Example:
            df.groupby('age', lambda group: len(group))
        """
        if column not in self.columns:
            raise ValueError(f"Column '{column}' not found.")
        
        grouped_data = {}
        for value in set(self.data[column]):
            group_indices = [i for i, x in enumerate(self.data[column]) if x == value]
            group = {col: [self.data[col][i] for i in group_indices] for col in self.columns}
            grouped_data[value] = agg_func(BytesFrame(group))
        
        return grouped_data

    def sort(self, column, ascending=True):
        """
        Sort the BytesFrame by a specific column.
        Example:
            df.sort('age', ascending=False)
        """
        if column not in self.columns:
            raise ValueError(f"Column '{column}' not found.")
        
        sorted_indices = sorted(range(len(self.data[column])), key=lambda i: self.data[column][i], reverse=not ascending)
        sorted_data = {col: [self.data[col][i] for i in sorted_indices] for col in self.columns}
        
        return BytesFrame(sorted_data)

    def to_csv(self, filepath, delimiter=","):
        """
        Export the BytesFrame data to a CSV file.
        
        Parameters:
        - filepath: Path to the output CSV file.
        - delimiter: Delimiter to use in the CSV file (default is ',').
        """
        with open(filepath, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=delimiter)
            
            # Write the header (column names)
            writer.writerow(self.columns)
            
            # Write the rows
            num_rows = len(next(iter(self.data.values())))
            for i in range(num_rows):
                row = [self.data[col][i] for col in self.columns]
                writer.writerow(row)

    def fillna(self, value, column=None):
        """
        Fill missing (None or empty) values with a given value.
        If column is None, fill missing values in all columns.
        """
        if column:
            self.data[column] = [value if x in (None, "") else x for x in self.data[column]]
        else:
            for col in self.columns:
                self.data[col] = [value if x in (None, "") else x for x in self.data[col]]
        return self

    def describe(self):
        """
        Provide summary statistics for numeric columns.
        """
        description = {}
        for col in self.columns:
            try:
                values = [float(x) for x in self.data[col]]
                description[col] = {
                    'count': len(values),
                    'mean': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                }
            except ValueError:
                continue  # Skip non-numeric columns
        
        return description

    def pivot(self, index, columns, values, agg_func):
        """
        Create a pivot table.
        Example:
            df.pivot(index='name', columns='age', values='score', agg_func=sum)
        """
        if index not in self.columns or columns not in self.columns or values not in self.columns:
            raise ValueError("Invalid columns specified.")
        
        pivot_data = {}
        unique_index = set(self.data[index])
        unique_columns = set(self.data[columns])
        
        for i in unique_index:
            pivot_data[i] = {}
            for j in unique_columns:
                cell_values = [self.data[values][k] for k in range(len(self.data[index]))
                               if self.data[index][k] == i and self.data[columns][k] == j]
                pivot_data[i][j] = agg_func(cell_values) if cell_values else None
        
        return pivot_data

    def show(self, n=None):
        if n is None:
            n = len(next(iter(self.data.values())))
        print(" | ".join(self.columns))
        print("-" * (len(self.columns) * 10))
        for i in range(n):
            row = [str(self.data[col][i]) for col in self.columns]
            print(" | ".join(row))

