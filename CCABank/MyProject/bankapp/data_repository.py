accounts = [
        {
            "id": 1,
            "type_name": "Savings Account",
            "rate_of_interest": 4.5,
            "year_launched": 1960
        },
        {
            "id": 2,
            "type_name": "Current Account",
            "rate_of_interest": 2.5,
            "year_launched": 1970
        },
        {
            "id": 3,
            "type_name": "Fixed Deposit Account",
            "rate_of_interest": 7.5,
            "year_launched": 1980
        }
    ]
next_account_id = 4

def createaccount(request):
    global next_account_id
    account = {
        "id": next_account_id,
        "type_name": request.POST["type_name"],
        "rate_of_interest": request.POST["rate_of_interest"],
        "year_launched": request.POST["year_launched"]
    }
    accounts.append(account)
    next_account_id += 1

def readaccounts():
    return accounts

def readaccount(id):
    """
    for account in accounts:
        if account["id"] == id:
            return account
    return None
    """
    return  next((item for item in accounts if item["id"] == id), None)

def updateaccount(request,id):
    account = readaccount(id)
    account["type_name"] = request.POST["type_name"]
    account["rate_of_interest"] = request.POST["rate_of_interest"]
    account["year_launched"] = request.POST["year_launched"]

def deleteaccount(id):
    accounts.remove(readaccount(id))
