from sklearn.preprocessing import StandardScaler

class DataProcessor:
    def __init__(self):
        self.scaler = StandardScaler()

    def split_data(self, X, y, test_size=0.2, random_state=42):
        """
        Splits the dataset into training and testing sets.
        """
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        return X_train, X_test, y_train, y_test

    def scale_data(self, X_train, X_test):
        """
        Standardizes features by removing the mean and scaling to unit variance.
        """
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        return X_train_scaled, X_test_scaled
