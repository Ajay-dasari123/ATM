from flask import Flask,redirect,url_for,render_template,request,session
import json
from mail import send_email
import random
import os

app = Flask(__name__)
app.secret_key = 'atm55'


def generate_otp():
    return str(random.randint(100000,999999))
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
def get_data():
    with open(DATA_FILE, 'r') as file:
        data = json.load(file)
        return data

def update_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data,file,indent=4)
    

@app.route('/')
def base():
    return redirect('login')

@app.route('/login',methods = ['GET','POST'])
def login():
    info=request.args.get('info')
    if request.method == 'POST':
        email = request.form.get('email')
        pin = request.form.get('pin')
        data = get_data()
        users = data["users"]
        for i in users:
            if i["email"] == email and  i["pin"]==pin:
                session['username'] = i["username"]
                session['id'] = i["id"]
                return redirect(url_for('dashboard', user=i["username"]))
        else:
            return render_template('login.html', info="Invalid login")

    return render_template('login.html', info=info)

@app.route('/register',methods=['GET','POST'])
def register():
    info=request.args.get('info')
    if request.method == 'POST':
        username = request.form.get('uname')
        email = request.form.get('email')
        pin = request.form.get('pin')
        data = get_data()
        users = data["users"]

        for i in users:
            if i["email"] == email:
                return render_template("register.html",info="Email is already registered")
        details = {
            "id": len(users)+1,
            "username":username,
            "email":email,
            "pin":pin,
            "history": [],
            "balance": 0
        }
        users.append(details)
        update_data(data)
        return redirect('login')

    return render_template("register.html")

@app.route('/forgotpin',methods=['GET','POST'])
def forgotpin():
    info=request.args.get('info')
    if request.method == 'POST':
        email = request.form.get('email')
        data = get_data()
        users = data["users"]
        for i in users:
            if email == i["email"]:
                username = i["username"]
                otp = generate_otp()
                send_email(email,username,otp)
                session["otp"]=otp
                session['email']=email
                return redirect('verify')
            
        return render_template('forgotpin.html',info="Email is not registered yet")

    return render_template('forgotpin.html')

@app.route('/verify',methods=['GET','POST'])
def verify():
    info=request.args.get('info')
    if request.method == 'POST':
        otp = request.form.get('otp')
        if otp == session["otp"]:
            session['otp']=None
            return redirect('resetpin')
        return render_template('verify.html',info="Invalid OTP")
    return render_template('verify.html')

@app.route('/resetpin',methods=['GET','POST'])
def resetpin():
    info=request.args.get('info')
    if request.method == 'POST':
        npin = request.form.get('npin')
        cpin = request.form.get('cpin')
        if npin == cpin:
            data = get_data()
            users = data["users"]
            for i in users:
                if i["email"] == session['email']:
                    i["pin"] = npin
                    update_data(data)
                    return redirect('login')

        return render_template('resetpin.html',info="Confirm the pin properly")
    return render_template('resetpin.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('login')

@app.route('/dashboard/<user>')
def dashboard(user):
    if 'username' not in session:
        return redirect('login')
    return render_template("dashboard.html",username=user)

@app.route('/checkBalance')
def checkBalance():
    data = get_data()
    users = data["users"]
    for i in users:
        if i["id"]==session['id']:
            balance = i["balance"]
            return render_template('checkbalance.html',username = session['username'],balance=balance)

@app.route('/deposit',methods=['GET','POST'])
def deposit():
    if request.method=='POST':
        try:
            amount = int(request.form.get('amount'))
        except Exception:
            return render_template("deposit.html",
                                username = session['username'],
                                info="Enter the proper amount")
        data = get_data()
        users = data["users"]
        for i in users:
            if i["id"] == session["id"]:
                i["balance"]+=amount
                i["history"].append(f"{amount} deposited")
                update_data(data)
                return redirect('checkBalance')
    return render_template("deposit.html")

@app.route('/withdraw',methods=['POST','GET'])
def withdraw():
    if request.method=='POST':
        try:
            amount = int(request.form.get('amount'))
            if amount < 0:
                raise Exception("Enter the proper amount")
        except Exception:
            return render_template("withdraw.html",
                                username = session['username'],
                                info="Enter the proper amount")
        
        data = get_data()
        users = data["users"]
        for i in users:
            if i["id"] == session["id"]:
                if i["balance"]>=amount:
                    i["balance"]-=amount
                    i["history"].append(f"{amount} Withdraw")
                    update_data(data)
                    return redirect('checkBalance')
                else:
                    return render_template("withdraw.html",
                                username = session['username'],
                                info="Insufficient balance")

    return render_template('withdraw.html')

@app.route('/viewtransactions')
def viewtransactions():
    if 'username' not in session or 'id' not in session:
        return redirect(url_for('login'))
    data = get_data()
    users = data["users"]
    for i in users:
        if i["id"]==session["id"]:
            history = i["history"]
            length = len(history)
            return render_template("viewtransactions.html", history=history,length=length)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)