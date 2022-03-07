function hookOptionalFieldsets(){
	function removeFormNovalidate(){
		/* MEMO: Remove novalidate attribute as it is only needed if javascript is disabled. */
		var forms = document.querySelectorAll("form");
		var length = forms.length;
		for (var i = 0; i < length; ++i) {
			forms[i].removeAttribute("novalidate");
		}
	}
	function prepareOptionalFieldsets(){
		/* MEMO: Remove the required attributes from optional form fieldset. */
		var optionalParticipantFields = document.querySelectorAll("fieldset.optional-participant");
		var length = optionalParticipantFields.length;
		for (var i = 0 ; i < length; ++i) {
			var fieldset = optionalParticipantFields[i];
			if (!fieldsetHasInput(fieldset)) {
				removeRequiredAttributes(fieldset);
				removeLabelRequiredAttributes(fieldset);
			}
			fieldset.addEventListener("change", changeHandler);
		}
	}
	function fieldsetHasInput(fieldset){
		/* MEMO: Check if the fieldset has any input. */
		var inputFields = fieldset.querySelectorAll(formInputSelector);
		var length = inputFields.length;
		for (var i = 0; i < length; ++i) {
			if (inputFields[i].value) {
				return true
			}
		}
		return false;
	}
	function addInputRequiredAttributes(fieldset){
		/* MEMO: Add required attribute to all input elements. */
		var inputFields = fieldset.querySelectorAll(formInputSelector);
		var length = inputFields.length;
		for (var i = 0; i < length; ++i) {
			var field = inputFields[i];
			if (field.getAttribute(isRequiredAttr) !== null) {
				field.setAttribute("required", true);
			}
		}
		fieldset.setAttribute(hasInputAttr, true);
	}
	function addLabelRequiredAttributes(fieldset){
		/* MEMO: Add a marker attribute to all labels that are required to make CSS work. */
		var labelFields = fieldset.querySelectorAll(formLabelSelector);
		var length = labelFields.length;
		for (var i = 0; i < length; ++i) {
			var field = labelFields[i];
			if (field.getAttribute(isRequiredAttr) !== null) {
				field.setAttribute("label-required", true);
			}
		}
	}
	function removeRequiredAttributes(fieldset){
		fieldset.setAttribute(hasInputAttr, false);
		var inputFields = fieldset.querySelectorAll(formInputSelector)
		var length = inputFields.length;
		for (var i = 0; i < length; ++i) {
			inputFields[i].removeAttribute("required");
		}
	}
	function removeLabelRequiredAttributes(fieldset) {
		var labelFields = fieldset.querySelectorAll(formLabelSelector);
		var length = labelFields.length;
		for (var i = 0; i < length; ++i) {
			labelFields[i].removeAttribute("label-required");
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
			addInputRequiredAttributes(fieldset);
			addLabelRequiredAttributes(fieldset);
		} else if (!inputElement.value && !fieldsetHasInput(fieldset)) {
			removeRequiredAttributes(fieldset);
			removeLabelRequiredAttributes(fieldset);
		}
	}
	var formInputSelector = ".form input,select,textarea";
	var formLabelSelector = ".form label[data-is-required]";
	var isRequiredAttr = "data-is-required";
	var hasInputAttr = "data-has-input";
	prepareOptionalFieldsets();
	removeFormNovalidate();
}