async function recieveWhatsappPhoneList() {
    var phoneList = []
    await fetch("/mongodb/phones/whatsapp")
    .then(r => r.text())
    .then(r => {
        r = r.split("'").join("\"").split("+").join("")

        phoneList = r
        document.querySelector("details > div").innerText = r.split(",").join(",\n")
    })
    console.log(phoneList)
    return phoneList
}
async function recieveTelegramPhoneList() {
    var phoneList = []
    await fetch("/mongodb/phones/telegram")
    .then(r => r.text())
    .then(r => {
        phoneList = r.split("'").map(String).filter(str => str[0] == '+')
    })
    console.log(phoneList)
    return phoneList
}
recieveTelegramPhoneList()

const sendMessage = async () => {
    document.querySelector("button").disabled = true;
    message = document.querySelector("#message").value

    const telegram_url = `send_message`
    let request = await fetch(telegram_url, {
        method:'POST',
        headers:{
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'message': message,
            'phones': await recieveTelegramPhoneList(),
        })
    })
    if (request.ok) alert('Telegram messages were sent!')
    else alert('Telegram messages were not sent!!!, somethings wrong!')

    // const whatsapp_url = `https://whatsapp-web-potato.herokuapp.com/mail/?numbers=${await recieveWhatsappPhoneList()}&message=${message}`
    // fetch(whatsapp_url)
    // .then(async r => {
    //     if(r.ok) {
    //         alert("all good!")
    //     }else{
    //         alert(await r.text())
    //     }
    // })
    // .catch(err => {
    //     alert("Готово")
    //     window.location.href = window.location.href;
    // })
}