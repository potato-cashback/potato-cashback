async function recieveWhatsappPhoneList() {
    var phoneList = []
    await fetch("/mongodb/phones/whatsapp")
    .then(r => r.text())
    .then(r => {
        phoneList = JSON.parse(r.split("'").join("\"").split("+").join(""))

    })
    console.log(phoneList)
    return phoneList
}


async function recieveTelegramPhoneList() {
    var phoneList = []
    await fetch("/mongodb/phones/telegram")
    .then(r => r.text())
    .then(r => {
        phoneList = JSON.parse(r.split("'").join("\""))
    })
    console.log(phoneList)
    return phoneList
}

async function sendMessagesInTelegram(message, image_URI) {
    const telegram_url = `send_message`
    
    let request = await fetch(telegram_url, {
        method:'POST',
        headers:{
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'message': message,
            'phones': await recieveTelegramPhoneList(),
            'image_URI': image_URI
        })
    })
    if (request.ok) alert('Telegram messages were sent!')
    else alert('Telegram messages were not sent!!!, somethings wrong!')
}

async function sendMessagesInWhatsapp(message, base64Image) {
    const url = 'https://whatsapp-web-potato.herokuapp.com/mail/';

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body:JSON.stringify({
                numbers: await recieveWhatsappPhoneList(),
                message: message,
                base64Image: base64Image.split(",")[1]
            })
        });
        const res = await response.text();
        console.log('Успех:', res);
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

function getMessageText() {
    return document.querySelector("#message").value;
}

function getImageURI() {
    return document.querySelector("#messageImg").src;
}

const sendMessage = async () => {
    document.querySelector("button").disabled = true;

    let message = getMessageText()
    let image_URI = getImageURI()

    if (message == '') {
        alert('Введите текст сообщения')
        return
    }

    popup("Вы уверены что хотите <strong>отправить</strong> сообщение?", async () => {
        removePopup()
        
        // await sendMessagesInTelegram(message, image_URI)
        await sendMessagesInWhatsapp(message, image_URI)
    })
}

function removePopup() {
    document.querySelector('#popup-container').style.visibility = 'hidden'
}
function popup(message, ok) {
    let container = document.querySelector('#popup-container')
    container.style.visibility = 'visible'

    container.querySelector('.popup-message').innerHTML = message

    container.querySelector('button.ok').addEventListener('click', ok)
}

(async () => {
    // Set image uploader
    window.addEventListener('load', function() {
        document.querySelector('input[type="file"]').addEventListener('change', function() {
            if (this.files && this.files[0]) {
                var reader = new FileReader();
                var img = document.querySelector('#messageImg');
                reader.onload = function(e) {
                    img.src = e.target.result;
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    });

    document.querySelector("#whatsapp-users").innerText = await recieveWhatsappPhoneList()
    document.querySelector("#telegram-users").innerText = await recieveTelegramPhoneList()
})();

