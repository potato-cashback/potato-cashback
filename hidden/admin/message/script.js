var phoneList = '["77476215825"]';

fetch("/mongodb/phones/whatsapp")
.then(r => r.text())
.then(r => {
    r = r.split("'").join("\"").split("+").join("")

    phoneList = r
    document.querySelector("details > div").innerText = r.split(",").join(",\n")
})

const sendMessage = () => {
    document.querySelector("button").disabled = true;
    message = document.querySelector("#message").value

    const url = `https://whatsapp-web-potato.herokuapp.com/mail/?numbers=${phoneList}&message=${message}`

    fetch(url)
    .then(async r => {
        if(r.ok) {
            alert("all good!")
        }else{
            alert(await r.text())
        }
    })
    .catch(err => {
        alert("Готово")
        window.location.href = window.location.href;
    })
}