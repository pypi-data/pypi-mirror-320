import numpy as np
from collections import Counter
class Node():
    def __init__(self, feature=None, threshold=None, left=None, right=None, gain=None, value=None):
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.gain = gain
        self.value = value

class DecisionTree():
    def __init__(self, min_samples=2, max_depth=2):
        self.min_samples = min_samples
        self.max_depth = max_depth

    def split_data(self, dataset, feature, threshold):
        left_dataset = []
        right_dataset = []
        
        # Loop over each row in the dataset and split based on the given feature and threshold
        for row in dataset:
            if row[feature] <= threshold:
                left_dataset.append(row)
            else:
                right_dataset.append(row)

        # Convert the left and right datasets to numpy arrays and return
        left_dataset = np.array(left_dataset)
        right_dataset = np.array(right_dataset)
        return left_dataset, right_dataset
    
    def entropy(self, y):
        entropy = 0
        labels = np.unique(y)
        for label in labels:
            label_examples = y[y == label]
            pl = len(label_examples) / len(y)      # IDENTIFY THE RATIO OF UNIQUE LABELS

            entropy += -pl * np.log2(pl)

        return entropy
    

    def information_gain(self, parent, left, right):
        
        information_gain = 0
        parent_entropy = self.entropy(parent)
        weight_left = len(left) / len(parent)
        weight_right= len(right) / len(parent)
        entropy_left, entropy_right = self.entropy(left), self.entropy(right)

        weighted_entropy = weight_left * entropy_left + weight_right * entropy_right
        information_gain = parent_entropy - weighted_entropy
        return information_gain
    

    def best_split(self, dataset, num_samples, num_features):
         # dictionary to store the best split values
        best_split = {'gain':- 1, 'feature': None, 'threshold': None}
        # loop over all the features
        for feature_index in range(num_features):
            #get the feature at the current feature_index
            feature_values = dataset[:, feature_index]
            #get unique values of that feature
            thresholds = np.unique(feature_values)
            # loop over all values of the feature
            for threshold in thresholds:
                # get left and right datasets
                left_dataset, right_dataset = self.split_data(dataset, feature_index, threshold)
                # check if either datasets is empty
                if len(left_dataset) and len(right_dataset):
                    # get y values of the parent and left, right nodes
                    y, left_y, right_y = dataset[:, -1], left_dataset[:, -1], right_dataset[:, -1]
                    information_gain = self.information_gain(y, left_y, right_y)
                    # update the best split if conditions are met
                    if information_gain > best_split["gain"]:
                        best_split["feature"] = feature_index
                        best_split["threshold"] = threshold
                        best_split["left_dataset"] = left_dataset
                        best_split["right_dataset"] = right_dataset
                        best_split["gain"] = information_gain
        return best_split
    
    def calculate_leaf_value(self, y):
    
        y = list(y)
        #get the highest present class in the array
        most_occuring_value = max(y, key=y.count)
        return most_occuring_value
    def build_tree(self, dataset, current_depth=0):
        
        # split the dataset into X, y values
        X, y = dataset[:, :-1], dataset[:, -1]
        n_samples, n_features = X.shape
        # keeps spliting until stopping conditions are met
        if n_samples >= self.min_samples and current_depth <= self.max_depth:
            # Get the best split
            best_split = self.best_split(dataset, n_samples, n_features)
            # Check if gain isn't zero
            if best_split["gain"]:
                # continue splitting the left and the right child. Increment current depth
                left_node = self.build_tree(best_split["left_dataset"], current_depth + 1)
                right_node = self.build_tree(best_split["right_dataset"], current_depth + 1)
                # return decision node
                return Node(best_split["feature"], best_split["threshold"],
                            left_node, right_node, best_split["gain"])

        # compute leaf node value
        leaf_value = self.calculate_leaf_value(y)
        # return leaf node value
        return Node(value=leaf_value)
    def fit(self, X, y):
        dataset = np.concatenate((X, y.reshape(-1, 1)), axis=1)  # Reshape y to 2D before concatenation

        # dataset = np.concatenate((X, y), axis=1)  
        self.root = self.build_tree(dataset)

        
    def predict(self, X):
       
        # Create an empty list to store the predictions
        predictions = []
        # For each instance in X, make a prediction by traversing the tree
        for x in X:
            prediction = self.make_prediction(x, self.root)
            # Append the prediction to the list of predictions
            predictions.append(prediction)
        # Convert the list to a numpy array and return it
        np.array(predictions)
        return predictions
    def make_prediction(self, x, node):
        # if the node has value i.e it's a leaf node extract it's value
        if node.value != None: 
            return node.value
        else:
            #if it's node a leaf node we'll get it's feature and traverse through the tree accordingly
            feature = x[node.feature]
            if feature <= node.threshold:
                return self.make_prediction(x, node.left)
            else:
                return self.make_prediction(x, node.right)
            
class RandomForest:
    def __init__(self, n_trees=10, min_samples=2, max_depth=2, max_features=None):
        self.n_trees = n_trees  # Number of trees in the forest
        self.min_samples = min_samples  # Minimum samples for splitting
        self.max_depth = max_depth  # Maximum depth of a tree
        self.max_features = max_features  # Number of features to sample for each split
        self.trees = []  # Store the trained trees

    def bootstrap_sample(self, X, y):
        """Create a bootstrap sample from the dataset."""
        n_samples = X.shape[0]
        indices = np.random.choice(n_samples, size=n_samples, replace=True)
        return X[indices], y[indices]

    def fit(self, X, y):
        """Train multiple decision trees on bootstrapped samples."""
        self.trees = []  # Clear any previously trained trees
        for _ in range(self.n_trees):
            # Create a bootstrap sample
            X_sample, y_sample = self.bootstrap_sample(X, y)
            
            # Train a decision tree on the bootstrap sample
            tree = DecisionTree(
                min_samples=self.min_samples, 
                max_depth=self.max_depth
            )
            tree.fit(X_sample, y_sample)
            self.trees.append(tree)

    def predict(self, X):
        """Aggregate predictions from all trees (majority voting)."""
        # Get predictions from each tree
        tree_predictions = np.array([tree.predict(X) for tree in self.trees])
        
        # Transpose to get predictions per sample
        tree_predictions = tree_predictions.T
        
        # Majority vote for classification
        predictions = [Counter(tree_preds).most_common(1)[0][0] for tree_preds in tree_predictions]
        return np.array(predictions)

            
    