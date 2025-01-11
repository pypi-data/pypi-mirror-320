
# Xander-AI

Xander-AI is a Python package designed to handle classification, regression, text, and image-related tasks with minimal setup and maximum efficiency.

## Installation

```bash
pip install xander-ai
```

---

## Usage

### General Instructions
- **Supported Tasks**: `regression`, `classification`, `text`, and `image`.
- **Target Column (`target_col`)**:
  - Required for `regression`, `classification`, and `text` tasks.
  - Not required for the `image` task.
- **Hyperparameters**:
  - Accepts a dictionary where the key `epochs` is used to define the number of training epochs.

---

### Task-Specific Details

#### **Image Task**
- **Dataset Format**:
  - Provide a `.zip` file containing a folder.
  - Inside the folder:
    - Subfolders represent class labels.
    - Images within subfolders correspond to their class.

##### Example Directory Structure:
```
dataset.zip
│
├── class_1/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
│
├── class_2/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
│
└── class_n/
    ├── image1.jpg
    ├── image2.jpg
    └── ...
```

##### Example Code for Image Task:
```python
from xander_ai import Xander

# Hyperparameters for training
hyperparameters = {
    "epochs": 10,
}

# Initialize the Xander model for image task
xander = Xander(
    dataset_path='path_to_your_dataset.zip',  # Provide path to zip file
    model_name="v1",  # You can change the model name as required
    hyperparameters=hyperparameters,  # Provide hyperparameters
    task="image"  # Specify task as 'image'
)

# Train the model
xander.train()
```

---

#### **Regression Task**
- **Dataset Format**:
  - The dataset should have a target column specified using `target_col`.
  - Ensure that the dataset is in a `.csv` or `.xlsx` format.

##### Example Code for Regression Task:
```python
from xander_ai import Xander

# Hyperparameters for training
hyperparameters = {
    "epochs": 20,
}

# Initialize the Xander model for regression task
xander = Xander(
    dataset_path='path_to_your_dataset.csv',  # Provide path to your dataset
    model_name="v1",  # Model version or name
    hyperparameters=hyperparameters,  # Hyperparameters dictionary
    target_col="target",  # Name of the target column
    task="regression"  # Specify task as 'regression'
)

# Train the model
xander.train()
```

---

#### **Classification Task**
- **Dataset Format**:
  - The dataset should have a target column specified using `target_col`.
  - The dataset should be in a `.csv` or `.xlsx` format.

##### Example Code for Classification Task:
```python
from xander_ai import Xander

# Hyperparameters for training
hyperparameters = {
    "epochs": 15,
}

# Initialize the Xander model for classification task
xander = Xander(
    dataset_path='path_to_your_dataset.csv',  # Provide path to your dataset
    model_name="v1",  # Model version or name
    hyperparameters=hyperparameters,  # Hyperparameters dictionary
    target_col="target",  # Name of the target column
    task="classification"  # Specify task as 'classification'
)

# Train the model
xander.train()
```

---

#### **Text Task**
- **Dataset Format**:
  - The dataset should have a target column specified using `target_col`.
  - The dataset should be in a `.csv` or `.xlsx` format.

##### Example Code for Text Task:
```python
from xander_ai import Xander

# Hyperparameters for training
hyperparameters = {
    "epochs": 25,
}

# Initialize the Xander model for text task
xander = Xander(
    dataset_path='path_to_your_text_dataset.csv',  # Provide path to your dataset
    model_name="v1",  # Model version or name
    hyperparameters=hyperparameters,  # Hyperparameters dictionary
    target_col="text_target",  # Name of the target column
    task="text"  # Specify task as 'text'
)

# Train the model
xander.train()
```

---

## License

MIT License