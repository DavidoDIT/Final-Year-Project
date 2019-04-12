from winesite import app

""" The file allows the running of the application """
if __name__ == "__main__":
    print(
        (
            "* Loading Keras model and Flask starting server..."
            "please wait until server has fully started"
        )
    )
    app.run(debug=True)
