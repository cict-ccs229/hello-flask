function sendMessage(event) {
    if (event && event.key !== "Enter") return;

    let inputField = document.getElementById("userInput");
    let userMessage = inputField.value.trim();
    if (userMessage === "") return;

    let chatbox = document.getElementById("messages");

    // Display user message
    let userDiv = document.createElement("div");
    userDiv.textContent = "You: " + userMessage;
    userDiv.style.fontWeight = "bold";
    chatbox.appendChild(userDiv);

    // Fetch diagnosis from the API
    fetch(`/diagnosis?symptoms=${userMessage}`)
        .then(response => response.json())
        .then(data => {
            let botDiv = document.createElement("div");
            if (data.error) {
                botDiv.textContent = "Bot: " + data.error;
            } else if (data.message) {
                botDiv.textContent = "Bot: " + data.message;
            } else {
                botDiv.innerHTML = "Bot: Possible diseases found:<br>";
                data.forEach(disease => {
                    botDiv.innerHTML += `<strong>${disease.name}</strong> (ICD-10: ${disease.icd10_codes}) <br> 
                    <a href="${disease.info_link}" target="_blank">More info</a><br><br>`;
                });
            }
            chatbox.appendChild(botDiv);
            chatbox.scrollTop = chatbox.scrollHeight;
        });

    inputField.value = "";
}
