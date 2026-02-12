
async function sendMessage() {
    const message = document.getElementById("message").value;
    const token = localStorage.getItem("token");

    const response = await fetch("http://3.109.152.112/api/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({
            message: message
        })
    });

    const data = await response.json();
    console.log(data);
}
