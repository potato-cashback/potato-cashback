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


function deletePollItem(e) {
    let pollItem = e.target.parentNode
    let poll = document.querySelector('#poll-list')

    let tagName = e.target.tagName.toLowerCase()
    switch (tagName) {
        case 'button':
            poll.removeChild(pollItem)
            break;
        case 'input':
            let input = pollItem.querySelector('.poll-item-message')
            if (input.value == '') {
                poll.removeChild(pollItem)
            }
            break;
    }
}

function newPollItem(e) {
    let input = e.target
    let poll = document.querySelector('#poll-list')
    let imgDeleteHtml = `<img src="https://img.icons8.com/fluency-systems-regular/14/000000/multiply.png"/>`
    
    let deletePollButton = document.createElement('button')
    deletePollButton.classList.add('poll-item-buttons')
    deletePollButton.addEventListener('click', deletePollItem)
    deletePollButton.innerHTML = imgDeleteHtml

    // Configure input to normal poll-item-message
    input.classList.remove('add-new-poll')
    input.placeholder = ''
    input.parentNode.appendChild(deletePollButton)
    input.addEventListener('input', deletePollItem)

    let newInput = document.createElement('input')
    newInput.classList.add('add-new-poll', 'poll-item-message')
    newInput.placeholder = 'Добавить новую опцию'
    newInput.addEventListener('input', newPollItem, { once: true })

    let pollItem = document.createElement('li')
    pollItem.classList.add('poll-item')
    pollItem.appendChild(newInput)

    poll.appendChild(pollItem)
}

async function sendPollsInTelegram(message, options) {
    const telegram_url = `send_poll`
    try {
        const response = await fetch(telegram_url, {
            method:'POST',
            headers:{
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'question': message,
                'options': options,
                'phones': await recieveTelegramPhoneList(),
            })
        })
        const res = await response.text();
        console.log('Успех:', res);
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

function getMessageText() {
    return document.querySelector("#message").value;
}

function getPollOptions() {
    let pollItems = document.querySelectorAll('.poll-item')
    let pollOptions = []

    pollItems.forEach(function(pollItem) {
        let input = pollItem.querySelector('.poll-item-message')
        let text = input.value
        if (text != '') {
            pollOptions.push(text)
        }
    })
    console.log(pollOptions)
    return pollOptions
}

const sendMessage = async () => {
    document.querySelector("button").disabled = true;

    let message = getMessageText()
    let pollOptions = getPollOptions()

    if (message == '') {
        alert('Введите текст вопроса')
        return
    }
    if (pollOptions == []) {
        aler('Введите опции')
        return
    }

    popup("Вы уверены что хотите <strong>отправить</strong> этот опрос?", async () => {    
        removePopup()
        
        await sendPollsInTelegram(message, pollOptions)
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
    document.querySelector('.add-new-poll').addEventListener('input', newPollItem, { once: true })
    document.querySelector("#telegram-users").innerText = await recieveTelegramPhoneList()
})();