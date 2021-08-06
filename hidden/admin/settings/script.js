let stop_bot = document.querySelector('#stop_bot')

let groupChatId = document.querySelector('#groupChatId')
let token = document.querySelector('#bot-token')
let uri = document.querySelector('#mongo-uri')

let cashback_friends = document.querySelector('#cashback-friends')
let welcome_cashbask = document.querySelector('#welcome-cashback')
let limit_cashback = document.querySelector('#max-limit-cashback')

let change = {
    '$set': {},
    '$delete': {},
}
let sectionId = 0
let itemId = 0
let sectionName = ['Товары для дома', 'Игршуки']

function onChange(e) {
    let tag = e.target

    key = tag.getAttribute('json-key')
    
    let value
    switch (tag.tagName) {
        case "INPUT": {
            value = tag.checked
            break;
        }
        case "DIV": {
            value = +tag.innerText || tag.innerText
            break;
        }
    }
    change['$set'][key] = value
}

function addPercents() {
    let list_percents = document.querySelector('#cashback-percent')

    let id = list_percents.querySelectorAll('li').length - 1
    let new_percent = `
        <li style="display: flex;">
            <div contenteditable=true class="setting cashback" json-key="cashback.${id}.on" oninput="onChange(event)"></div>
            <div contenteditable=true class="setting percent" style="margin-left: 1rem;" json-key="cashback.${id}.percent" oninput="onChange(event)"></div>
        </li>`

    list_percents.innerHTML = list_percents.innerHTML + new_percent
}

function settingCashbackPercents(data) {
    for (const c of data['cashback']) {
        addPercents()
        let list_percents = document.querySelectorAll('#cashback-percent li')
        let empty_percent = list_percents[list_percents.length - 1]

        empty_percent.querySelector('.cashback').innerText = c['on']
        empty_percent.querySelector('.percent').innerText = c['percent']
    }
}


// Show the latest value's
async function setValues() {
    var data = await getJson()

    token.innerText = data["TOKEN"]
    uri.innerText = data["URI"]
    stop_bot.checked = data["TECHNICAL_STOP"]
    groupChatId.innerText = data["groupChatId"]
    cashback_friends.innerText = data["friend_money"]
    welcome_cashbask.innerText = data["welcome_cashback_sum"]
    limit_cashback.innerText = data["MAX_BALANCE"]

    setItems(data.items.balance);
    settingCashbackPercents(data)
}
setValues()

function nextSection(move) {
    let list_sections = document.querySelectorAll('.section')

    if (sectionId + move == list_sections.length || sectionId + move < 0) return;
    
    document.querySelectorAll(`.section.current .item`)[itemId].classList.remove("current")
    list_sections[sectionId].classList.remove("current")

    sectionId += move
    itemId = 0

    list_sections[sectionId].classList.add("current")
    document.querySelectorAll(`.section.current .item`)[itemId].classList.add("current")
}

const saveJson = function() {
    popup("Вы уверены что хотите <strong>сохранить</strong> изменение?", async () => {
        removePopup()
        let url = 'saveJSON'
        console.log(url)
        let request = await fetch(url, {
            method:'POST',
            headers:{
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(change)
        })
        if (request.ok) {
            alert("Saved!");
        }        
    })
}

async function getJson() {
    let request = await fetch('getJSON')
    let data;
    if (request.ok) {
        data = JSON.parse(await request.text())
    } else {
        alert("Couldn't retrive JSON, setting default values")
        data = {
            "TOKEN": "1861177956:AAGfxYGzvOlw4Fxwi4S6P_GOns-R_YwUFvA",
            "URI": "mongodb+srv://H_reugo:Nurmukhambetov@cluster0.vq2an.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
            "TECHNICAL_STOP": false,
            "groupChatId": 1654644284,
    
            "friend_money": 20,
            "welcome_cashback_sum": 200,
            "MAX_BALANCE": 20000,
        }
    }
    return data
}

function removePopup() {
    document.querySelector('#popup-container').style.visibility = 'hidden'
}
function popup(message, ok) {
    let container = document.querySelector('#popup-container')
    container.style.visibility = 'visible'

    container.querySelector('.message').innerHTML = message

    container.querySelector('button.ok').addEventListener('click', ok)
}

const cancelJson = function() {
    popup("Вы уверены что хотите <strong>отменить</strong> изменение?", async () => {
        await setValues()
        removePopup()
    })
}
