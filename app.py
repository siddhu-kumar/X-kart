from flask import Flask, render_template, request,flash, redirect,url_for,session, make_response, send_from_directory
import random,re,sqlite3
import S2_db as dblib
from werkzeug.utils import secure_filename
import datetime
app= Flask(__name__)
app.secret_key = "Myfirst"

@app.route('/',methods=['GET', 'POST'])       
def register(): 
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        city = request.form['city']
        password = request.form['password']

        with sqlite3.connect('sql.db') as sqliteConnection:
            cursor = sqliteConnection.cursor()
            cursor.execute(f'''Select * from Customers where email="{email}"''')
            result = cursor.fetchall()
            if result:
                flash('Email Already Registered')
                return redirect(url_for('register'))

        if not re.match(r'\w*[a-z]+\w*[A-Z]+\w*|\w*[A-Z]+\w*[a-z]+\w*',password):
                flash('Password must contain atleast 1 Uppercase and 1 lowercase character')
                return redirect(url_for('register'))

        userid = random.randint(1000000,9999999)
        with sqlite3.connect('sql.db') as sqliteConnection:
            cursor = sqliteConnection.cursor()
            cursor.execute(f'''INSERT INTO Customers (name,email,password,address,city,userid) VALUES ('{name}','{email}','{password}','{address}','{city}','{userid}')''')
            sqliteConnection.commit()
        return render_template('registration_success.html', 
                        name=name, ack = userid)
    else:
        return render_template('register.html')

@app.route('/login',methods=['GET', 'POST'])       
def login(): 
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        if userid == "admin@admin.com" and password == "1234":
            return redirect(url_for('admin_home'))
        with sqlite3.connect('sql.db') as sqliteConnection:
            cursor = sqliteConnection.cursor()
            cursor.execute(f'''Select * from Customers where userid="{userid}"''')
            result = cursor.fetchone()
            #print(result)
            if not result:
                flash("No such User Found",'warning')
                return redirect(url_for('login'))
            if result[2]!=password:
                flash("Wrong Password",'warning')
                return redirect(url_for('login'))
            session['username'] = [result[0],result[5]]
            session['cart'] = {}
            return redirect(url_for('home'))

    else:
        return render_template('login.html')

@app.route('/logout',methods=['GET', 'POST'])       
def logout(): 
    if request.method == 'POST':
        pass
    else:
        # print(session)
        session.pop('username', None)
        session.pop('cart', None)
        #print(session)
        flash("Logged Out Successfully !",'primary')
        return redirect(url_for('login'))

@app.route('/home')
def home():
    with sqlite3.connect('sql.db') as sqliteConnection:
        cursor = sqliteConnection.cursor()
        cursor.execute(f'''Select * from Products''')
        items = cursor.fetchall()
        username = session['username']
    return render_template('home.html',items=items, username=username)

@app.route('/add/<id>',methods=['GET','POST'])
def add(id):
    print(id)
    temp = session['cart']
    if(id not in temp):
        temp[id] = 1
    else:
        temp[id] += 1
    
    session['cart'] = temp

    print(session['cart'])
    for key,value in session['cart'].items():
            print(key,value)
    return redirect(url_for('home'))

@app.route('/cart')
def cart():
    prd_list = list()
    username = session['username']
    with sqlite3.connect('sql.db') as connect:
        cursor = connect.cursor()
        for key,value in session['cart'].items():
            get_prd = cursor.execute(f"select * from Products where prod_id='{key}'").fetchone()
            # print(get_prd)
            prd_list.append([get_prd[0],get_prd[1],get_prd[2],get_prd[3],value])
    
    return render_template('cart.html', items=prd_list, username = username)

@app.route('/update_cart/<string:prod_id>/<int:val>',methods=['POST'])
def update_cart(prod_id,val):
    if request.method =='POST':
        temp = session['cart']
        if val == 0:
            if temp[prod_id]>1:
                temp[prod_id] -= 1
                print(temp[prod_id])
            else:
                del temp[prod_id]
        else:
            temp[prod_id]+=1
            print(temp[prod_id])
        session['cart'] = temp

    return redirect(url_for('cart'))

@app.route('/test')
def test():
    session.pop('username',None)
    session.pop('cart',None)
    return 'Done'

@app.route('/payment',methods=['GET','POST'])       
def payment():
    if request.method=='POST':
        user_id = session['username'][1]
        cart = session['cart']
        with sqlite3.connect('sql.db') as connect:
            cursor = connect.cursor()
            order_id = random.randint(100000,999999)
            qnt = 0
            amount = 0
            for id in cart:
                cursor.execute('''INSERT INTO OrderItems (order_id, prod_id, quantity) VALUES (?,?,?)''',(order_id, id, cart[id]))
                qnt +=1
                data = cursor.execute(f'''select price from Products where prod_id="{id}"''').fetchone()
                amount = data[0]
            curr_date= datetime.datetime.now()
            expected_date = curr_date + datetime.timedelta(days=5)
            cursor.execute('''INSERT INTO Orders (order_id, amount, status, user_id, order_date, expected_date, quantity) VALUES (?,?,?,?,?,?,?)''',(order_id, amount, 'confirmed', user_id, curr_date.strftime("%Y-%m-%d"), expected_date.strftime("%Y-%m-%d"),qnt))
            connect.commit()
        session['cart'] = {}
        flash("Order Successsful",'success')
        return redirect('/order')
    else:
        return render_template('payments.html')

@app.route('/order')       
def order():
    username = session['username'][0]
    user_id = session['username'][1]
    cart = session['cart']
    with sqlite3.connect('sql.db') as connect:
        cursor = connect.cursor()
        print(user_id)
        data = cursor.execute(f'''select * from Orders where user_id="{user_id}"''').fetchall()
    return render_template('order.html', orders=data, username=username)

@app.route('/view_order/<int:order_id>')       
def view_order(order_id):
    username = session['username'][0]
    with sqlite3.connect('sql.db') as connect:
        cursor = connect.cursor()
        data = cursor.execute(f'''select * from OrderItems join Products on OrderItems.prod_id=Products.prod_id where order_id="{order_id}"''').fetchall()
        print(data)
    return render_template('view_order.html',data = data, username=username)

@app.route('/admin_home',methods=['GET','POST'])
def admin_home():
    if request.method == 'POST':
        prd_name = request.form['prd_name'].capitalize().strip()
        prd_category = request.form['prd_category'].capitalize().strip()
        prd_price = request.form['prd_price']
        if(len(prd_category)==0 or len(prd_name)==0):
            flash('Invalid Inputs','warning')
            print('Invalid input')
            return redirect(url_for('admin_home'))
        with sqlite3.connect('sql.db') as connect:
            cursor = connect.cursor()
            prd_id = prd_category[0]+str(random.randint(1000,9999))
            cursor.execute('''INSERT INTO Products (prod_id,prod_name, prod_category,price) VALUES (?,?,?,?)''',(prd_id,prd_name, prd_category,prd_price))
            connect.commit()
            flash('Product has been added.')
            cursor.execute('''select * from Products where prod_id = ?''',(prd_id,))
            print(cursor.fetchone())
    return render_template('admin.html')


@app.route('/show_product',)
def show_product():
    with sqlite3.connect('sql.db') as connect:
        cursor = connect.cursor()
        data = cursor.execute('''select * from Products''').fetchall()

    return render_template('showproduct.html',items = data)

@app.route('/update_product/<string:prd_id>',methods=['GET','POST'])
def update_product(prd_id):
    print(prd_id)
    with sqlite3.connect('sql.db') as connect:
        cursor = connect.cursor()
        data = cursor.execute('select prod_name,prod_category,price from Products where prod_id = ?',(prd_id,)).fetchone()
    if request.method == 'POST':
        prd_name = request.form['prd_name']
        prd_category = request.form['prd_category']
        prd_price = request.form['prd_price']
        with sqlite3.connect('sql.db') as connect:
            cursor = connect.cursor()
            cursor.execute('update Products set prod_name = ?,prod_category = ?,price = ? where prod_id = ?',(prd_name,prd_category,prd_price,prd_id))
            connect.commit()
            data = cursor.execute('select prod_name,prod_category,price from Products where prod_id = ?',(prd_id,)).fetchone()
            print('product updated successfully')
    return render_template('updateproduct.html',items = data)

@app.route('/customers_list',methods=['GET','POST'])
def customers_list():
    with sqlite3.connect('sql.db') as connect:
        cursor = connect.cursor()
        cursor.execute('select userid, name, email, city, address from customers')
        data = cursor.fetchall()
    return render_template('customer_list.html',data = data)

@app.route('/delete_product/<string:prd_id>',methods=['GET','POST'])
def delete_product(prd_id):
    with sqlite3.connect('sql.db') as connect:
        cursor = connect.cursor()
        cursor.execute('delete from Products where prod_id = ?',(prd_id,))
        connect.commit()
        print('deleted successfully')
        data = cursor.execute('''select * from Products''').fetchall()

    return render_template('showproduct.html',items = data)


@app.route('/admin_order',methods=['GET','POST'])
def admin_order():
    with sqlite3.connect('sql.db') as connect:
        cursor = connect.cursor()
        data = cursor.execute(f'''select * from Orders''').fetchall()
    return render_template('admin_order.html',orders = data)

@app.route('/profile',methods=['GET','POST'])
def profile():
    user_id = session['username'][1]
    with sqlite3.connect('sql.db') as connect:
        cursor = connect.cursor()
        cursor.execute(f'select name,email,address,city,userid from Customers where userid = {user_id}')
        data = cursor.fetchone()
        print(data)
    print(user_id)

    if request.method == 'POST':
        up = request.files["image"]
        dblib.save(
            secure_filename(up.filename),
            up.content_type,
            up.read(),
        )
        return "OK"
    
    # dbfile = request.args.get("f")
    user = dblib.get_user_by_id(user_id)
    if user and user[3]:
        response = make_response(user[4])
        response.headers["Content-type"] = "image/jpeg"  # Set the appropriate content type
        return response 

    return render_template('userprofile.html',data = data)




if __name__=='__main__':
   app.run(debug=True) 