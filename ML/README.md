### How to Run:
This ML model uses a virtul enviroment to store all the packages to better manage between different people:
- Install the most recent version of python (https://www.python.org/downloads/) along with pip 
- Install the venv package `pip install venv`
- To enter the virtual enviroment type the following:
    - MacOS/Linux: source ML-env/bin/activate 
    - Windows: ML-env\Scripts\activate.bat 
- Once in the environment, install the required packages: `python -m pip install -r requirements.txt`
- To leave the virtual environment, type `deactivate`

### References
- https://medium.com/pursuitnotes/support-vector-regression-in-6-steps-with-python-c4569acd062d
- https://towardsdatascience.com/radial-basis-function-rbf-kernel-the-go-to-kernel-acf0d22c798a
- https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVR.html