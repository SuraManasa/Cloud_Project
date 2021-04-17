from stock import app as app


if __name__ == "__main__":
    app.debug=True
    app.run(use_reloader=False,host='0.0.0.0',port=80)
