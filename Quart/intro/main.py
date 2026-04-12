from quart import Quart, render_template, Blueprint

app = Quart(__name__)

@app.route("/")
async def main_page():
    return "Hello, Welcome"

if __name__ == "__main__":
    app.run(debug=True)