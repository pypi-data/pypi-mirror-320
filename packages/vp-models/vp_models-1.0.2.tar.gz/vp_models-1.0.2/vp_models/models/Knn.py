
import numpy as np


class Knn_():
  
  def __init__(self, n_neighbors=3):
      self.n_neighbors = n_neighbors

  def euclidean_distance(self, x1, x2):
      return np.linalg.norm(x1 - x2)

  def fit(self, X_train, y_train):
      self.X_train = X_train
      self.y_train = y_train
      

  def predict(self, X):
      predictions = []

      for x in X:
            prediction = self._predict(x)
            predictions.append(prediction)
      return np.array(predictions)
  
  def _predict(self, x):
      distances = []

      for x_train in self.X_train:
          distance = self.euclidean_distance(x, x_train)
          distances.append(distance)
          
      distances = np.array(distances)


      n_neighbors_idxs = np.argsort(distances)[: self.n_neighbors]


      labels = self.y_train[n_neighbors_idxs]
      labels = list(labels)

      most_occuring_value = max(labels, key=labels.count)
      return most_occuring_value
  
