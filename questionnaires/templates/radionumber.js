	function checkboxClicked() {
		var numberfield = document.getElementById('numberfield');
		var checkbox = document.getElementById('checkboxfield');
		if (checkbox.checked == true) {
			numberfield.value = 'fake';
			numberfield.disabled = true;
		} else {
			numberfield.value = '';
			numberfield.disabled = false;
		}
	}
	
	function numberEntered() {
		var element = document.getElementById('radiofield');
		element.checked=false;
	}