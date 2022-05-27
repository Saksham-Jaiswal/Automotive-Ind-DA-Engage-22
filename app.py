#importing class Flask from the flask library
from flask import Flask
#inorder to render html from your flask application we use function render_template
#to see the function definition select render_template, hold cmd key and then click on render_template and this is basically a general way to open any predefined fn or class 
from flask import render_template,redirect,url_for,request,flash
import pandas as pd
from pandas_profiling import ProfileReport
from flask_caching import Cache
from werkzeug.utils import secure_filename
import os

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}

# creating an instance/object named as 'app' of class Flask 
app = Flask(__name__)  
# tell Flask to use the above defined config
app.config.from_mapping(config)
cache = Cache(app)


#treating data
df=pd.read_csv("static/cars_engage_2022.csv")
df.drop(columns='Unnamed: 0',inplace=True)
l1=df.columns[df.isna().mean()>0.8].tolist()
df.drop(columns=l1,inplace=True)


#creating a route decorator, it is basically the pages you want to create for your website for each new page you will have to create a route i.e. a decorator
@app.route("/")
def hello_world():
    return render_template('index.html')

#render the data analysis report of the given sample dataset
@app.route("/Data Analysis Report")
def report():
    return render_template('Data Analysis Report.html')

#get the dataset from the user
@app.route('/Analyse My Dataset', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'csvfile' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['csvfile'] #here csvfile is the key whose value is the uploaded file on the webpage and we are storing that value to the variable file
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        if not os.path.isdir('static'):
            os.mkdir('static')
        file.save(os.path.join('static', filename))
        return redirect(url_for('analyse', name=filename))
    return render_template('Analyse My Dataset.html')

#analyse the dataset uploaded by the user
@app.route("/<name>")  
@cache.cached(timeout=100)
def analyse(name):
    df1=pd.read_csv(("static/"+name))
    l1=df1.columns[df1.isna().mean()>0.8].tolist()
    df1.drop(columns=l1,inplace=True)    
    profile=ProfileReport(df1,minimal=True, dark_mode=True)
    op_file="templates/"+name+".html"
    profile.to_file(output_file=op_file)
    return render_template(name+".html")

@app.route("/query",methods=["POST","GET"])  #this method here gets the values of multiple parameters from the client i.e. the webpage
def query():
    if(request.method=="POST"):
        p1=request.form["nm1"]  #here nm1 is the key and the value will be the input given by the user to the form
        p2=request.form["nm2"]
        p3=request.form["nm3"]
        return redirect(url_for("res",prm1=p1,prm2=p2,prm3=p3))
    return render_template("query.html")

@app.route("/<prm1>/<prm2>/<prm3>")  #here we operate upon those variables and reder the result on the webpage
def res(prm1,prm2,prm3):
    return render_template("automotiveDatasetJP.html")
    # if(prm3=="min"):
    #     m=df_new[prm2].min()
    # if(prm3=="max"):
    #     m=df_new[prm2].max()
    # if(prm3=="mean"):
    #     m=df_new[prm2].mean()
    


  


#following two lines are to command flask to run the application
if __name__=="__main__":
    app.secret_key = 'super secret key'
    app.run(debug=True)