import numpy as np
from collections import Counter
from .decision_tree import My_DecisionTree


class My_Random_Forest():
    

    def __init__(self,n_trees=100,min_samples_split=2,max_depth=100,n_features=None):
        self.n_tress = n_trees
        self.min_samples_split =min_samples_split
        self.max_depth = max_depth
        self.n_features = n_features
        self.trees = []


    def fit(self,X,y):
        self.trees = [My_DecisionTree(min_samples_split=self.min_samples_split,max_depth=self.max_depth,n_features=self.n_features) for _ in range(self.n_tress)]
        for tree in self.trees:
            X_sample,y_sample = self.take_random_sample(X,y)
            tree.fit(X_sample,y_sample)


    def take_random_sample(self,X,y):
        n_samples = X.shape[0]
        random_indices = np.random.choice(n_samples,n_samples,replace=True)
        return X[random_indices],y[random_indices]
    

    def predict(self,X):
        tree_predictions = np.array([tree.predict(X) for tree in self.trees])
        #tree predictions for each [[predictions from 1st tress for all samples] [predictions from second tree for all samples]... ]
        tree_predictions =  tree_predictions.T  
        #make it to [[prediction for sample 1 from all trees], [prediction for sample 2 from all trees,....]]
        y_pred = [self._most_common_label(tree_prediction) for tree_prediction in tree_predictions]
        return np.array(y_pred)
    

    def _most_common_label(self,y):
        return Counter(y).most_common(1)[0][0]  
        #returns the most common occurence from a list of predictions for each sample 