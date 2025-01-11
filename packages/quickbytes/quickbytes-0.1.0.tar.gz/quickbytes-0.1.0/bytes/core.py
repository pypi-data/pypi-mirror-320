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
