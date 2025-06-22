# MACSima Parser

**MACSima Parser** helps you turn experiment data from a MACSima imaging run (in `.json` format) into a clear Excel file you can open in Excel, Google Sheets, or similar tools.
You do not need to know Python to use this tool!

---

## 1. Setup

### 1.1 Install Python (if you don’t have it)

* **Windows/macOS:** Download and install Python 3.10 from [python.org/downloads](https://www.python.org/downloads/release/python-3100/).

  * During install, make sure to check the box **“Add Python to PATH”**.
* **Linux:** Usually Python 3 is already installed.
* You can check if Python is installed by typing `python3 --version` in Terminal.

### 1.2 Install Miniconda (if you don’t have it)

We recommend using Miniconda for managing Python versions and dependencies in a virtual environment. Download and install Miniconda from [[Miniconda installers](https://docs.conda.io/en/latest/miniconda.html)](https://www.anaconda.com/docs/getting-started/miniconda/install)

NOTE: make sure conda is added to your PATH. Ignore warning message in installer.

### 1.3 Create a virtual environment using Miniconda 

**Once Miniconda is installed**, create your virtual environment.

```sh
conda create -n macsima python=3.10
```
This will prompt you to type y (yes) to proceed.
### 1.4 Activate your virtual environment

```sh
conda activate macsima
```

You’ll see your terminal prompt change to show `(macsima)` at the start, which means the environment is active.
Link to tutorial for more info e.g. how to see active env

---

### 1.5 Install dependencies

With your environment activated, install the required libraries:

```sh
pip install pandas xlsxwriter
```

### 1.6 Download this code

Click the green **“Code”** button (top right) and select **Download ZIP**.
Unzip it to a folder of your choice.

---

## 2. Run the parser

### 2.1 Open a Terminal / Command Prompt

* **Windows:** Open “Anaconda Prompt” (if you have Anaconda/Miniconda), or just “Command Prompt”.
* **macOS:** Open Terminal.
* **Linux:** Open your favorite Terminal.

---

### 2.2 Prepare your data

Copy your `.json` MACSima file to the same folder as this script, or note its path.

### 2.3 Run the code

In Terminal/Command Prompt, run:

```sh
python src/macsima_parser.py path_to_your_file.json
```

If you forget the file path, the program will **ask you to enter it**.

**Output**
A new Excel file (with the same name as your JSON file, but ending with `.xlsx`) will be created in the same folder.

Open it in Excel, Google Sheets, or similar!

---

## Run Tests (Optional)

If you want to make sure the parser works correctly, you can run:

```sh
pytest src/test_macsima_parser.py
```

---

## Troubleshooting

* **“python: command not found”**
  Make sure you installed Python and followed step 1.
* **“No module named pandas” or similar**
  Make sure you ran the `pip install pandas xlsxwriter` command with your environment activated.
* **Excel file not created**
  Double-check that your input JSON file is correct and in the right location.
* **Any errors?**
  Please copy the error message and open an [issue](#).

---

## About

Developed by Lauren Cassidy.
This script is open-source. Improvements are welcome!

---
