from flask import Flask, render_template, request
app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=False)

def addition(num1, num2):
    operationResult = float(num1) + float(num2)
    return operationResult

def subtraction(num1, num2):
    operationResult = float(num1) - float(num2)
    return operationResult

def multiplication(num1, num2):

    operationResult = float(num1) * float(num2)
    return operationResult 

def division(num1, num2):
    #operationResult = float(num1) / float(num2)
    try:
        operationResult = float(num1) / float(num2)
    except ZeroDivisionError:
        operationResult = "cannot divide by zero"
    return operationResult 

@app.route('/')
def calcyoulater_index():
    return render_template('index.html')

@app.route('/<string:page_name>')
def html_page(page_name):
    return render_template(page_name)

@app.route("/addition", methods=['POST'])
def getAddition():
    num1 = request.form['number1']
    num2 = request.form['number2']  
    getOperationResult = addition(num1, num2)
    return render_template('add.html', result=getOperationResult)

@app.route("/subtraction", methods=['POST'])
def getSubtraction():
    num1 = request.form['number1']
    num2 = request.form['number2']  
    getOperationResult = subtraction(num1, num2)
    return render_template('subtract.html', result=getOperationResult)

@app.route("/multiplication", methods=['POST'])
def getMultiplication():
    num1 = request.form['number1']
    num2 = request.form['number2']
    getOperationResult = multiplication(num1, num2)
    return render_template('multiply.html', result=getOperationResult)

@app.route("/division", methods=['POST'])
def getDivision():
    num1 = request.form['number1']
    num2 = request.form['number2']
    getOperationResult = division(num1, num2)
    return render_template('divide.html', result=getOperationResult)
