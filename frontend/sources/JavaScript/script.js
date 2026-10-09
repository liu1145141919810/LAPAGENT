const button = document.getElementById('startButton');
const feedback = document.getElementById('feedback');

button.addEventListener('click', async () => {
    //console.log('Button clicked');
    feedback.textContent = 'Waiting...';
    try {
        const response = await fetch("http://localhost:8000");
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        feedback.textContent = data.message;
    } catch (e) {
        feedback.textContent = 'Error occurred.';
    }
});