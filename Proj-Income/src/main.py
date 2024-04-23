from utils import make_dataset
import numpy as np
import pandas as pd

X, y, X_test = make_dataset()


def KNeighborsClassifier():
    from sklearn.neighbors import KNeighborsClassifier
    model = KNeighborsClassifier(n_neighbors=9).fit(X, y)
    y_pred = model.predict(X_test)
    return y_pred

def LogisticRegression():
    from sklearn.linear_model import LogisticRegression
    return LogisticRegression(C=1).fit(X, y).predict(X_test)

def DecisionTreeClassifier():
    from sklearn.tree import DecisionTreeClassifier
    return DecisionTreeClassifier(random_state=42, max_depth=6).fit(X, y).predict(X_test)

def GradientBoostingClassifier():
    from sklearn.ensemble import GradientBoostingClassifier
    model = GradientBoostingClassifier(n_estimators=200, max_depth=6, learning_rate=0.05, random_state=42)
    return model.fit(X, y).predict(X_test)

def MLPClassifier():
    from sklearn.neural_network import MLPClassifier
    model = MLPClassifier(max_iter=1000, alpha=0.1)
    return model.fit(X, y).predict(X_test)

if __name__ == "__main__":
    models = [KNeighborsClassifier, 
              LogisticRegression, 
              DecisionTreeClassifier, 
              GradientBoostingClassifier,
              MLPClassifier,
              ]
    for model in models:
        print(f"{model.__name__} is running...")
        y_pred = model()
        np.savetxt(f"pred/{model.__name__}.txt", y_pred, fmt="%d")
    
    y_pred = GradientBoostingClassifier()
    np.savetxt("testlabel.txt", y_pred, fmt="%d")