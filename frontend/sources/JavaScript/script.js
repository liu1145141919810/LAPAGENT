const button = document.getElementById('startButton');
const feedback = document.getElementById('feedback');
const input = document.getElementById('userInput');

async function sendMessage(userMessage){
    const response = await fetch("http://localhost:8000/receive_message", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: userMessage })
    });
    const ResponseData = await response.json();
    backinfo = ResponseData.reply;
    if (backinfo != userMessage) {
        console.log('Meeting some error')
    }
    //else console.log('Message sent successfully');
    }

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
input.addEventListener('keydown', async (e) => {
    if (e.key === 'Enter') {
        const userInput = input.value;
        //console.log('User input:', userInput);
        sendMessage(userInput);
        input.value = ''; // Clear the input field after pressing Enter
    }
});