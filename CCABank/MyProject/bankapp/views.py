from django.http import HttpResponse
from django.shortcuts import render, redirect
#import data_repository as repo
import bankapp.db_repository as repo

def userlogin(request):
    if request.method == "POST":
        credentials = {"login_name":request.POST["login_name"],
                       "login_password":request.POST["login_password"]}
        session_id = repo.userlogin(credentials)
        if session_id:
            response = redirect("bhomepage")
            response.set_cookie('SESSION_ID', session_id)
            return response
        else:
            return HttpResponse("Invalid credentials")
    else:
        session_id = None
        return render(request,
                      "user_login.html",
                      {"user_role":repo.getuser(session_id)["role_name"]})

def userlogout(request):
    repo.deletesession(request.COOKIES.get('SESSION_ID'))
    response = redirect("buserlogin")
    response.delete_cookie('SESSION_ID')
    return response

def homepage(request):
    session_id = request.COOKIES.get('SESSION_ID')
    welcome_message = "Welcome to CCA Bank. "
    balance_amount = None
    user = repo.getuser(session_id)
    if user["role_name"] != "ROLE_PUBLIC":
        welcome_message += (user["login_name"])
    else:
        welcome_message += "You are not logged in. Please log in or register first."
    if request.method == "POST":
        if repo.validatecsrftoken(request.POST["token_csrf"],session_id):
            balance_amount = repo.getuserbalance(session_id)["balance_amount"]
    return render(request, "home_page.html",
                  {"welcome_message":welcome_message,
                   "user_role":user["role_name"],
                   "csrf_token":user["token"],
                   "balance_amount":balance_amount})

def addaccount(request):
    if request.method == "POST":
        account = {"type_name":request.POST["type_name"],
                   "rate_of_interest":request.POST["rate_of_interest"],
                   "year_launched":request.POST["year_launched"]}
        repo.createaccount(account)
        return redirect("blistaccount")
    else:
        return render(request,
                      "account_form.html",
                      {"form_title":"Create New Account",
                       "user_role":repo.getuser(request.COOKIES.get('SESSION_ID'))["role_name"]})

def updateaccount(request,id):
    if request.method == "POST":
        account = {"type_name": request.POST["type_name"],
                   "rate_of_interest": request.POST["rate_of_interest"],
                   "year_launched": request.POST["year_launched"]}
        repo.updateaccount(account,id)
        return redirect("blistaccount")
    else:
        return render(request,
                      "account_form.html",
                      {"form_title":"Update Account",
                       "account":repo.readaccount(id),
                       "user_role":repo.getuser(request.COOKIES.get('SESSION_ID'))["role_name"]})

def deleteaccount(request,id):
    repo.deleteaccount(id)
    return redirect("blistaccount")

def pagenotfound(request,exception):
    return render(request, "404.html",status=404)

def listaccount(request):
    return render(request,
                  "list_account.html",
                  {"accounts":repo.readaccounts,
                   "user_role":repo.getuser(request.COOKIES.get('SESSION_ID'))["role_name"]})

def aboutus(request):
    return render(request,
                  "about_us.html",
                  {"user_role":repo.getuser(request.COOKIES.get('SESSION_ID'))["role_name"]})

def contactus(request):
    return render(request,
                  "contact_us.html",
                  {"user_role":repo.getuser(request.COOKIES.get('SESSION_ID'))["role_name"]})

def userregister(request):
    return render(request,
                  "user_register.html",
                  {"user_role":repo.getuser(request.COOKIES.get('SESSION_ID'))["role_name"]})

def usertransaction(request):
    if request.method == "POST":
        session_id = request.COOKIES.get('SESSION_ID')
        if repo.validatecsrftoken(request.POST["token_csrf"],session_id):
            transfer = {"to_user": request.POST["to_user"],
                        "transfer_amount": request.POST["transfer_amount"], }
            repo.transfermoney(session_id,transfer)
            return redirect("bhomepage")
        else:
            print("CSRF Attack")
            return HttpResponse("CSRF Attack!")
    else:
        user = repo.getuser(request.COOKIES.get('SESSION_ID'))
        return render(request,
                      "user_transaction.html",
                      {"user_role":user["role_name"],"csrf_token":user["token"]})

def userfeedback(request):
    if request.method == "POST":
        comment = {"user_comment":request.POST["user_comment"],}
        repo.addcomment(request.COOKIES.get('SESSION_ID'),comment)
        return redirect("buserfeedback")
    else:
        return render(request,
                      "user_feedback.html",
                      {"user_role":repo.getuser(request.COOKIES.get('SESSION_ID'))["role_name"],
                       "user_comments":repo.getcomments()})
