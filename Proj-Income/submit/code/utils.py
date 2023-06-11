def make_dataset():
    import numpy as np
    def fillna(df):
        df[df == "?"] = np.nan
        for col in ["workclass", "occupation", "native.country"]:
            df.fillna(df[col].mode(0)[0], inplace=True)
        return df

    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn import preprocessing
    from sklearn.preprocessing import StandardScaler
    train_data = pd.read_csv("data/traindata.csv")
    train_label = pd.read_csv("data/trainlabel.txt", header=None, names=["income"])
    train_data = pd.concat([train_data, train_label], axis=1)
    train_data = fillna(train_data)

    X_test = pd.read_csv("data/testdata.csv")
    X_test = fillna(X_test)
    X = train_data.drop(["income"], axis=1)
    y = train_data["income"]

    features = X.columns
    global feature_names
    feature_names = features
    for feature in features:
        le = preprocessing.LabelEncoder()
        X[feature] = le.fit_transform(X[feature])
        X_test[feature] = le.fit_transform(X_test[feature])

    scaler = StandardScaler()
    X = pd.DataFrame(scaler.fit_transform(X), columns=features)
    X_test = pd.DataFrame(scaler.fit_transform(X_test), columns=features)

    return X, y, X_test

