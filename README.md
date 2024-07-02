## What's this about?

This project began life as an exercise in creating a simple
Django Ninja API for my own educational purposes. However,
I very quickly dreaded the idea of replicating boilerplate
view functions for basic CRUD operations on the models.

As a result, the "AutoDojo" project was spawned. AutoDojo
was originally a part of this code base, before being split
into a separately maintainable and installable package.

The AutoDojo package is also available
[from my Github page](https://github.com/owenjklan/django-autodojo).

It demonstrates AutoDojo's abilities to generate the required
Schema classes and view functions for simple Django ORM Model
classes. Foreign Key support is present but generating views
to deal with M2M relations appropriately is missing from AutoDojo,
as of July 2024.

To see an example of AutoDojo in use, take a look at [django_books_api/urls.py](./django_books_api/urls.py).

### There's also Postman / Newman-based testing...
This project also became a vector for experimenting with building
Postman collections to run tests against generated APIs. Although
the test Postman collection doesn't cover all aspects of testing
the API, it does demonstrate taking a collection exported from
JSON and using the Newman CLI Postman runner tool to perform
tests against the application.

This can be found in the `testing` directory in the base repository
directory and the [TESTING-README.md](./testing/TESTING-README.md)
file has more details.