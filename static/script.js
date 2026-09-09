//get DOM elements 
const sendButton = document.getElementById("sendButton");
const chatBox = document.getElementById("chatBox");
const changeModeButton = document.getElementById("changeModeButton");
const modelSelection = document.querySelector(".mode-selection");
const logoutButton = document.getElementById("logoutButton");
//handle file attachments
const attachButton = document.getElementById("attachButton");
const fileInput = document.getElementById("fileInput");
const filePreview = document.getElementById("attachmentPreview")
//open the file picker when the attachment button is clicked
attachButton.addEventListener("click", () => {
    fileInput.click();
});
//display a preview when the user select a file
fileInput.addEventListener("change", () => {
    //check whether a file has been selected
    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        filePreview.innerHTML = `
                <div class="attachment-item">
                    <img src ="${URL.createObjectURL(file)}"alt="selected image">
                    <div class ="attachment-info">
                        <span>${file.name}</span>
                        <button type="button" id="removeFile">X</button>
                    </div>
                </div>`;
        filePreview.style.display = "block";
        //remove the selected file and hide its preview
        document.getElementById("removeFile").addEventListener("click", () => {
            fileInput.value = "";
            filePreview.innerHTML = "";
            filePreview.style.display = "none";
        });

    }
});
let socket;
let typingMessage = null;
let conversationID = null;
//Establish a websocket connection with the backend
function connectWebSocket() {
    const token = localStorage.getItem("access_token");
    if ((!token)){
        console.error("No access token found");
        return;
    }
    socket = new WebSocket(`ws://127.0.0.1:8000/ws?token=${token}`);
    //Handle websocket connection errors
    socket.onopen = () => {
        console.log("Webdocket connected");
        sendButton.disabled = false;
    };
    socket.onerror = (error) => {
        console.error("websocket error:", error);
    };
    //reconnect automatically if the websocket connection is closed
    socket.onclose = (event) => {
        console.log(
            "websocket disconnected:", event.code, event.reason
        );
        sendButton.disabled = true;
        //setTimeout(connectWebSocket, 1000);
    };
//format the Gemini response into readable HTML
    function formatGeminiResponse(text) {
        text = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            //store code blocks separetely to prevent formatting from modifying them
        const codeBlocks = [];
//Extract code blocks and temporarily replace them with placeholders
        text = text.replace(/```(?:python|javascript|js|html|css)?\s*([\s\S]*?)```/g,
            (match, code) => {
                const index = codeBlocks.length;
                codeBlocks.push(
                    `<pre><code>${code.trim()}</code></pre>`);

                return `___CODE_BLOCK_${index}___`;

            }
        );//convert Markdown heading into HTML headings
        text = text.replace(/^###(.*)$/gm, "<h3>$1</h3>");
        text = text.replace(/^##(.*)$/gm, "<h2>$1</h2>");
        text = text.replace(/^#(.*)$/gm, "<h1>$1</h1>");
        text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        text = text.replace(/\*(.*?)\*/g, "<em>$1</em>");
        //Preserve line breaks in the formatted response
        text = text.replace(/\n/g, "<br>");
        //reestore the orgininal code block in their placeholders
        codeBlocks.forEach((code, index) => {
            text = text.replace(`___CODE_BLOCK_${index}___`, code
            );
        });
        return text;
    }
//Handle response received from the backend 
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        conversationID = data.conversationid;
        //remove the typing indicator when the reponse arrives
        if (typingMessage) {
            typingMessage.remove();
            typingMessage = null;
        }
//Create and display the assistant's response message
        const botMessage = document.createElement("div");
        botMessage.className = "message bot-message";
        botMessage.innerHTML = `<div class ="message-label">Assistant</div>
                <div class ="message-text"> ${formatGeminiResponse(data.response)} </div>`;
        chatBox.appendChild(botMessage);
        chatBox.scrolltop = chatBox.scrollHeight;
    };
}
connectWebSocket();
sendButton.addEventListener("click", async () => {
    const message = userInput.value.trim();
    const file = fileInput.files && fileInput.files.length > 0 ? fileInput.files[0] : null;
    
     //prevent sending a message before selecting a mode
    if (!selectedMode) {
        return;
    }//Ignore the request if both message and file are empty
    if (!message && !file) {
        return;
    }// display the user's message and selected file in the chat
    if (message || file) {
        const userMessage = document.createElement("div");
        userMessage.className = "message user-message";
        let content = `<div class ="message-label">You</div>`;
        if (message) {
            content += `<div class ="message-text"> ${message}</div>`;
        }
        if (file) {//display image files as a preview
            if (file.type.startsWith("image/")) {
                const imageData = await new Promise((resolve, reject) => {
                    //convert the selected image into a data URL for preview
                    const reader = new FileReader();
                    reader.onload = () => resolve(reader.result);
                    reader.onerror = () => reject(reader.error);
                    reader.readAsDataURL(file);
                });
                content += `<div class ="message-attachment">
                            <img src ="${imageData}" alt ="${file.name}" class ="sent-image">
                            <div class="file-name">${file.name}</div>
                            </div>
                            `;
            }// display non-image files with a file icon and filename
            else {
                content += `<div class="message-attachment">
                            <div class= "file-icon">📎</div>
                            <div class ="file-name">${file.name}</div>
                            </div>`;
            }

        }
        userMessage.innerHTML = content;
        chatBox.appendChild(userMessage);
        chatBox.scrollTop = chatBox.scrollHeight;

    }

    if ((message || file) && socket.readyState == WebSocket.OPEN) {
        let fileData = null;
        if (file) {
            console.log("IMAGE SELECTED:", file.name, file.type, file.size);
            console.log("FILE:", file);
            console.log("IS FILE:", file instanceof File);
            //convert the selected file into binary data for transmission
            const buffer = await file.arrayBuffer();
            const bytes = new Uint8Array(buffer);
            let binary = "";
            //process the file in chuncks to safely handle large files
            const chunkSize = 8192;
            //convert the binary data into a string in managable chunks
            for (let i = 0; i < bytes.length; i += chunkSize) {
                binary += String.fromCharCode(

                    ...bytes.subarray(i, i + chunkSize)
                );
            }//prepare file metadata and encoded data for the backend
            fileData = {
                name: file.name,
                type: file.type,
                data: btoa(binary)
            };


        }//Show a typing indicator while waiting for the assistant response
        typingMessage = document.createElement("div");
        typingMessage.className = "message bot-message";
        typingMessage.innerHTML = `<div class ="message-label">Assistant</div>
                        <div class="message-text">Typing..</div>`;
        chatBox.appendChild(typingMessage);
        chatBox.scrollTop = chatBox.scrollHeight;
        //send the message,file data,send selected mode to the backend
        socket.send(JSON.stringify({
            message: message,
            file: fileData,
            mode: selectedMode,
            conversationid : conversationID
        }));
    }
    //clear the input fields and file preview after sending
    userInput.value = "";
    fileInput.value = "";
    filePreview.innerHTML = "";
    filePreview.style.display = "none";
});
//create the mode welcome message
const modeWelcome = document.createElement("div");
modeWelcome.className = "mode-welcome";
modeWelcome.style.display = "none";
document.querySelector(".chat-box").appendChild(modeWelcome);
//store the currently selected chatbot mode
let selectedMode = null;
//get elements required for chatbot mode selection
const modeSelection = document.querySelector(".mode-selection");
const modeButtons = document.querySelectorAll(".mode-button");
const inputArea = document.querySelector(".input-area");
const userInput = document.getElementById("userInput");
//Hide the input area until a mode is selected
inputArea.style.display = "none";
//enter key press should also send the message
userInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
       sendButton.click();
    }
});
//handle chatbot selection
modeButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        modeButtons.forEach(b => {
            //removes the selected state from other mode buttons
            b.classList.remove("selected");
        });
        btn.classList.add("selected");
        selectedMode = btn.dataset.mode;
        console.log("Selected mode:", selectedMode);
        //replace the mode selection screen with the welcome message
        modeSelection.style.display = "none";
        modeWelcome.style.display = "block";
        //display the selected mode and provide an options to change it
        modeWelcome.innerHTML = `<div class="mode-status">
        <div class="mode info"><span class="mode-status-icon">${getModeIcon(selectedMode)}</span>
        <span class="mode-status-text">${selectedMode.charAt(0).toUpperCase() + selectedMode.slice(1)} Mode</span>
        </div>
        </div>`;
        inputArea.style.display = "flex";
        userInput.focus();
    });
});
changeModeButton.addEventListener("click",changeMode);
//reset the chat and return to the mode selection screen
function changeMode() {
    //clear the pervious chat messages when switching modes
    chatBox.querySelectorAll(".message").forEach(message =>{message.remove();});
    modeWelcome.style.display = "none";
    modeSelection.style.display = "block";
    inputArea.style.display = "none";
    selectedMode = null;
    modeButtons.forEach(btn => {
        btn.classList.remove("selected");
    });
}
//return an icorn based on the selected mode
function getModeIcon(mode) {
    const modekey = mode
    .trim()
    .toLowerCase()
    .replace(/\s+mode$/,"");
    const icons = {
        coding: "mdi:code-tags",
        writing: "mdi:lead-pencil",
        study: "mdi:book-open-page-variant",
        research: "mdi:magnify",
        general: "mdi:message-text"
    };
    //Normalixe the mode name so it matches the icon mapping
    const icon = icons[modekey];
    console.log("mode:",mode);
    console.log("mode key:",modekey);
    console.log("Icon:",icon);
    return `<iconify-icon icon="${icon}"></iconify-icon>`;
}
//logout button 
logoutButton.addEventListener("click",()=>{
    if (socket && socket.readyState === WebSocket.OPEN){
        socket.close();
    }
    //remove the JWT access token
    localStorage.removeItem("access_token");
    //Return to the login page
    window.location.href ='/login';
});