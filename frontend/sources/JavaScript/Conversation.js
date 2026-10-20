import optionReader from './APISelect.js';
import { sendMessage,AddBase } from './public_usage.js';

const Startbutton = document.getElementById('startButton');
const Loadbutton = document.getElementById('loadButton');
const HistorySelect = document.getElementById('historySelect');

let Userinput = document.getElementById('userInput');
const chatBox = document.getElementById("messageInput");
const chatContainer =document.getElementById("messagesContainer");
const closeChatButton = document.getElementById("closeChatButton");
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
            AddBase("start_conversation"));
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
        const history = await fetch(AddBase("load_history"));
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

    const data = await sendMessage(choosenConversationId, AddBase("load_conversation"));
    
    chatContainer.innerHTML = ''; // Clear previous messages

    for (const msg of data){
        const role_name = await sendMessage(msg.role_id, AddBase("check_role_name"));
        if (role_name == "user")
            appendMessage(msg.message, "user");
        else if (role_name == "system")
            appendMessage(msg.message, "agent");
    }
})

Userinput.addEventListener('keydown', async (e) => {
    InputKeydownHandler(e);
});
async function  InputKeydownHandler(e) {
       if (e.key === 'Enter') {
        console.log('Enter key pressed. Sending message...');
        const userInput = Userinput.value;
        appendMessage(userInput, "user");
        Userinput.value = '';
        const role_id = await sendMessage("user", AddBase("check_role"));
        
        let the_package ={
            message:userInput,
            conversation_id:conversation_id,
            role_id:role_id,
        };

        Userinput.value = ''; // Clear the input field after pressing Enter
        const reply = await sendMessage(the_package, AddBase("receive_message"));
        appendMessage(reply, "agent");
    }
}

function appendMessage(text, role = "agent") {   // role: "user" | "agent" | "system"
  // Create wrapper
  const wrapper = document.createElement("div");
  wrapper.className = "msg-wrapper " + role;
  
  // Create avatar
  const avatar = document.createElement("div");
  avatar.className = "avatar " + role;
  if (role === "user") {
    avatar.textContent = "U";  // User avatar
  } else if (role === "agent") {
    avatar.textContent = "AI"; // Agent avatar
  } else {
    avatar.textContent = "⚙";  // System avatar
  }
  
  // Create message bubble
  const msg = document.createElement("div");
  msg.className = "msg";
  msg.textContent = text;  // textContent avoids HTML injection
  
  // Assemble
  wrapper.appendChild(avatar);
  wrapper.appendChild(msg);
  chatContainer.appendChild(wrapper);
  chatContainer.scrollTop = chatContainer.scrollHeight;  // auto-scroll to the newest message
}

closeChatButton.addEventListener("click", () => {
    chatBox.hidden = true;
    Userinput.hidden = true;
    HistorySelect.hidden = true;
    chatContainer.innerHTML = ''; // Clear previous messages

    const response = sendMessage(conversation_id, AddBase("delete_conversation"));
    console.log(`Operation feedback: ${response} `);
});