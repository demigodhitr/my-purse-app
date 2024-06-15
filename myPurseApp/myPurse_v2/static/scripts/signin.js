 function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        // get our protection cookie value, we need it to allow this request reach the appropriate domain and view function block in the backend. the function logic is written above.
        const csrftoken = getCookie('csrftoken');
        // get the loader. 
        var loader = document.getElementById("requestLoader");
        // form submit button
        var submitButton = document.getElementById("submitButton");
        submitButton.addEventListener("click", authenticateUser); 
        function authenticateUser (event) {
            event.preventDefault();
            this.style.display = "none";
            loader.style.display = "flex";
           
            var username = document.getElementById("username").value;
            var password = document.getElementById("password").value;
            const errorElement = document.getElementById("errorMessage");
            const vElement = document.getElementById("verifyEmail");
            const successElement = document.getElementById("successMessage")


            if (!username || !password) { 
                showOffcanvas('menu-request-error');
                errorElement.innerHTML = "Ghost users cannot use our platform, please enter your username and password to continue";
                document.getElementById("password").value = '';
                timeoutID = setTimeout(reset, 1300)
                return;
             }

             url = '{% url "signin" %}'
             fetch(url, {
                method: 'POST',
                body : JSON.stringify({ 'username': username, 'password': password }),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
             })
             .then(response => {
                if (!response.ok) {
                    console.log(response);
                }
                return response.json();
             })
             .then(data => {
                if (!data.success) {
                    if (data.verify){
                        verifyButton = document.getElementById('verifyButton')
                        verifyButton.addEventListener('click', function(event){
                            event.preventDefault();
                            const email = data.email;
                            var raw_url = '{% url "email_verification" "placeholder" %}'
                            var url = raw_url.replace('placeholder', email)
                            window.location.href = url;
                            
                        })
                        vElement.innerHTML = data.verify;
                        showOffcanvas('menu-request-pending');
                        setTimeout(reset, 1300);
                        return;
                    } else if (data.error){
                        if (data.disable){
                            submitButton.removeAttribute('id');
                            errorElement.innerHTML = data.error;
                            showOffcanvas('menu-request-error');
                            setTimeout(disable, 800);
                            username = username;
                            return;
                        }
                        errorElement.innerHTML = data.error;
                        showOffcanvas('menu-request-error');
                        setTimeout(reset, 1300);
                        return;
                    }
                }
                else {
                    successElement.innerHTML = data.success;
                    showOffcanvas('menu-request-ok');
                    setTimeout(function() {
                        reset();
                        window.location.href = "{% url 'home' %}";
                    }, 1300) 
                }
             })
             .catch(error => {
                console.log(error);
                showOffcanvas('menu-request-error');
                errorElement.innerHTML = error;
                setTimeout(reset, 1300);
                password = '';
                username = username;
                return;
             })

        };

        function showOffcanvas(offcanvasId) {
            var offcanvasElement = document.getElementById(offcanvasId);
            var bsOffcanvas = new bootstrap.Offcanvas(offcanvasElement);
            bsOffcanvas.show();
        }

        function reset() {
            submitButton.style.display = "block";
            loader.style.display = "none";
            }
        function disable() {
            loader.style.opacity = "0.6";
                submitButton.style.opacity = "0.5";
                setTimeout(function (){
                    submitButton.style.display = "none";
                    
                }, 5000);
            }
            document.addEventListener('DOMContentLoaded', function () {

            let deferredPrompt;

            window.addEventListener('beforeinstallprompt', (e) => {

                e.preventDefault();

                deferredPrompt = e;

                showInstallButton();
            });

            function showInstallButton() {
                const isIos = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
                const isAndroid = /Android/.test(navigator.userAgent);

                if (isIos) {
                    const iosModal = new bootstrap.Offcanvas(document.getElementById('menu-install-pwa-ios'));
                    iosModal.show();
                } else if (isAndroid) {
                    const androidModal = new bootstrap.Offcanvas(document.getElementById('menu-install-pwa-android'));
                    androidModal.show();
                }
            }

            function installPWA() {
                // Show the install prompt
                deferredPrompt.prompt();
                // Wait for the user to respond to the prompt
                deferredPrompt.userChoice.then((choiceResult) => {
                    if (choiceResult.outcome === 'accepted') {
                        console.log('User accepted the install prompt');
                    } else {
                        console.log('User dismissed the install prompt');
                    }
                    deferredPrompt = null;
                });
            }

            const installButton = document.querySelector('.pwa-install');
            if (installButton) {
                installButton.addEventListener('click', installPWA);
            }
        });