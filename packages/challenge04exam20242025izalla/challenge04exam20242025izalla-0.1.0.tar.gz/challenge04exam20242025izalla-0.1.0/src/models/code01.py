import pandas as pd


class code01:
    # Load the dataset
    df = pd.read_csv('src\data\MyeBooksComCleaned.csv')

    # Calculate mean and median of a column
    def function01(df):
        mean_value = df['column'].mean()
        median_value = df['column'].median()
        return mean_value, median_value

    # Print the results
    print(f"{function01(df)}")
