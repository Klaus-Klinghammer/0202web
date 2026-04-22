from bottle import post, request

@post('/home')
def my_form():
    email = request.forms.get('ADRESS')
    return f"Thanks! The answer will be sent to the mail {email}"