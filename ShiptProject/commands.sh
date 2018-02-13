#!/bin/bash
# put all your commands here

curl http://localhost:5000/customers -H "Content-Type: application/json" -X POST -d '{"name":"Sanduíchess"}' -v

curl http://localhost:5000/categories -H "Content-Type: application/json" -X POST -d '{"name":"Food"}' -v

curl http://localhost:5000/products -H "Content-Type: application/json" -X POST -d '{"name":"Apple", "category" : ["Technology"]}' -v

curl http://localhost:5000/orders -H "Content-Type: application/json" -X POST -d '{"products":{"Apple":70}, "customer_id": 1, "status": "new"}' -v

curl http://localhost:5000/ordersummary -H "Content-Type: application/json" -X GET -d '{"start_date" : "1/1/2017","end_date":"1/2/2018", "time_unite":"month", "save":"yes"}' -v
