# MACSima Parser

**MACSima Parser** helps you turn experiment data from a MACSima imaging run (in `.json` format) into a clear Excel file you can open in Excel, Google Sheets, or similar tools.
You do **not** need to know Python to use this tool!

---

## Quick Start (No Python Experience Needed)

### 1. Install Python (if you don’t have it)

* **Windows/macOS:** Download and install Python 3.10 from [python.org/downloads](https://www.python.org/downloads/release/python-3100/).

  * During install, make sure to check the box **“Add Python to PATH”**.
* **Linux:** Usually Python 3 is already installed.
* You can check if Pythin is installed by typing `python3 --version` in Terminal.

### 2. Download this code

Click the green **“Code”** button (top right) and select **Download ZIP**.
Unzip it to a folder of your choice.

---

### 3. Open a Terminal / Command Prompt

* **Windows:** Open “Anaconda Prompt” (if you have Anaconda/Miniconda), or just “Command Prompt”.
* **macOS:** Open Terminal (search for it in Spotlight).
* **Linux:** Open your favorite Terminal.

---

### 4. Create an isolated Python environment (recommended)

**If you use Anaconda/Miniconda (recommended for beginners):**

```sh
conda create -n macsima python=3.10
conda activate macsima
```

**If you do not use Anaconda:**

```sh
python3 -m venv macsima_env
```

Activate it:

* **Windows:** `macsima_env\Scripts\activate`
* **macOS/Linux:** `source macsima_env/bin/activate`

---

### 5. Install dependencies

With your environment activated, install the required libraries:

```sh
pip install pandas xlsxwriter
```

---

### 6. Run the parser

Copy your `.json` MACSima file to the same folder as this script, or note its path.

In Terminal/Command Prompt, run:

```sh
python src/macsima_parser.py path_to_your_file.json
```

If you forget the file path, the program will **ask you to enter it**.

**What you’ll get:**
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
