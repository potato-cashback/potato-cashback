var uploadField = document.querySelector("#message-image-container > input[type=file]");

uploadField.onchange = function() {
    if(this.files[0].size >  1048576){
       alert("File is more than 1mb. Too big!");
       this.value = "";
    };
};

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

async function sendMessagesInTelegram(message, base64Image) {
    const telegram_url = `send_telegram_message`
    console.log("hello?", base64Image)
    try {
        const response = await fetch(telegram_url, {
            method:'POST',
            headers:{
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'message': message,
                'phones': await recieveTelegramPhoneList(),
                'base64Image': base64Image
            })
        })
        const res = await response.text();
        console.log('Успех:', res);
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

async function sendMessagesInWhatsapp(message, base64Image) {
    const url = 'send_whatsapp_message';

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body:JSON.stringify({
                'numbers': await recieveWhatsappPhoneList(),
                'message': message,
                'base64Image': base64Image
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

function getBase64Image() {
    let src = document.querySelector("#messageImg").src;
    return (src.substring(0, 4) == 'data' ? src.split(",")[1]: '#');
}

const sendMessage = async () => {
    document.querySelector("button").disabled = true;

    let message = getMessageText()
    let base64Image = getBase64Image()

    console.log(base64Image)
    if (message == '') {
        alert('Введите текст сообщения')
        return
    }

    popup("Вы уверены что хотите <strong>отправить</strong> сообщение?", async () => {    
        removePopup()
        
        await sendMessagesInTelegram(message, base64Image)
        await sendMessagesInWhatsapp(message, base64Image)
    })
}

function removePopup() {
    document.querySelector('#popup-container').style.visibility = 'hidden'
}
function popup(message, ok) {
    let container = document.querySelector('#popup-container')
    let buttonOk = container.querySelector('button.ok')
    container.style.visibility = 'visible'

    container.querySelector('.popup-message').innerHTML = message

    buttonOk.addEventListener('click', ok, { once: true })
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
                    resizeImage()
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    });

    document.querySelector("#whatsapp-users").innerText = await recieveWhatsappPhoneList()
    document.querySelector("#telegram-users").innerText = await recieveTelegramPhoneList()
})();

const resizeImage = () => {
    let canvas = document.getElementsByTagName('canvas')[0];
    let ctx = canvas.getContext('2d');
    let image = document.querySelector('#messageImg');

    canvas.height = 512 * (image.naturalHeight / image.naturalWidth);
    canvas.width = 512;

    ctx.drawImage(image, 0, 0, canvas.width, canvas.height);

    image.src = canvas.toDataURL()
}