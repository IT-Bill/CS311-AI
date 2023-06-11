# Adult Census Income

## Installation
Provide step-by-step instructions on how to set up the environment for running your code. Include any necessary dependencies that need to be installed.

1. Navigate to the project directory:
   ```bash
   cd 12110817_张展玮
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## File Structure

```bash
12110817_张展玮
│  README.md
│  requirements.txt
│  tree.txt
│  
├─code
│     main.py
│     test_note.ipynb
│     utils.py
│     __init__.py
│          
├─data
│      testdata.csv
│      traindata.csv
│      trainlabel.txt
│      
└─pred  # Predictions are stored here.
        DecisionTreeClassifier.txt
        GradientBoostingClassifier.txt
        KNeighborsClassifier.txt
        LogisticRegression.txt
        MLPClassifier.txt
```

## Usage

Explain how to run your code and provide any necessary instructions or command line arguments.

1. Navigate to the project directory:
   ```bash
   cd 12110817_张展玮
   ```

2. Run the code:
   ```bash
   python code/main.py
   
   # info
   KNeighborsClassifier is running...
   LogisticRegression is running...
   DecisionTreeClassifier is running...
   GradientBoostingClassifier is running...
   MLPClassifier is running...
   ```

