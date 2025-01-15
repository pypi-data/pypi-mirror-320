import pandas as pd


# Load the dataset
data = pd.read_csv('src\data\MyeBooksComCleaned.csv')

class code02:
    # Filter the data
    def function02(data):
        f = data[data['column'] > 10]

        # Calculate the sum
        s = f['column'].sum()
        return f,s

    # Print the result
    print(f"Sum: {function02(data)}")