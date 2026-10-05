from flask import Flask, render_template

# First you must run the scraper to generate data for pages

app = Flask(__name__)


@app.route("/")
def home() -> str:
    return render_template("home.html")


@app.route("/<page_name>")
def page(page_name: str) -> tuple[str, int]:
    try:
        with open(f"pages/{page_name}.txt", "r", encoding="utf-8") as f:
            content = f.read()
            status_code = 200
    except OSError:
        content = "Page not found."
        status_code = 404

    return render_template(
        "page.html", title=page_name.capitalize(), content=content
    ), status_code


if __name__ == "__main__":
    app.run()
