async function sendMessage(userMessage,address){
    console.log("Sending message", userMessage, "to address:", address);
    const response = await fetch(address, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: userMessage })
    });
    const ResponseData = await response.json();
    const backinfo = ResponseData.reply;
    //else console.log('Message sent successfully');
    return backinfo;
    }
export {sendMessage};