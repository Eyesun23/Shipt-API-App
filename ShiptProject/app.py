from models import Base, Category, Product, Customer, Order, OrderItem
from flask import Flask, jsonify, request, url_for, abort, g, render_template,make_response, send_file
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import datetime
from pandas import DataFrame
import json

engine = create_engine('sqlite:///customers.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/categories', methods = ['GET','POST','PUT'])
def showAllCategorys():
    if request.method == 'GET':
        categorys = session.query(Category).all()
        return jsonify(categorys = [category.serialize for category in categorys])
    elif request.method == 'POST':
        name = request.json.get('name')
        id = request.json.get('id')
        description = request.json.get('description')
        newCategory = Category(name = name, id = id, description = description)
        session.add(newCategory)
        session.commit()
        return jsonify(newCategory.serialize)
    elif request.method == 'PUT':
        name = request.json.get('name')
        id = request.json.get('id')
        description = request.json.get('description')
        session.query(Category).filter(Category.id == id).update({Category.name:name, Category.description:description})
        session.commit()
        return "updated"

@app.route('/products', methods = ['GET', 'POST'])
def showAllProducts():
    if request.method == 'GET':
        products = session.query(Product).all()
        return jsonify(products = [product.serialize for product in products])
    elif request.method == 'POST':
        name = request.json.get('name')
        description = request.json.get('description')
        category = request.json.get('category')
        category_obj = [session.query(Category).filter(Category.name == str(cat_name) ).first() for cat_name in category]
        price = request.json.get('price')
        newProduct = Product(name = name, description = description, price = price)
        newProduct.category.extend(category_obj)
        session.add(newProduct)
        session.commit()
        return jsonify(newProduct.serialize)

@app.route('/customers', methods = ['GET', 'POST'])
def showAllCustomers():
    if request.method == 'GET':
        customers = session.query(Customer).all()
        return jsonify(customers = [customer.serialize for customer in customers])
    elif request.method == 'POST':
        name        = request.json.get('name')
        email       = request.json.get('email')
        newCustomer = Customer(name = name, email = email)
        session.add(newCustomer)
        session.commit()
        return jsonify(newCustomer.serialize)


@app.route('/orders', methods = ['GET','POST','PUT'])
def showAllOrders():
    if request.method == 'GET':
        orders = session.query(Order).all()
        return jsonify(orders = [order.serialize for order in orders])
    elif request.method == 'POST':
        products    = request.json.get('products')
        status      = request.json.get('status')
        date        = request.json.get('date')
        customer_id = request.json.get('customer_id')
        newOrder    = Order(status=status, customer_id= customer_id, date=date)
        session.add(newOrder)
        session.commit()
        for prod_name, quantity in products.items():
            item = session.query(Product).filter(Product.name == str(prod_name) ).first()
            oi   = OrderItem( item.id, newOrder.id, quantity = quantity)
            session.add(oi)
        session.commit()
        return jsonify(newOrder.serialize)

@app.route('/ordersummary', methods = ['GET','POST','PUT'])
def showAllDates():
    """
        An API endpoint that accepts a date range and a day,
        week, or month and returns a breakdown of products sold by quantity per day/week/month.
    """
    if request.method == 'GET':
        json = request.get_json()
        try:
            start_date = datetime.datetime.strptime(json['start_date'], '%m/%d/%Y')
            end_date   = datetime.datetime.strptime(json['end_date'], '%m/%d/%Y')
        except ValueError:
            return make_response(jsonify(error='Invalid date format, use MM/DD/YYYY (11/20/2000 for Nov 20, 2001)'), 400)
        interval = json['time_unite']
        if interval not in ['day', 'month', 'year']:
            return make_response(jsonify(error='Invalid interval format (use day, month, or year).'), 400)
        delta  = end_date-start_date
        orders = session.query(Order).filter(Order.date.between(start_date, end_date)).all()
        items_quantities = {}
        for order in orders:
            for item in order.itemsOrder:
                prod_name = item.product.name
                items_quantities[prod_name] = items_quantities.get(prod_name, 0) + item.quantity
        if interval == 'day':
            results = {key: round(value/delta.days,2) for key,value in items_quantities.items()}
        elif interval == 'month':
            results = {key: round(value/(delta.days/30.0),2) for key,value in items_quantities.items()}
        else:
            results = {key: round(value/(delta.days/365.25),2) for key,value in items_quantities.items()}
        if "save" in json.keys():
            dump_to_csv(json,results)
            return dump_to_csv(json,results)
        else:
            return jsonify(results)

@app.route('/ordersummary/recieve/', methods = ['GET'])
def sendfile():
    if request.method == 'GET':
        directory='/Users/friend/Desktop/Shipt/'
        file_name     ='sales_summary.csv'
        return send_file(directory+file_name, attachment_filename='sales_summary.csv')


def dump_to_csv(json,results):
    if "save" in json.keys():
        directory         = "/Users/friend/Documents/"
        directory ="/Users/friend/Desktop/Shipt/"
        file_name                = "sales_summary.csv"
        dictionary_result = {"Product" : list(results.keys()),
                             "Average_sales": list(results.values())}
        df = DataFrame(dictionary_result)[["Product","Average_sales" ]]
        df.to_csv(directory+file_name, index = False)
        return send_file(directory+file_name, attachment_filename=file_name)


@app.route('/orderitems', methods = ['GET','POST','PUT'])
def showAllOrderItems():
    if request.method == 'GET':
        orderitems = session.query(OrderItem).all()
        return jsonify(orderitems = [orderitem.serialize for orderitem in orderitems])
    elif request.method == 'POST':
        id           = request.json.get('id')
        quantity     = request.json.get('quantity')
        newOrderItem = OrderItem(quantity=quantity, id = id)
        session.add(newOrderItem)
        session.commit()
        return jsonify(newOrderItem.serialize)

@app.route("/customercat", methods=['GET','POST','PUT'])
def showAllCustCat():
    results   = []
    customers = session.query(Customer).all()
    for customer in customers:
        quantities = {}
        for order in customer.orders:
             for item in order.itemsOrder:
                for category in item.product.category:
                    quantities[category] =  quantities.get(category,0) + item.quantity
        for category in quantities.keys():
            results.append({'id': customer.id, 'name': customer.name, 'category_id': category.id, 'category': category.name, 'quantity': quantities[category]})
    return jsonify(results)

@app.route('/customers/<id>', methods = ['GET', 'POST'])
def showCustomerOrders(id):
    if request.method == 'GET':
        orders = session.query(Customer).filter(Customer.id == int(id)).first().orders
        results = []
        for order in orders:
            order_detail =[]
            for item in order.itemsOrder:
                order_detail.append({'order.id': item.order_id, 'product.id': item.product_id, 'name': item.product.name, 'quantity': item.quantity})
            results.append({'order': order.serialize,
                            'deltails': order_detail})
    return jsonify(results)


if __name__ == '__main__':
    app.debug = True
    app.run()
