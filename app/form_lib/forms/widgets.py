from __future__ import unicode_literals

from wtforms.widgets import Input, TextArea, Select, ListWidget

# MEMO: Bunch of custom widgets to fix some errors in WTForms rendering.


class CustomInput(Input):
    """
    Render a basic ``<input>`` field.

    This is used as the basis for most of the other input fields.

    By default, the `_value()` method will be called upon the associated field
    to provide the ``value=`` HTML attribute.
    """

    def __call__(self, field, **kwargs):
        if 'required' not in kwargs and 'required' in getattr(field, 'flags', []):
            kwargs.setdefault('data_is_required', True)

        return super().__call__(field, **kwargs)


class CustomTextInput(CustomInput):
    """
    Render a single-line text input.
    """
    input_type = 'text'


class CustomCheckboxInput(CustomInput):
    """
    Render a checkbox.

    The ``checked`` HTML attribute is set if the field's data is a non-false value.
    """
    input_type = 'checkbox'

    def __call__(self, field, **kwargs):
        if getattr(field, 'checked', field.data):
            kwargs['checked'] = True
        return super(CustomCheckboxInput, self).__call__(field, **kwargs)


class CustomFileInput(CustomInput):
    """Render a file chooser input.

    :param multiple: allow choosing multiple files
    """

    input_type = 'file'

    def __init__(self, multiple=False):
        super(CustomFileInput, self).__init__()
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        # browser ignores value of file input for security
        kwargs['value'] = False

        if self.multiple:
            kwargs['multiple'] = True

        return super(CustomFileInput, self).__call__(field, **kwargs)


class CustomTextArea(TextArea):
    """
    Renders a multi-line text area.

    `rows` and `cols` ought to be passed as keyword args when rendering.
    """
    def __call__(self, field, **kwargs):
        if 'required' not in kwargs and 'required' in getattr(field, 'flags', []):
            kwargs.setdefault('data_is_required', True)

        return super().__call__(field, **kwargs)


class CustomSelect(Select):
    """
    Renders a select field.

    If `multiple` is True, then the `size` property should be specified on
    rendering to make the field useful.

    The field must provide an `iter_choices()` method which the widget will
    call on rendering; this method must yield tuples of
    `(value, label, selected)`.
    """
    def __call__(self, field, **kwargs):
        if 'required' not in kwargs and 'required' in getattr(field, 'flags', []):
            kwargs.setdefault('data_is_required', True)

        return super().__call__(field, **kwargs)


class CustomListWidget(ListWidget):
    """
    Renders a list of fields as a `ul` or `ol` list.

    This is used for fields which encapsulate many inner fields as subfields.
    The widget will try to iterate the field to get access to the subfields and
    call them to render them.

    If `prefix_label` is set, the subfield's label is printed before the field,
    otherwise afterwards. The latter is useful for iterating radios or
    checkboxes.
    """
    def __call__(self, field, **kwargs):
        if 'required' not in kwargs and 'required' in getattr(field, 'flags', []):
            kwargs.setdefault('data_is_required', True)

        return super().__call__(field, **kwargs)
