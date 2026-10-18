import optionReader from './APISelect.js';
import { sendMessage } from './public_usage.js';

const Startbutton = document.getElementById('startButton');
const Loadbutton = document.getElementById('loadButton');
const HistorySelect = document.getElementById('historySelect');

const Userinput = document.getElementById('userInput');
const chatBox = document.getElementById("messageInput");
let conversation_id = 0;

Startbutton.addEventListener('click', async () => {
    Userinput.hidden = false;
    chatBox.hidden = false;
    HistorySelect.hidden = false;
    const val=optionReader();
    if (!val) {
        console.error('No provider selected. Please select a provider first.');
        return;
    }
    try {
        const response = await sendMessage(val,
            "http://localhost:8000/start_conversation");
        conversation_id = response;
        //const data = await response.json();
    } catch (e) {
        console.error('Error fetching data:', e);
    }
});
Loadbutton.addEventListener('click', async () => {
    Userinput.hidden = false;
    chatBox.hidden = false;
    HistorySelect.hidden = false;

    try{
        const history = await fetch("http://localhost:8000/load_history");
        const data = await history.json();
        HistorySelect.innerHTML = '<optgroup label="History"></optgroup>';
        const optgroup = HistorySelect.querySelector('optgroup');
        for (const item of data) {
            const option = document.createElement('option');
            option.value = `${item.AI_Model} - ${item.conversation_id}`;;
            option.textContent = `${item.AI_Model} - ${item.conversation_id}`;
            optgroup.appendChild(option);
        }
    }
    catch(e){
        console.error('Error loading history:', e);
    }
});
HistorySelect.addEventListener('change', async () => {
    // Extract the model name from the selected option    
    const choosenModel = HistorySelect.value.split(' - ')[0]; 
    const choosenConversationId = Number(HistorySelect.value.split(' - ')[1]);  
    conversation_id = choosenConversationId; // Update the global conversation_id variable 

    const data = await sendMessage(choosenConversationId, "http://localhost:8000/load_conversation");
    chatBox.innerHTML = '';
    for (const msg of data){
        const role_name = await sendMessage(msg.role_id, "http://localhost:8000/check_role_name");
        if (role_name == "user")
            appendMessage(msg.message, "user");
        else if (role_name == "system")
            appendMessage(msg.message, "agent");
    }
})

Userinput.addEventListener('keydown', async (e) => {
    if (e.key === 'Enter') {
        console.log('Enter key pressed. Sending message...');
        const userInput = Userinput.value;
        appendMessage(userInput, "user");
        Userinput.value = '';
        const role_id = await sendMessage("user", "http://localhost:8000/check_role");
        
        let the_package ={
            message:userInput,
            conversation_id:conversation_id,
            role_id:role_id,
        };

        Userinput.value = ''; // Clear the input field after pressing Enter
        const reply = await sendMessage(the_package, "http://localhost:8000/receive_message");
        appendMessage(reply, "agent");
    }
});

function appendMessage(text, role = "agent") {   // role: "user" | "agent" | "system"
  const div = document.createElement("div");
  div.className = "msg " + role;
  div.textContent = text;                         // textContent avoids HTML injection
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;       // auto-scroll to the newest message
}