from quart import Quart

app = Quart(__name__)

@app.route("/")
async def home():
    return "Hello"

if __name__ == "__main__":
    app.run()