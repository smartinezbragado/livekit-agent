document.addEventListener('DOMContentLoaded', function() {
    const sendInterviewBtn = document.getElementById('sendInterview');
    const candidateEmail = document.getElementById('candidateEmail');
    const jobDescription = document.getElementById('jobDescription');
    const responseMessage = document.getElementById('responseMessage');

    sendInterviewBtn.addEventListener('click', function() {
        const email = candidateEmail.value.trim();
        const jobDesc = jobDescription.value.trim();

        if (email && jobDesc) {
            // Basic email validation
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if (!emailPattern.test(email)) {
                showMessage('Please enter a valid email address. ❌', 'error');
                return;
            }

            // Simulate sending interview (You can replace this with actual AJAX call)
            setTimeout(function() {
                showMessage(`Interview sent to ${email} for the position: "${jobDesc}"! ✅`, 'success');
                candidateEmail.value = '';
                jobDescription.value = '';
            }, 1000);
        } else {
            showMessage('Please fill in both fields. ❌', 'error');
        }
    });

    function showMessage(message, type) {
        responseMessage.textContent = message;

        if (type === 'success') {
            responseMessage.classList.remove('error');
            responseMessage.classList.add('success');
        } else {
            responseMessage.classList.remove('success');
            responseMessage.classList.add('error');
        }
    }
});