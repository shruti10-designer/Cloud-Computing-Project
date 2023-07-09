function validateForm() {
    var form = document.getElementById("health-form");
    var weight = parseFloat(form.elements["Weight"].value);
    var height = parseFloat(form.elements["Height"].value);

    if (isNaN(weight) || isNaN(height)) {
        alert("Please enter valid values for weight and height");
        return false;
    }

    if (form.checkValidity()) {
        return true;
    } else {
        alert("Please fill out all required fields");
        return false;
    }
}