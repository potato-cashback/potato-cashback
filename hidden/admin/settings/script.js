let stop_bot = document.querySelector('#stop_bot')

let groupChatId = document.querySelector('#groupChatId')
let token = document.querySelector('#bot-token')
let uri = document.querySelector('#mongo-uri')

let cashback_friends = document.querySelector('#cashback-friends')
let welcome_cashbask = document.querySelector('#welcome-cashback')
let limit_cashback = document.querySelector('#max-limit-cashback')

const saveJson = async function() {
    let data = create_json();
    let url = 'saveJSON?data=' + encodeURIComponent(JSON.stringify(data))
    console.log(url)
    let request = await fetch(url)
    if (request.ok) {
        alert("Saved!");
    }
}

async function get_json() {
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

function create_json() {
    return {
        "TOKEN": token.innerText,
        "URI": uri.innerText,
        "TECHNICAL_STOP": stop_bot.checked,
        "groupChatId": parseInt(groupChatId.innerText),

        "friend_money": parseInt(cashback_friends.innerText),
        "welcome_cashback_sum": parseInt(welcome_cashbask.innerText),
        "MAX_BALANCE": parseInt(limit_cashback.innerText),
    }
}


// Show the latest value's
(async function() {
    var data = await get_json()

    token.innerText = data["TOKEN"]
    uri.innerText = data["URI"]
    stop_bot.checked = data["TECHNICAL_STOP"]
    groupChatId.innerText = data["groupChatId"]
    cashback_friends.innerText = data["friend_money"]
    welcome_cashbask.innerText = data["welcome_cashback_sum"]
    limit_cashback.innerText = data["MAX_BALANCE"]
})()