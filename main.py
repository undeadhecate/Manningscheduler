from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello():
    return render_template('home.html')

@app.route('/AddUser')
def adduser():
    return render_template('AddUser.html')

@app.route('/CreateManning')
def createmanning():
    return render_template('CreateManning.html')

@app.route('/ManageDutyPost')
def AddDutyPost():
    return render_template('ManageDutyPost.html')

@app.route('/ManageManning')
def ManageManning():
    return render_template('ManageManning.html')

@app.route('/ViewManning')
def ViewManning():
    return render_template('ViewManning.html')

if __name__ == '__main__':

    app.run(debug=True, host='127.0.0.1', port=5000)
