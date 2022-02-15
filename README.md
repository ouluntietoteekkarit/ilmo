# otit_ilmo
Event registration forms for Oulun Tietoteekkarit ry

## Run development server
```shell
python3 -m venv env
source env/bin/activate
pip install -r requirements
export FLASK_APP=app.py
flask run
```

## S gunicorn
```shell
gunicorn --workers=1 --worker-connections=400 --bind=0.0.0.0:62733 wsgi:app --name=ilmot --timeout 20 --daemon
```

## Adding new forms
Add a new event form python script to the forms folder. The file must have .py file extension. The name of the 
script file is used for creating URL paths, database tables and for the application's internal form identification. 

Create a new folder in templates folder with the same name as the form script, excluding any possible file extension.
In this folder, create a file with name index.html. This file will contain the form's HTML template.

Third and last file that must be added is the privacy statement pdf. The file must have same name as the from's script 
file and it must be a pdf file with .pdf file extension. The file must be stored in static/privacy_statements folder.

### Form scripts
A form script is a normal python module and contains all the backend code that a form needs. It must expose a single 
public function called get&#95;module&#95;info at the end of the script. get_module_info is used to obtain the form's 
information so that it can be registered to Flask. The method must return a singleton instance of ModuleInfo as some 
of this object's information is filled in by the Flask server and is used by the form itself.

At the beginning of the script, after all the imports, the script should declare a variable called _form_name. The 
value of _form_name must be the script's name without path or file extensions. There's a helper function to achieve 
this and the declaration should look like this: `_form_name = file_path_to_form_name(__file__)`. The _form_name is 
declared so early for convenience and to allow easier copy-paste creation of new forms. Using the script file's name 
in this manner also ensures that all the forms have a unique name value as most file systems do not allow items of 
same name under a single folder.

The form script must define three classes: &#95;Model, &#95;Form and &#95;Controller. _Model is the database model 
and it must inherit BasicModel. The &#95;Model class must also define &#95;&#95;tablename&#95;&#95; attribute to and 
set it to _form_name. This prevents table name conflicts in the database. &#95;Form defines the HTML form that is 
shown in the browser. It must inherit BasicForm. Commonly used form fields can be added with decorators. &#95;Controller 
must inherit FormController. A barebones controller that overrides _get_email_msg can handle most of the common case.
If more flexibility is required, other methods can be overridden as well.

All form scripts aim to define identically named, enclosed classes to keep them consistent. It is possible to use 
different class names but there is little reason to do so.


### Form HTML template
The forms require an HTML template to be displayed in the browser. Each template must extend form.html. Importing 
macros.html is also adviced by not necessary. macros.html contains a set of utility macros. form.html has four blocks 
which can be overridden in the template to alter their contents. These are extra_styles, extra_js, event_info and 
registration_form. For a minimal form, only event_info needs to be overridden. event_info must contain the event 
information. registration_form is used to render the _Form classe's fields. extra_styles allows adding CSS styles 
to the form, such as background images. The contents of this block must include the style tags. extra_js allows 
adding JavaScript to the form. This block must include the script tags. Multiple script tags may be used.
