let stop_bot = document.querySelector('#stop_bot')

let groupChatId = document.querySelector('#groupChatId')
let token = document.querySelector('#bot-token')
let uri = document.querySelector('#mongo-uri')

let cashback_friends = document.querySelector('#cashback-friends')
let welcome_cashbask = document.querySelector('#welcome-cashback')
let limit_cashback = document.querySelector('#max-limit-cashback')

let change = {}
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
    change[key] = value
}

function buttonItem(itemId, last) {
    if (itemId == 0)
        return [`<button class="button-item left" onclick="addItem(-1);">
                    <img src="https://img.icons8.com/fluency-systems-regular/14/000000/plus-math.png"/>
                </button>`,
                `<button class="button-item right" onclick="nextItem(+1);">
                    <img src="https://img.icons8.com/fluency-systems-regular/14/000000/forward--v1.png"/>
                </button>`]
    else if (itemId == last - 1)
        return [`<button class="button-item left" onclick="nextItem(-1);">
                    <img src="https://img.icons8.com/fluency-systems-regular/14/000000/back.png"/>
                </button>`,
                `<button class="button-item right" onclick="addItem(+1);">
                    <img src="https://img.icons8.com/fluency-systems-regular/14/000000/plus-math.png"/>
                </button>`]
    else 
        return [`<button class="button-item left" onclick="nextItem(-1);">
                    <img src="https://img.icons8.com/fluency-systems-regular/14/000000/back.png"/>
                </button>`,
                `<button class="button-item right" onclick="nextItem(+1);">
                    <img src="https://img.icons8.com/fluency-systems-regular/14/000000/forward--v1.png"/>
                </button>`]
}

function addItem(move) {
    let list_items = document.querySelector(`.section.current .items`)

    new_item = `
    <li class="item current">
        <img class="item-img" src=""/>
        <h3>Имя</h3>
        <div contenteditable=true class="setting item-name" json-key="items.${sectionId}.${itemId+move}.name" oninput="onChange(event)"></div>
        <h3>Цена</h3> 
        <div contenteditable=true class="setting cashback item-price" json-key="items.${sectionId}.${itemId+move}.price" oninput="onChange(event)"></div>
        <h3>Лимит</h3>
        <div contenteditable=true class="setting item-limit" json-key="items.${sectionId}.${itemId+move}.limit" oninput="onChange(event)"></div>
        <h3>Изображения</h3>
    </li>
    `
    list_items.innerHTML = list_items.innerHTML + new_item
    nextItem(move)
}

function nextItem(move) {
    let list_items = document.querySelectorAll(`.section.current .item`)
    if (itemId + move == list_items.length || itemId + move < 0) return;

    list_items[itemId].classList.remove("current")
    itemId += move
    list_items[itemId].classList.add("current")

    let buttons = buttonItem(itemId, list_items.length)
    document.querySelector(`.section.current .button-item.left`).outerHTML = buttons[0]
    document.querySelector(`.section.current .button-item.right`).outerHTML = buttons[1]
}

function settingItems(data) {
    var list = document.querySelector('.sections')
    list.innerHTML = '';
    data['items'].forEach((section, i) => {
        var imagesHTML = ''
        section.forEach((item, j) => {
            let imageHTML = `
            <li class="item ${(i == 0 && j == 0)?"current":""}">
                <img class="item-img" src="${'image/' + item['image']}" alt="${item['name']}"/>
                <h3>Имя</h3>
                <div contenteditable=true class="setting item-name" json-key="items.${i}.${j}.name" oninput="onChange(event)">${item['name']}</div>
                <h3>Цена</h3> 
                <div contenteditable=true class="setting cashback item-price" json-key="items.${i}.${j}.price" oninput="onChange(event)">${item['price']}</div>
                <h3>Лимит</h3>
                <div contenteditable=true class="setting item-limit" json-key="items.${i}.${j}.limit" oninput="onChange(event)">${item['limit']}</div>
                <h3>Изображения</h3>
            </li>`
            imagesHTML = imagesHTML + imageHTML
        })

        let sectionHTML = 
        `<li class="section ${(i == 0)?"current":""}">
        <button class="button-section left" onclick="nextSection(-1);">
            <img src="https://img.icons8.com/fluency-systems-regular/14/000000/back.png"/>
        </button>
        <div class="section-name">${sectionName[i]}</div>
        <button class="button-section right" onclick="nextSection(+1);">
        <img src="https://img.icons8.com/fluency-systems-regular/14/000000/forward--v1.png"/>
        </button>
        
        <button class="button-item left" onclick="nextItem(-1);">
            <img src="https://img.icons8.com/fluency-systems-regular/14/000000/back.png"/>
        </button>
        <ul class="items">
            ${imagesHTML}
        </ul>
        <button class="button-item right" onclick="nextItem(+1);">
            <img src="https://img.icons8.com/fluency-systems-regular/14/000000/forward--v1.png"/>
        </button>
        </li>`

        list.innerHTML = list.innerHTML + sectionHTML
    })

    nextItem(0)
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

    settingItems(data);
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
        let url = 'saveJSON?data=' + encodeURIComponent(JSON.stringify(change))
        console.log(url)
        let request = await fetch(url)
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
