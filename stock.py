import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, session, request, logging
import requests
import json
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
#from passlib.hash import sha256_crypt
from functools import wraps
import os
from datetime import datetime
import pandas as pd
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from flask_jsglue import JSGlue

APIKEY="QV3BDKS6QV2DCOUJ"
APIfunction="TIME_SERIES_INTRADAY"
APIinterval="1min"

persondata=[{
"name":"SNAP" ,   
"basePrice":11
},
{
"name":"AAPL",    
"basePrice":250
},
{
"name":"TWTR" ,   
"basePrice":25
},
{
"name":"TSLA" ,   
"basePrice":500
},
{
"name":"NFLX" ,   
"basePrice":375
},
{
"name":"FB" ,   
"basePrice":160
},
{
"name":"MSFT",    
"basePrice":150
},
{
"name":"MSFTT",    
"basePrice":100
}
]

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'csv'}

def appending_files(filepath):
    f=open("sampledata.txt","r")
    filedata=json.loads(f.read())
    addeddatadf=pd.read_csv(filepath,engine='python')
    addeddatadf = addeddatadf[addeddatadf['name'].notna()]
    addeddatadf = addeddatadf[addeddatadf['basePrice'].notna()]
    addeddatadf= addeddatadf.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    addeddatadf['name'] = addeddatadf['name'].str.upper()
    print(addeddatadf['name'])
    aadeddfjson=addeddatadf.to_json(orient='records')
    print(filedata)
    print(type(aadeddfjson))
    print(type(json.loads(aadeddfjson)))
    print(type(filedata))
    print(aadeddfjson)
    total=filedata+json.loads(aadeddfjson)
    total = [i for n, i in enumerate(total) if i not in total[n + 1:]]
    with open('sampledata.txt', 'w') as f:
        json.dump(total, f)
    

app =Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
JSGlue(app)

@app.route('/home')
def test():
    return "home"  
   

@app.route("/upload_bulk_records", methods=["GET", "POST"])
def upload_image():
    if request.method=="POST" or request.method=="GET":
        print(request.method)
        if 'file' not in request.files:
            return render_template("upload_records.html",message="No file")
        file=request.files["file"]
        if file.filename == '':
            return render_template("upload_records.html",message="No file selected")
        if file and allowed_file(file.filename):
            file.save(os.path.join("uploads",file.filename))  
            print("hereeeeee")
            print(file.filename)
            uploadedfile_path=os.path.join("uploads",file.filename)
            print(uploadedfile_path)
            addeddatadf=pd.read_csv(uploadedfile_path,engine='python')
            if ('name' in addeddatadf) and ('basePrice' in addeddatadf):
                appending_files(uploadedfile_path)
                return render_template("upload_records.html", message="Successfully Uploaded")
            else:
                return render_template("upload_records.html", message="Upload the CSV files with the column names 'name' and 'basePrice'")    
        else:
            return render_template("upload_records.html", message="Upload CSV extension file")

@app.route('/delete_records',methods=['POST'])
def delete_records():
    #deldata=request.get_json()
    deldata=[{"name":request.args.get('name'),"basePrice":float(request.args.get('baseprice'))}]
    f=open("sampledata.txt","r")
    filedata=json.loads(f.read())
    print("filedata")
    print(filedata)
    print("deldata")
    print(deldata)
    for i in range(len(deldata)):
        deldata[i]['name']=deldata[i]['name'].replace(' ', '')
        deldata[i]['basePrice']=float(str(deldata[i]['basePrice']).replace(' ', ''))
        #print(deldata[i])
        for j in range(len(filedata)):
            if ((deldata[i]["name"] == filedata[j]["name"]) and (deldata[i]["basePrice"] == filedata[j]["basePrice"])):
                filedata.pop(j)
                break
    print("after")   
    print(filedata)         
    with open('sampledata.txt', 'w') as f:
        json.dump(filedata, f)    
    return redirect(url_for('home'))




@app.route('/homepage')
def home():
    # Create cursor
    f=open("sampledata.txt","r")
    filedata=json.loads(f.read())
    df = pd.DataFrame(filedata) 
    print(df.head)
    for index, row in df.iterrows():
        APIsymbol=row['name']
        APIURL="https://query1.finance.yahoo.com/v7/finance/options/"+APIsymbol
        #APIURL="https://www.alphavantage.co/query?function="+APIfunction+"&symbol="+APIsymbol+"&interval="+APIinterval+"&apikey="+APIKEY
        print(APIURL)
        r=requests.get(APIURL)
        df.loc[index,'id']=int(index+1)
        print(r)
        if r.status_code in (200,):
            api_data=r.json()
            if api_data['optionChain']['result']:
                if 'regularMarketPrice' in api_data['optionChain']['result'][0]['quote']:
                    current_price=api_data['optionChain']['result'][0]['quote']['regularMarketPrice']
                    df.loc[index,'currentPrice']=current_price
                    df.loc[index,'percentageChange']=round(((float(current_price)-float(row['basePrice']))/float(current_price))*100,2)
                else:
                    df.loc[index,'currentPrice']=0
                    df.loc[index,'percentageChange']=0
                    df.loc[index,'message']="Error_in_the_Symbol"
            else:
                df.loc[index,'currentPrice']=0
                df.loc[index,'percentageChange']=0
                df.loc[index,'message']="Error_in_the_Symbol"
        else:
            df.loc[index,'currentPrice']=0
            df.loc[index,'percentageChange']=0
            df.loc[index,'message']="Error_with_the_API_call"
    print(df.head()) 
    df_json=df.to_json(orient='records') 
    print(type(json.loads(df_json)))
    #return {'alldata':json.loads(df_json)}
    return render_template('alldata.html', articles=json.loads(df_json))
    

@app.route("/mukya1",methods=['POST'])
def mukya1():
    data=request.args.get('text_to_save')
    print("data1")
    print(type(data))
    time=str(datetime.now())
    time=time.replace(' ','-').replace(':','-').split('.')[0]
    filename='1-'+time+'.txt'
    with open(filename, 'w') as f:
        f.write(data)
    return 'ok1'


@app.route("/mukya2",methods=['POST'])
def mukya2():
    data=request.args.get('text_to_save')
    print("data2")
    print(type(data))
    time=str(datetime.now())
    time=time.replace(' ','-').replace(':','-').split('.')[0]
    filename='2-'+time+'.txt'
    with open(filename, 'w') as f:
        f.write(data)
    
    return 'ok2'    

@app.route("/add_record", methods=['GET','POST'])
def add_a_record():
    print(request.method)
    if 'stockname' in request.form:
        name=request.form['stockname'] 
        baseprice=request.form['baseprice']  
        if name!='' and baseprice!='':
            print("name n price")
            print(name)
            print(baseprice)
            jsondata=[{"name":name.upper().replace(" ",""),"basePrice":float(baseprice)}]
            f=open("sampledata.txt","r")
            filedata=json.loads(f.read())
            total=filedata+jsondata
            total = [i for n, i in enumerate(total) if i not in total[n + 1:]]
            print(total)
            with open('sampledata.txt', 'w') as f:
                json.dump(total, f)
            message="Successfully uploaded"       
        return render_template("add_record.html",message=message)
    else:
        return render_template("add_record.html",message="fill the details")


@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200