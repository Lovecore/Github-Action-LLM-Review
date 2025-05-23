@app.get("/badcode")
def badcode():
    eval("print('bad code')")
    return {"message": "This is a test endpoint TEST ENDPOINT WIHT BAD CODE"}
    