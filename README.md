# ngo #

### Example of RESTlike API requests ###

* Create new user: 
```
curl -v -X POST http://127.0.0.1:8080/user -H "Content-Type: application/json" --data-binary @- <<BODY
{
    "email": "johndoe@gmail.com",
    "telegram": "@johnDoe",
    "first_name": "John",
    "last_name": "Doe"
}
BODY

```

* Get user by ID:
```
curl http://127.0.0.1:8080/user/13 | jq
```

* Delete user by ID:
```
curl -v -X DELETE http://127.0.0.1:8080/user/13 | jq
```

* Update user by ID:
```
curl -v -X PUT http://127.0.0.1:8080/user/2 -H "Content-Type: application/json" --data-binary @- <<BODY
{
"uuid": "b17e71ff-f466-11eb-b895-54ab3aab2d49",
"email": "johndoe@gmail.com",
"telegram": "@johnDoe",
"first_name": "John",
"last_name": "Doe Moriarty",
"created": "2021-08-03 20:20:20"
}
BODY
```

### Example user actions ###

* Deposit:
```
curl -v -X POST http://127.0.0.1:8080/actions/deposit -H "Content-Type: application/json" --data-binary @- <<BODY
{
"user_id": 2,
"fund_id": 2,
"asset_id": 2,
"amount": 200.00,
"comment": "Doe Moriarty"
}
BODY
```