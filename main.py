import sqlite3

from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/categories")
async def categories():
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")  # northwind specific
    app.db_connection.row_factory = sqlite3.Row
    category_id = app.db_connection.execute("SELECT CategoryID, CategoryName FROM Categories ").fetchall()
    app.db_connection.close()
    ready_data = [{"id": item[0], "name": item[1]}for item in category_id]
    return {
        "categories": ready_data
    }


@app.get("/customers")
async def customers():
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")  # northwind specific
    app.db_connection.row_factory = sqlite3.Row
    customers_id = app.db_connection.execute("SELECT CustomerID, CompanyName FROM Customers ").fetchall()
    app.db_connection.close()
    ready_data = [{"id": item[0], "name": item[1]}for item in customers_id]
    return {
        "categories": ready_data
    }


@app.get('/products/{id}', status_code=200)
async def products(id: int):
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")
    app.db_connection.row_factory = sqlite3.Row
    product = app.db_connection.execute(f"SELECT ProductName FROM Products WHERE ProductID = {id}").fetchone()
    if product is None:
        raise HTTPException(status_code=404)
    app.db_connection.close()
    return {"id": id, "name": product['ProductName']}


@app.get('/employees', status_code=200)
async def employees(limit: int = -1, offset: int = 0, order: str = 'id'):
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")
    app.db_connection.row_factory = sqlite3.Row
    columns = {'first_name' : 'FirstName', 'last_name' : 'LastName', 'city' : 'City', 'id' : 'EmployeeID'}
    if order not in columns.keys():
        raise HTTPException(status_code=400)
    order = columns[order]
    employee = app.db_connection.execute(f"SELECT EmployeeID, LastName, FirstName, City FROM "
                                         f"Employees ORDER BY {order} LIMIT {limit} OFFSET {offset}").fetchall()
    app.db_connection.close()
    ready_data = [{"id": i['EmployeeID'], "last_name":i['LastName'],
                   "first_name":i['FirstName'], "city":i['City']} for i in employee]
    return {"employees": ready_data}


@app.get('/products_extended', status_code=200)
async def products_extended():
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")
    app.db_connection.row_factory = sqlite3.Row
    prod = app.db_connection.execute('''
    SELECT Products.ProductID AS id, Products.ProductName AS name, Categories.CategoryName AS category, 
    Suppliers.CompanyName AS supplier FROM Products 
    JOIN Categories ON Products.CategoryID = Categories.CategoryID 
    JOIN Suppliers ON Products.SupplierID = Suppliers.SupplierID ORDER BY Products.ProductID
    ''').fetchall()
    ready_data = [{"id": i['id'], "name": i['name'], "category": i['category'], "supplier": i['supplier']} for i in prod]
    app.db_connection.close()
    return {"products_extended": ready_data}


@app.get('/products/{id}/orders', status_code=200)
async def products_id_orders(id: int):
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")  # northwind specific
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(f'''SELECT Products.ProductID, Orders.OrderID AS id, 
    Customers.CompanyName AS customer, [Order Details].Quantity AS quantity, [Order Details].UnitPrice AS unitprice, 
    [Order Details].Discount as discount FROM Products 
    JOIN [Order Details] ON Products.ProductID = [Order Details].ProductID 
    JOIN Orders ON [Order Details].OrderID = Orders.OrderID JOIN Customers ON Orders.CustomerID = Customers.CustomerID 
    WHERE Products.ProductID = {id} ORDER BY Orders.OrderID''').fetchall()
    app.db_connection.close()
    if data is None:
        raise HTTPException(status_code=404)
    return {"orders": [
        {"id": i["id"], "customer": i["customer"], "quantity": i["quantity"], "total_price": round(((i['unitprice'] * i['quantity']) - (i['discount'] * (i['unitprice'] * i['quantity']))), 2)}for i in data]}
