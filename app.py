from flask import Flask
from flask import render_template,redirect,url_for,request,flash
import pandas as pd
from pandas_profiling import ProfileReport
from flask_caching import Cache
from werkzeug.utils import secure_filename
import os
from newsapi import NewsApiClient

config = {
    "DEBUG": True,         
    "CACHE_TYPE": "SimpleCache",  
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask(__name__)  
app.config.from_mapping(config)
cache = Cache(app)

@app.route("/",methods=["POST","GET"])
def query():
    if request.method=="POST":
        p1=request.form["nm1"]
        return redirect(url_for("res1",prm1=p1))
    return render_template('index.html')

@app.route("/<prm1>")  
def res1(prm1):
        return render_template("query_result.html",q=prm1)

#render the data analysis report of the given sample dataset
@app.route("/Data Analysis Report")
def report():
    return render_template('Data Analysis Report.html')

#get the dataset from the user
@app.route('/Analyse My Dataset', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'csvfile' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['csvfile'] 
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        if not os.path.isdir('static'):
            os.mkdir('static')
        file.save(os.path.join('static', filename))
        # return redirect(url_for('analyse', name=filename))
        df1=pd.read_csv(("static/"+filename))
        l1=df1.columns[df1.isna().mean()>0.8].tolist()
        df1.drop(columns=l1,inplace=True)    
        profile=ProfileReport(df1,minimal=True, dark_mode=True)
        op_file="templates/"+filename+".html"
        profile.to_file(output_file=op_file)
        return render_template(filename+".html")
    return render_template('Analyse My Dataset.html')


#trending page
@app.route('/trending')
def trending():
    newsapi = NewsApiClient(api_key="cf58ec497365431eab660fea88c66aa6")
    all_articles = newsapi.get_everything(q='+automotive',language='en',sort_by='popularity',page=1)
    articles = all_articles['articles']

    desc = []
    news = []
    img = []
    lnk=[]

    for i in range(len(articles)):
        myarticles = articles[i]

        news.append(myarticles['title'])
        desc.append(myarticles['description'])
        img.append(myarticles['urlToImage'])
        lnk.append(myarticles['url'])

    mylist = zip(news, desc, img,lnk)

    return render_template('trending.html', context=mylist)

if __name__=="__main__":
    app.secret_key = 'super secret key'
    app.run(debug=True)