/* due_book/static/js/register.js */

/* ========================================
   DUE Book - Register Form JavaScript
   ======================================== */

// Toggle Password Visibility
function togglePassword(fieldId) {
  const field = document.getElementById(fieldId);
  const button = field.parentElement.querySelector(".password-toggle i");

  if (field.type === "password") {
    field.type = "text";
    button.classList.remove("fa-eye");
    button.classList.add("fa-eye-slash");
  } else {
    field.type = "password";
    button.classList.remove("fa-eye-slash");
    button.classList.add("fa-eye");
  }
}

// Form Validation (UI-ONLY)
document
  .getElementById("registerForm")
  .addEventListener("submit", function (e) {
    e.preventDefault(); // Ngăn submit thật (UI-ONLY)

    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm_password").value;

    // Kiểm tra mật khẩu khớp
    if (password !== confirmPassword) {
      alert("❌ Mật khẩu xác nhận không khớp!");
      return;
    }

    // Kiểm tra độ dài mật khẩu
    if (password.length < 6) {
      alert("❌ Mật khẩu phải có ít nhất 6 ký tự!");
      return;
    }

    // UI-ONLY: Hiển thị thông báo test
    alert(
      "✅ Form đăng ký hoạt động tốt! (UI-ONLY)\n\nSprint tiếp theo sẽ kết nối Backend.",
    );
  });

// Real-time Password Match Validation
document
  .getElementById("confirm_password")
  .addEventListener("input", function () {
    const password = document.getElementById("password").value;
    const confirmPassword = this.value;

    if (confirmPassword && password !== confirmPassword) {
      this.style.borderColor = "#ef4444";
    } else if (confirmPassword && password === confirmPassword) {
      this.style.borderColor = "#10b981";
    } else {
      this.style.borderColor = "#e2e8f0";
    }
  });