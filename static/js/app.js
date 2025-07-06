
document.addEventListener("DOMContentLoaded", function () {
    let passwordInput = document.querySelector(".check_pass");
    let confirmPasswordInput = document.querySelector(".conf_pass");
    let submitButton = document.querySelector(".btn-sub-val");

    // Disable the submit button on load
    submitButton.disabled = true;

    function verifyPassword() {
        let password = passwordInput.value;
        let confirm = confirmPasswordInput.value;

        if (password === confirm) {
            confirmPasswordInput.classList.add("is-valid");
            confirmPasswordInput.classList.remove("is-invalid");
            submitButton.disabled = false;
        } else {
            confirmPasswordInput.classList.add("is-invalid");
            confirmPasswordInput.classList.remove("is-valid");
            submitButton.disabled = true;
        }
    }

    // Attach the event handler to both input fields
    passwordInput.addEventListener("input", verifyPassword);
    confirmPasswordInput.addEventListener("input", verifyPassword);
});