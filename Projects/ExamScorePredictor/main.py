import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

def main():
    data = input("Enter the path to the CSV file containing exam scores: ")
    
    if not os.path.isfile(data):
        print("File not found. Please check the path and try again.")
        return
    
    df = pd.read_csv(data)
    print("Data Preview:")
    print(df.head())

    if 'Hours' not in df.columns or 'Scores' not in df.columns:
        print("CSV file must contain 'Hours' and 'Scores' columns.")
        return
    
    X = df[['Hours']]
    y = df['Scores']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"Model Performance:\nMean Squared Error: {mse}\nR^2 Score: {r2}")

    plt.scatter(X, y, color='blue')
    plt.plot(X, model.predict(X), color='red')
    plt.xlabel('Hours Studied')
    plt.ylabel('Scores')
    plt.title('Hours vs Scores')
    plt.show()
    
    hours = float(input("Enter number of hours studied to predict score: "))
    predicted_score = model.predict([[hours]])
    print(f"Predicted Score for studying {hours} hours: {predicted_score[0]}")
    