import numpy as np
from collections import Counter

def euclidean_distance(x1,x2):
    return np.sqrt(np.sum(x1-x2)**2)

class KNN:
    def __init__(self,k):
        self.k = k


    def scr_fit(self,X,y):
        self.X_train = X
        self.y_train = y


    def scr_predict(self,X):
        predictions= [self._predict(x) for x in X]
        return predictions

    
    def _predict(self,x):
        #compute distances
        distances = [euclidean_distance(x,x_train) for x_train in self.X_train]





        #get the k nearest labels
        #returns index of the k nearest labels from that we are taking the top 3 distances
        k_indices = np.argsort(distances)[:self.k]
        k_nearest_labels = [self.y_train[i] for i in k_indices]


        #majority vote, most common class label

        most_common = Counter(k_nearest_labels).most_common()
        return most_common[0][0] 





        #majority vote, most common class label