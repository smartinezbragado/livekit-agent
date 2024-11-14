document.addEventListener('DOMContentLoaded', function() {
    const sendInterviewBtn = document.getElementById('sendInterview');
    const candidateEmail = document.getElementById('candidateEmail');
    const jobDescription = document.getElementById('jobDescription');
    const candidateResume = document.getElementById('candidateResume');
    const responseMessage = document.getElementById('responseMessage');

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    candidateEmail.addEventListener('input', function() {
        if (emailPattern.test(candidateEmail.value.trim())) {
            candidateEmail.classList.remove('error');
            candidateEmail.classList.add('valid');
        } else {
            candidateEmail.classList.remove('valid');
            candidateEmail.classList.add('error');
        }
    });

    sendInterviewBtn.addEventListener('click', function() {
        const email = candidateEmail.value.trim();
        const jobDesc = jobDescription.value.trim();
        const resumeFile = candidateResume.files[0];

        if (email && jobDesc && resumeFile) {
            if (!emailPattern.test(email)) {
                showMessage('Please enter a valid email address. ❌', 'error');
                return;
            }

            // Disable the button and show loading spinner
            sendInterviewBtn.disabled = true;
            sendInterviewBtn.classList.add('loading');

            // Prepare form data
            const formData = new FormData();
            formData.append('email', email);
            formData.append('job_description', jobDesc);
            formData.append('resume', resumeFile);

            // Call /talent/generate-prompt endpoint
            fetch('http://localhost:8000/api/v1/talent/generate-prompt', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Extract the generated prompt
                const systemPrompt = data.system_prompt;

                // Prepare email data
                const emailData = {
                    email: email,
                    subject: 'Your Interview Invitation',
                    content: systemPrompt
                };

                // Call /notifications/send-email endpoint
                return fetch('http://localhost:8000/api/v1/notifications/send-email', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(emailData)
                });
            })
            .then(response => response.json())
            .then(data => {
                showMessage(`Interview sent to ${email} successfully! ✅`, 'success');

                // Reset form fields
                candidateEmail.value = '';
                jobDescription.value = '';
                candidateResume.value = '';
                candidateEmail.classList.remove('valid');
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('An error occurred while sending the interview. ❌', 'error');
            })
            .finally(() => {
                // Re-enable the button
                sendInterviewBtn.disabled = false;
                sendInterviewBtn.classList.remove('loading');
            });
        } else {
            showMessage('Please fill in all fields and attach a resume. ❌', 'error');
        }
    });

    function showMessage(message, type) {
        responseMessage.textContent = message;
        responseMessage.className = type;
    }

    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Mobile menu toggle
    const menuIcon = document.getElementById('menuIcon');
    const navLinks = document.getElementById('navLinks');

    menuIcon.addEventListener('click', function() {
        navLinks.classList.toggle('active');
    });
    
    // AI Onboarding Buddy functionality
    const sendMessageBtn = document.getElementById('sendMessage');
    const userMessageInput = document.getElementById('userMessage');
    const chatWindow = document.getElementById('chatWindow');

    sendMessageBtn.addEventListener('click', sendMessage);
    userMessageInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    function sendMessage() {
        const message = userMessageInput.value.trim();
        if (message === '') return;

        // Display user message
        appendMessage('You', message);
        userMessageInput.value = '';

        // Send message to API
        fetch('http://localhost:8000/api/v1/onboarding/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            // Display AI response
            const aiMessage = data.response;
            appendMessage('AI Onboarding Buddy', aiMessage);
        })
        .catch(error => {
            console.error('Error:', error);
            appendMessage('Error', 'There was a problem communicating with the server.');
        });
    }

    // Smooth scroll to chatbot section when 'AI Onboarding' link is clicked
    const onboardingLink = document.querySelector('a[href="#onboarding"]');
    if (onboardingLink) {
        onboardingLink.addEventListener('click', function(event) {
            event.preventDefault();
            const onboardingSection = document.getElementById('ai-onboarding-buddy');
            onboardingSection.scrollIntoView({ behavior: 'smooth' });
        });
    }

    // Smooth scroll to chatbot section when 'AI Interview' link is clicked
    const interviewLink = document.querySelector('a[href="#interview"]');
    if (interviewLink) {
        interviewLink.addEventListener('click', function(event) {
            event.preventDefault();
            const interviewSection = document.getElementById('send-interview');
            interviewSection.scrollIntoView({ behavior: 'smooth' });
        });
    }

    function appendMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');

        const senderElement = document.createElement('div');
        senderElement.classList.add('message-sender');
        senderElement.textContent = sender;

        const textElement = document.createElement('div');
        textElement.classList.add('message-text');
        textElement.textContent = message;

        messageElement.appendChild(senderElement);
        messageElement.appendChild(textElement);
        chatWindow.appendChild(messageElement);

        // Scroll to the bottom of the chat window
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
});