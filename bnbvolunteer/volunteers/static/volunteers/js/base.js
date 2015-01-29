$( ".datetimeEntry" ).keydown(function(e){
  var key = e.keyCode;
  var isValidkeys = [16, 191, 189, 111, 191, 109, 186];
  var keyIsValid = false;
  for (isValid in isValidkeys){
  	if (key === isValid){
  		keyIsValid = true;
  	}
  }
  if ((key >= 96 && key <= 105) || (key >= 48 && key <= 57) || keyIsValid) { //keyCode checks which character the user is entering
    // Do nothing (for some reason, doing ![the statement in the 'if' statement] wasn't working...)
  }else{
    e.preventDefault(); //prevents anything other than a number or [/ or - or shift or ; (for :)] to be entered
  }
});

$( ".onlyNumbersEntry" ).keydown(function(e){
  var key = e.keyCode;
  if ((key >= 96 && key <= 105) || (key >= 48 && key <= 57)) { //keyCode checks which character the user is entering
    // Do nothing (for some reason, doing ![the statement in the 'if' statement] wasn't working...)
  }else{
    e.preventDefault(); //prevents anything other than a number or [/ or -] to be entered
  }
});

$( ".phoneNumberEntry" ).keydown(function(e){
  phonekeyEntryFunction(e.keyCode);
});

$( "#id_phone" ).keydown(function(e){
  phonekeyEntryFunction(e.keyCode);
});

function phonekeyEntryFunction(key){
  var isValidKeys = [16, 191, 189, 109];
  var keyIsValid = false;
  for (isValid in isValidKeys){
  	if (key === isValid){
  		keyIsValid = true;
  	}
  }
  if ((key >= 96 && key <= 105) || (key >= 48 && key <= 57) || keyIsValid) { //keyCode checks which character the user is entering
    // Do nothing (for some reason, doing ![the statement in the 'if' statement] wasn't working...)
  }else{
    e.preventDefault(); //prevents anything other than a number or [/ or - or shift (for parentheses if they want)] to be entered
  }
}