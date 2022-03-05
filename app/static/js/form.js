function hookOptionalFieldsets(){
	function removeFormNovalidate(){
		var forms = document.querySelectorAll("form");
		var length = forms.length;
		for (var i = 0; i < length; ++i) {
			forms[i].removeAttribute("novalidate");
		}
	}
	function prepareOptionalFieldsets(){
		var optionalParticipantFields = document.querySelectorAll("fieldset.optional-participant");
		var length = optionalParticipantFields.length;
		for (var i = 0 ; i < length; ++i) {
			var fieldset = optionalParticipantFields[i];
			if (!fieldsetHasInput(fieldset)) {
				removeRequiredAttributes(fieldset);
			}
			fieldset.addEventListener("change", changeHandler);
		}
	}
	function fieldsetHasInput(fieldset){
		var inputFields = fieldset.querySelectorAll(formElementSelector);
		var length = inputFields.length;
		for (var i = 0; i < length; ++i) {
			if (inputFields[i].value) {
				return true
			}
		}
		return false;
	}
	function addRequiredAttributes(fieldset){
		var inputFields = fieldset.querySelectorAll(formElementSelector)
		var length = inputFields.length;
		for (var i = 0; i < length; ++i) {
			var field = inputFields[i];
			if (field.getAttribute(isRequiredAttr) !== null) {
				field.setAttribute("required", true);
			}
		}
		fieldset.setAttribute(hasInputAttr, true);
	}
	function removeRequiredAttributes(fieldset){
		fieldset.setAttribute(hasInputAttr, false);
		var inputFields = fieldset.querySelectorAll(formElementSelector)
		var length = inputFields.length;
		for (var i = 0; i < length; ++i) {
			inputFields[i].removeAttribute("required");
		}
	}
	function changeHandler(event){
		/* MEMO: Handler routine for enabling and disabling required
				 status of optional participant fieldsets. */
		var fieldset = event.currentTarget;
		var inputElement = event.target;
		if (fieldset === inputElement) {
			// MEMO: Fieldset itself changed. Shouldn't happen.
			return;
		}
		var hasInput = fieldset.getAttribute(hasInputAttr).toLowerCase() === 'true';
		if (
			(!hasInput && fieldsetHasInput(fieldset))
			|| (!hasInput && inputElement.value)
		) {
			addRequiredAttributes(fieldset);
		} else if (!inputElement.value && !fieldsetHasInput(fieldset)) {
			removeRequiredAttributes(fieldset);
		}
	}

	var formElementSelector = "input,select,textarea";
	var isRequiredAttr = "data-is-required";
	var hasInputAttr = "data-has-input";
	removeFormNovalidate();
	prepareOptionalFieldsets();
}