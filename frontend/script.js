/*********************************
 * THEME TOGGLE
 *********************************/
function toggleTheme() {
    document.body.classList.toggle("dark");
}

/*********************************
 * HELPER: GET & VALIDATE USER ID
 *********************************/
function getUserIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    const userId = params.get("user_id");

    if (!userId) {
        alert("User ID missing in URL");
        throw new Error("User ID missing");
    }

    if (!/^[a-fA-F0-9]{24}$/.test(userId)) {
        alert("Invalid user ID format");
        throw new Error("Invalid user ID");
    }

    return userId;
}

/*********************************
 * RESUME UPLOAD
 *********************************/
async function uploadResume() {
    const fileInput = document.getElementById("resumeFile");
    const result = document.getElementById("result");
    const spinner = document.getElementById("spinner");

    if (!fileInput.files.length) {
        result.innerText = "Please select a PDF file";
        return;
    }

    const userId = getUserIdFromURL();

    spinner.classList.remove("hidden");
    result.innerText = "";

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const res = await fetch(
            `http://127.0.0.1:8000/upload-resume/?user_id=${userId}`,
            {
                method: "POST",
                body: formData
            }
        );

        const data = await res.json();

        if (data.error) throw new Error(data.error);

        result.innerText = `📄 Resume Score: ${data.resume_score}`;
    } catch (err) {
        alert(err.message);
        result.innerText = "Error uploading resume";
    } finally {
        spinner.classList.add("hidden");
    }
}

/*********************************
 * INTERVIEW SUBMISSION
 *********************************/
async function submitAnswer() {
    const answer = document.getElementById("answer").value.trim();
    const score = document.getElementById("score");
    const spinner = document.getElementById("spinner");

    if (!answer) {
        score.innerText = "Please enter an answer";
        return;
    }

    const userId = getUserIdFromURL();

    spinner.classList.remove("hidden");
    score.innerText = "";

    try {
        const res = await fetch("http://127.0.0.1:8000/interview/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                user_id: userId,
                answer: answer
            })
        });

        const data = await res.json();

        if (data.error) throw new Error(data.error);

        score.innerText = `🎤 Interview Score: ${data.interview_score}`;
    } catch (err) {
        alert(err.message);
        score.innerText = "Error submitting interview";
    } finally {
        spinner.classList.add("hidden");
    }
}

/*********************************
 * LOGIN VALIDATION + REDIRECT
 *********************************/
async function validateLogin() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    const emailError = document.getElementById("emailError");
    const passwordError = document.getElementById("passwordError");
    const card = document.getElementById("loginCard");

    emailError.innerText = "";
    passwordError.innerText = "";

    let valid = true;

    if (!email) {
        emailError.innerText = "Email field cannot be empty";
        valid = false;
    } else if (!email.includes("@") || !email.includes(".")) {
        emailError.innerText = "Please enter a valid email address";
        valid = false;
    }

    if (!password) {
        passwordError.innerText = "Password field cannot be empty";
        valid = false;
    }

    if (!valid) {
        card.classList.remove("shake");
        void card.offsetWidth;
        card.classList.add("shake");
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:8000/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();
        console.log("LOGIN RESPONSE:", data);

        if (!data.success) {
            alert(data.message || "Login failed");
            return;
        }

        if (!data.user_id) {
            alert("Login failed: user_id missing");
            return;
        }

        // ✅ SUCCESS
        window.location.href =
            `dashboard.html?user_id=${data.user_id}`;

    } catch (err) {
        console.error(err);
        alert("Server error. Please try again.");
    }
}

/*********************************
 * PASSWORD VISIBILITY TOGGLE
 *********************************/
function togglePassword() {
    const passwordInput = document.getElementById("password");
    const toggleIcon = document.querySelector(".toggle-password");

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        toggleIcon.innerText = "🙈";
    } else {
        passwordInput.type = "password";
        toggleIcon.innerText = "👁";
    }
}
function checkPasswordStrength() {
    const password = document.getElementById("password").value;
    const strengthText = document.getElementById("strengthText");
    const strengthFill = document.getElementById("strengthFill");

    let strength = 0;

    if (password.length > 5) strength++;
    if (password.match(/[A-Z]/)) strength++;
    if (password.match(/[0-9]/)) strength++;
    if (password.match(/[^A-Za-z0-9]/)) strength++;

    const width = strength * 25;
    strengthFill.style.width = width + "%";

    if (strength <= 1) {
        strengthText.innerText = "Weak";
        strengthFill.style.background = "red";
    } else if (strength === 2) {
        strengthText.innerText = "Medium";
        strengthFill.style.background = "orange";
    } else {
        strengthText.innerText = "Strong";
        strengthFill.style.background = "green";
    }
}
