# ImageInj

## CS50
>This was my final project for conclude the CS50 course

>CS, python, flask, flask web framework, web development, CS50, Image Injection, Steganography
## Features

- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)
- [Flask](https://flask.palletsprojects.com/en/1.1.x/)
- [Flask-WTF](https://flask-wtf.readthedocs.io/en/stable/index.html)
- [Stegano](https://pypi.org/project/stegano/)

I've used Flask web framework based in Python
its was necessary flask-sqlalchemy for manage SQL database with sqlite and flask-wtf for upload files and forms extensions

## Explaining the project and the database
My final project is a website that allow the registered users to Inject Text inside Images using steganography, and then share this images with other users, the users can see the images and if they want, they can extract the text from the image.

All information about users, cases and selected cases for each people are stored in site.db.

I used sqlalchemy extension to connect the database to the application and sqlite3 for managing.

### Injecting text inside images

```python
@app.route("/inject", methods=["GET", "POST"])
@login_required
def inject():
    form = InjectImageForm()
    if form.validate_on_submit():
        image = form.image.data
        text = form.text.data
        filename = image.filename

        # Read the image file into memory
        image_bytes = BytesIO(image.read())
        img = Image.open(image_bytes)

        # Inject the text into the image
        secret = lsb.hide(img, text)

        # Save the modified image
        secret.save(filename)

        return redirect(url_for("home"))
    return render_template("inject.html", form=form)
``` 

if you do not select any file or not write any text the program warns you through messages 

```html
<div class="container">
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <div class="alert alert-danger" role="alert">
                    {% for message in messages %}
                        {{ message }}
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        <div class="flex-container">
      {% block content %}
      {% endblock %}
   </div>
    </div>
```


## Walkthrough on youtube
[My Final Project presentation](https://youtu.be/xX9LMsMln_Y)

## Documentation
https://flask.palletsprojects.com/en/1.1.x/

https://flask-sqlalchemy.palletsprojects.com/en/2.x/

https://flask-wtf.readthedocs.io/en/stable/form.html#module-flask_wtf.file

## About CS50
CS50 is a openware course from Havard University and taught by David J. Malan

Introduction to the intellectual enterprises of computer science and the art of programming. This course teaches students how to think algorithmically and solve problems efficiently. Topics include abstraction, algorithms, data structures, encapsulation, resource management, security, and software engineering. Languages include C, Python, and SQL plus students’ choice of: HTML, CSS, and JavaScript (for web development).

- Where I get CS50 course?
https://cs50.harvard.edu/x/2023/