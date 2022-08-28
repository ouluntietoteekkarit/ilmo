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
gunicorn --workers=1 --worker-connections=400 --bind=0.0.0.0:62733 wsgi:server --name=ilmot --timeout 20 --daemon
```

## Adding new forms
Add a new event form python script to the _app/forms_ folder. The file must have .py file extension. The name of the 
script file is used for creating URL paths, database tables and for the application's internal form identification. 
Usually file systems only allow unique file names in a single directory so this should enforce the uniqueness of 
form names.

Create a new folder in _app/templates_ folder with the same name as the form script, excluding any possible file extension.
In this folder, create a file with name index.html. This file will contain the form's HTML template.

Third and last file that must be added is the privacy statement pdf. The file must have same name as the form's script 
file and it must be a pdf file with .pdf file extension. The file must be stored in _app/static/privacy_statements_ folder.

### Form scripts
A form script is a normal python module and contains all the backend code that a form needs. It must expose a single 
public function called get&#95;module&#95;info. get&#95;module&#95;info is used to obtain the form's information so 
that it can be registered to Flask. The method must return a singleton instance of ModuleInfo as some of this object's 
information is filled in by the Flask and is used by the form itself.

The script should declare a variable called _form_name. The value of _form_name must be the script's name without 
path or file extensions. There's a helper function to achieve this and the declaration should look like this: 
`_form_name = make_form_name(__file__)`. The _form_name should be declared early in the script for convenience and 
to allow easier copy-paste creation of new forms. Using the script file's name in this manner also ensures that all 
the forms have a unique name value as most file systems do not allow items of same name under a single folder.

The form script must define one class: &#95;Controller. The &#95;Controller must inherit/extend FormController. A 
barebones controller that overrides _get_email_msg can handle most of the common cases. If more flexibility is required, 
other methods can be overridden as well.

All form scripts aim to define identically named, enclosed classes to keep them consistent. It is possible to use 
different class names but there is little reason to do so because they are never exposed outside their defining module.

The form script must also define arrays of attributes that will define the HTML form and database model for the data
that the form will collect. Utitlity functions for commonly used attributes exist. Each form has three parts; required 
participant attributes, optional participant attributes and other attributes. Required participant attributes are 
always required. Optional participants are not necessary. Other attributes are used to hold other miscellaneous 
information. These attribute arrays are fed to make_types function which will generate proper form and database classes 
from them dynamically. The details of these classes are unimportant and they are exposed to the _Controller through 
interface-like classes.

To make form script creation easier, a stripped down base script exists in _app/form_lib/base_form_script.py_ file. The 
contents of this file can be copied to the newly created form python script file and errornous parts of the script may 
be replaced with the event's information. Another option is to copy some existing event script file's contents and 
modify them to have the new event's information.


### Form HTML template
The forms require an HTML template to be displayed in the browser. Each template must extend form.html. Importing 
macros.html is also adviced by not necessary. macros.html contains a set of utility macros. form.html has five 
blocks which can be overridden in the template to alter their contents. These are extra_styles, extra_js, event_info, 
registration_form and participant_list. For a minimal form, only event_info needs to be overridden. event_info must 
contain the event information. registration_form is used to render the form's attributes as input fields. extra_styles 
allows adding CSS styles to the form, such as background images. The contents of this block must include the style tags. 
extra_js allows adding JavaScript to the form. This block must include the script tags. Multiple script tags may be 
used. participant_list should be overridden when its contents should be different from a list of names. Excluding 
participant_list does not prevent it from being rendered. If the form does not ask for name publishing consent at all,
the participant list will not be rendered. Utility macros to render the list can be found in macros.html.

The form information is exposed in form variable. The form offers methods to access all the relevant fields. They are 
get_required_participants, get_optional_participants and get_other_attributes. While it is possible to access these 
properties with their attribute names, it is not recommended as this could potentially break in the future if more 
changes to the system are made. Optional participant fieldsets must always be wrapped in a 
registration&#95;optional&#95;participant call to ensure proper HTML generation and to keep the related JS and CSS 
working.
