let stop = document.querySelector('#stop')

let groupChatId = document.querySelector('#groupChatId')
let token = document.querySelector('#bot-token')
let uri = document.querySelector('#mongo-uri')

let cashback_friends = document.querySelector('#cashback-friends')
let welcome_cashbask = document.querySelector('#welcome-cashback')
let limit_cashback = document.querySelector('#max-limit-cashback')

let save = document.querySelector('#submit')

const saveJson = async function() {
    let data = create_json();
    let url = 'saveJSON?data=' + encodeURIComponent(JSON.stringify(data))
    console.log(url)
    let request = await fetch(url)
    console.log(request)
}

function create_json() {
    return {
        "TOKEN": token.innerText,
        "URI": uri.innerText,
        "TECHNICAL_STOP": stop.checked,
        "groupChatId": groupChatId.innerText,

        "friend_money": cashback_friends.innerText,
        "welcome_cashback_sum": welcome_cashbask.innerText,
        "MAX_BALANCE": limit_cashback.innerText,
    }
}
