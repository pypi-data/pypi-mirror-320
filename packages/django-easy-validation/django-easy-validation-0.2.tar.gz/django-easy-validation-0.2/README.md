Django Easy Validation |pypi version|
---------------------------------------



Django Easy Validation is a simple Django library that allows validation for forms via ajax in a simple and elegant way.



## Installation

Install project with pip

```bash
  pip install django-easy-validation
```
    
## Usages

```python
from django_easy_validation import Validator
from django.http import HttpResponse, JsonResponse


    def store(request):
       errors = Validator.validate(request, {
           "name": "required|unique:rating_metrices|max:100|min:6",
           "score": "required|numeric"
       })
       if errors:
           return JsonResponse(errors, status=422, safe=False)

    return JsonResponse('success', safe=False)

```
By default validator generated messages will be thrown, but messsages can be customized too. For example if you want to show custom messages based on validation attributes you can define it as follows

```python
from django_easy_validation import Validator
from django.http import HttpResponse, JsonResponse


    def store(request):
       errors = Validator.validate(request, {
           "name": "required|unique:rating_metrices|max:100|min:6",
           "score": "required|numeric"
       },{
         'name.required': 'Name field cannot be empty',
         'score.required': 'Score should be assigned to each name',
      })
       if errors:
           return JsonResponse(errors, status=422, safe=False)

    return JsonResponse('success', safe=False)
```

## Advance Usages

Instead of writing rules inside the validator validate method you can import it from other files to make the code for elegant. For example: Create a user_rules.py file under rules directory and place all your rules and messages there.

user_rules.py
```python

class UserRules:

    valid_rules = {
        'name': 'required|min:6|max:20',
        'score': 'required|numeric',
    }

    messages = {
        'required.name': 'Name field cannot be empty',
        'required.score': 'You must add score for each name',
    }


```
Now you can import user_rules.py in your views and use it as below

```python

from django_easy_validation import Validator
from rules.user_rules import UserRules


def store(request):
    metrices = json.loads(request.body)
    errors = Validator.validate(request, UserRules.valid_rules, UserRules.messages)
    if errors and is_ajax:
        return JsonResponse(errors, status=422, safe=False)

```
## Available Validation Rules

```javascript
required
min     (min:10)
max     (max:100)
unique  (unique:users)
email
numeric
boolean
string
uppercase

```
## Build Locally

Clone the project

```bash
  git clone https://github.com/sandysh/django-easy-validation.git
```

Go to the project directory

```bash
  cd django-easy-validation
```

Build

```bash
  python setup.py sdist
```

Publish

```bash
  twine upload dist/*
```


## Authors

- [@sandysh](https://www.github.com/sandysh)