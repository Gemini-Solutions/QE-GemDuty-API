# NextGen
NextGen is a Python-based AI powered application capable of generating UI, API and Performance test cases for web applications. This application generates locator and feature files, automates the execution scripts for the users to reduce the manual intervention.

## Steps to run the application for the first time:
### 1. Check Python is installed
Make sure that python3 is installed on your system by running command
```bash
python --version
```
![image](https://github.com/user-attachments/assets/6e4d36d4-c463-46fa-bc71-0897107fae89)

If the command does not return the Python version, install it from SelfService Portal, python official website or reach out to the IT team.
![image](https://github.com/user-attachments/assets/b3618f7b-ac3f-490e-b60e-378444dc53f7)

### 2. Check you have a Python IDE
Our suggestion is to use Visual Studio Code IDE. Check if you can download it from SelfService Portal. If not, download it using this [link](https://code.visualstudio.com/download).

If you get **Unverified download blocker** error (refer to the image below)
![image](https://github.com/user-attachments/assets/1a5739b7-d8d1-4e36-a502-271c627f43f1)

Open the undownloaded file and click on **Download unverified file** to continue (refer to the image below)
![image](https://github.com/user-attachments/assets/ea48b7ce-5bc8-4ca5-821d-9ea32645dd3a)

Optional: After Visual Code is installed, install necessary extensions as per your requirements.

### 3. Create virtual environment by running the command:
```bash
python -m venv <name-of your-virtual-environment>
```
**Note:** If you get **UnauthorizedAccessError** given in the screenshot below, use the command given below to get rid of this error.
![image](https://github.com/user-attachments/assets/37c72891-4640-4a37-bec3-ae59e8c5aad7)

<img width="800" alt="image" src="https://github.com/user-attachments/assets/4fbd43a2-5fb2-4a4a-9704-6612bf63bd07">

### 3. Install extensions that will support you while working on Python in VS Code.
### 4. Create a .env file and add a secret key there. Please ask for the secret key values in DM.
```bash
Set-ExecutionPolicy Unrestricted -Scope CurrentUser
```
![image](https://github.com/user-attachments/assets/a3e157a1-48ff-4363-919d-8bff820a83c6)

(You may get this error if using powershell  terminal. For cmd terminal, this error usually do not appear)

### 4. Activate virtual environment by running the command:
```bash
.\venv\Scripts\activate
```
**Note:** Never install any dependency without activating the virtual environment

### 5. Install required depdendencies by using the command:
```bash
pip install -r requirements.txt
```
**Note:** If you get error given below while installing the dependencies, follow the steps given below:
![image](https://github.com/user-attachments/assets/89f42b4c-6dc0-49d3-8df4-8c037f94fce4)

Step 1: Open requirements.txt file and remove the **multidict** dependency
Step 2: Install multidict dependency indendently by running the command:
```bash
pip install multidict
```
Step 3: Add the multidict dependency to requirements.txt file by runn ing the command:
```bash
pip freeze > requirements.txt
```

### 6. Create a .env file
Copy `.env.example` file keys to `.env` file and ask for its values.

### 7. Provide login method if your application has a authentication layer
Connect with the team for this step.

### 8. Activate the streamlit app to launch the application by running the command:
```bash
python -m streamlit run main.py
```

## Note for the contributers:
1. `main` branch will be used by users to test their applications. New features will be added to the main branch after every release
2. All development will be done in the develop branch. Always take a fresh pull of develop branch to work and have a peer review of your feature before merging/raising the PR
3. For demo purpose, a branch can be cut from the develop branch
4. If any new dependency is added, make sure to add that dependency in `requirements.txt` file
5. Your commit should be self descriptive. Use the template given below for commit messages:
Summary of the feature(s) going in the PR
(a line gap)
Explaining the features (optional)
