import sqlite3,random

sqliteConnection = sqlite3.connect('sql.db')
cursor = sqliteConnection.cursor()
# print('DB Init')

query1 = '''create table if not exists Customers( 
    name varchar(20), 
    email varchar(20), 
    password varchar(30),
    address varchar(300),
    city varchar(300),
    userid integer primary key
    )'''

query2 = '''Delete from Customers'''

query3 = '''create table if not exists Products(  
    prod_id varchar(20) primary key, 
    prod_name varchar(20), 
    price float,  
    prod_category varchar(20) 
    )'''


query4 = '''create table if not exists OrderItems(  
    order_id varchar(20), 
    prod_id varchar(20),
    quantity int)
    '''

query5 = '''create table if not exists Orders(  
    order_id varchar(20), 
    amount float,
    status varchar(20),
    user_id varchar(20),
    quantity int,
    order_date Date,
    expected_date Date)
    '''

query6 = '''drop table OrderItems'''

# query5 = "insert into Customers (name,email,address,city,password,userid) values ('siddhu','siddhu@gmail.com','tcs','tri','123',12345)"
# cursor.execute(query5)


products = [['Mobile','Electronics' ,14999],
['Laptop','Electronics',95999],
['Ear Phone','Electronics',699],
['Speaker','Electronics',2999],
['Clock','Home Decor',4000],
['Vase','Home Decor',1500],
['Curtains','Home Decor',700],
['Wallpaper','Home Decor',300],
['Pen','Stationary',15],
['Notebook','Stationary',120],
['Box','Stationary',299]]

# for name,category,price in products:
#     prod_id = category[0]+str(random.randint(1000,9999))
#     cursor.execute(f'''INSERT INTO Products (prod_id,prod_name,price,prod_category) VALUES ('{prod_id}','{name}','{price}','{category}')''')

cursor.execute('''create table if not exists profileimage(
    `ids` INTEGER PRIMARY KEY AUTOINCREMENT,
    `userid` INTEGER NOT NULL,
    `file_name` TEXT,
    `file_mime` TEXT NOT NULL,
    `file_data` BLOB NOT NULL,
    foreign key (userid) references Customers(userid)
);''')

# cursor.execute(query1)
# # # cursor.execute(query2)
# cursor.execute(query5)
cursor.execute(query4)

sqliteConnection.commit()
sqliteConnection.close()
