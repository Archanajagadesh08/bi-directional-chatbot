 //handle user registration
 const registerForm = document.getElementById('registerForm');
 registerForm.addEventListener("submit",async(event)=>{
  event.preventDefault();
  const username = document.getElementById('username').value;
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirm_password').value;
  try{
    //send registration details to the server
    const response = await fetch ('http://127.0.0.1:8000/auth/register',{
      method:'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body:JSON.stringify({
        username: username,
        email: email,
        password: password,
        confirm_password: confirmPassword
      })
    });
    const data = await response.json();
    if (!response.ok){
      alert(data.detail || 'Registeration failed');
      return;
    }
    //show success message and redirect to login
    alert('Registration successful! Please login.');
    window.location.href = '/';
  } catch(error){
console.error('Registration error:',error);
alert('Unable to connect to server');
  }
 });
 //toggle password visibility 
 const passwordInput = document.getElementById('password');
            const confirmPasswordInput = document.getElementById('confirm_password');
            const togglePassword = document.getElementById('togglePassword');
            const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');

            togglePassword.addEventListener('click', () => {
              passwordInput.type = passwordInput.type === 'password' ? 'text' : 'password';
            });
            toggleConfirmPassword.addEventListener('click', () => {
              confirmPasswordInput.type = confirmPasswordInput.type === 'password' ? 'text' : 'password';
            });