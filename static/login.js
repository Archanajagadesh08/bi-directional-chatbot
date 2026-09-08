 //handle user login
 const loginForm = document.getElementById("loginForm");
 loginForm.addEventListener("submit",async(event)=>{
    event.preventDefault();
    const email =  document.getElementById("email").value;
    const password = document.getElementById("password").value;
    try{
        //send login credentials to the server
        const response = await fetch("http://127.0.0.1:8000/auth/login",{
            method: "POST",
            headers:{
                "content-type": "application/json"
            },
            body: JSON.stringify({
                email:email,
                password: password
            })
        });
        const data = await response.json();
        if (!response.ok){
            alert(data.detail||"Login failed");
            return;
        }
        //store access token and redirect to the chat page 
        localStorage.setItem("access_token",data.access_token);
        window.location.href = "/";
    } catch(error)
    {
        console.error("Login error:",error);
        alert("Unable to connect to server");
    }
 });
 //Toggle password visibility
 const passwordInput = document.getElementById('password');
            const togglePasswordButton = document.getElementById('togglePassword');

            togglePasswordButton.addEventListener('click', ()=> {
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    togglePasswordButton.textContent = '👁️';
                    togglePasswordButton.setAttribute('aria-label', 'Hide password');
                } else {
                    passwordInput.type = 'password';
                    togglePasswordButton.textContent = '👁️';
                    togglePasswordButton.setAttribute('aria-label', 'Show password');
                }
            });
            