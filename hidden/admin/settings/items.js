var numberOfItems;

const setItems = (items) => {
    console.log(items)
    items = Object.values(items)

    numberOfItems = items.length
    placeItemsInCarousel(items)
}

const itemTemplate = (item) => {

    if(!(item.image.indexOf("blob") + 1) && !(item.image.indexOf("data:image/") + 1)){ 
        // if not a blob or a data:image/ 
        item.image = "image/" + item.image
    }

    return `
<div  class="item" id="tag_${item.tag}">
    <button onclick="openEditMenu('${item.tag}')">🖊️</button>
    <button onclick="deleteItem('${item.tag}')">🗑️</button>
    <table>
        <tr class="image">
            <td colspan="2">
                <img src="${item.image}" alt="картинка ${item.name}">
            </td>
        </tr>
        <tr class="name">
            <td class="rowName">Название:</td>
            <td>${item.name}</td>
        </tr>
        <tr class="price">
            <td class="rowName">Цена:</td>
            <td>${item.price} ₸</td>
        </tr>
        <tr class="limit">
            <td class="rowName">Лимит Покупок:</td>
            <td>${item.limit}</td>
        </tr>
        <tr class="tag">
            <td class="rowName">Тег в Базе:</td>
            <td>${item.tag}</td>
        </tr>
    </table>
</div>    
`
} 

const placeItemsInCarousel = (items) => {
    console.log(items)

    items.forEach((item, i) => {
        document.querySelector("#items").innerHTML += itemTemplate(item)
        
        if(i == 0){
            document.querySelectorAll(".item")[i].classList.add("current")
        }
    })
}

const getCurrentAndNeighbors = () => {
    listOfItems = [...document.querySelectorAll(".item")]
    curr = document.querySelector(".current")
    currNum = listOfItems.indexOf(curr)

    rightId = (currNum + 1 + listOfItems.length) % listOfItems.length
    leftId = (currNum - 1 + listOfItems.length) % listOfItems.length


    return {
        right: listOfItems[rightId],
        left: listOfItems[leftId],
        current: curr,
        // rightId: rightId,
        // leftId: leftId
    }
}

const setCurr = (nextCurr) => {
    curr = document.querySelector(".current")
    
    if(curr)
    curr.classList.remove("current")
    
    nextCurr.classList.add("current")
}

const scrollMove = (side) => {
    setCurr(getCurrentAndNeighbors()[side])
}

const deleteItem = (itemTag, conf) => {
    conf = conf || confirm("Вы уверены, что хотите удалить?");
    if(conf){
        if(document.querySelectorAll(".item").length > 1)
            scrollMove("left")
        else
            openAddMenu()

        document.querySelector("#items")
        .removeChild(document.querySelector(`#tag_${itemTag}`))

        path = `items.balance.${itemTag}`
        change["$delete"][path] = 0    
    }
}

const addNewItem = (data) => {
    Object.entries(data).forEach(entery => {
        path = `items.balance.${data["tag"]}.${entery[0]}`
        
        if(entery[0] != "image")
            change["$set"][path] = entery[1]
        else
            change["$set"][path] = entery[1].split(",")[1]
    })
    
    document.querySelector("#items").innerHTML += itemTemplate(data)
    setCurr(document.querySelector(`#tag_${data.tag}`))
}

// MENU

const openAddMenu = () => {
    document.querySelector("#addMenu").style.display = "block";
}
const closeAddMenu = () => {
    document.querySelector("#addMenu").style.display = "none";
}
const clearAddMenu = () => {
    document.querySelector("#addMenu")
    .querySelectorAll("input")
    .forEach(input => {
        input.value = ""
    })
    document.querySelector("#inputAddImage").src = ""
}

function getBase64Image(img) {
    var canvas = document.createElement("canvas");
    canvas.width = img.naturalWidth;
    canvas.height = img.naturalHeight;
    var ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0);
    var dataURL = canvas.toDataURL("image/png");

    return "data:image/png;base64," + dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
}

const getAddMenuData = () => {
    let data = {}

    document.querySelector("#addMenu")
    .querySelectorAll("input")
    .forEach(input => {
        if(input.type == 'number')
            data[input.name] = Number(input.value)
        else if(input.type == 'text')
            data[input.name] = input.value
        else if(input.type == 'file')
            data[input.name] = getBase64Image(document.querySelector("#inputAddImage"))
    })

    return data
}

const addMenuButton = () => {
    let addMenuFilled = true;

    document.querySelector("#addMenu")
    .querySelectorAll("input")
    .forEach(input => {
        addMenuFilled = addMenuFilled && input.value;
    })

    if(addMenuFilled){
        addNewItem(getAddMenuData())
        closeAddMenu()
        clearAddMenu()
    }
    else{
        alert("Заполните меню полностью!")
    }
}

// display loaded image

var loadAddFile = function(event) {
	var image = document.getElementById('inputAddImage');
	image.src = URL.createObjectURL(event.target.files[0]);
};

document.querySelector("#addMenu")
.querySelector("input[type='file']")
.addEventListener("change", (e) => {
    loadAddFile(e)
})

// edit menu
const editingItem = {}


const openEditMenu = (tag) => {
    editMenu = document.querySelector("#editMenu")
    tag = document.querySelector(`#tag_${tag}`)
    
    editMenu.querySelectorAll("input").forEach(input => {
        cl = input.name
        
        if(input.type != "file"){
            if(cl != "price"){
                v = tag.querySelector(`.${cl} > td:nth-child(2)`).innerText
            }else{
                v = tag.querySelector(`.${cl} > td:nth-child(2)`).innerText.split(" ")[0]
            }
            
            input.value = v
            editingItem[cl] = v
        }else{
            editingItem[cl] = tag
            .querySelector("img").src
            .split(window.location.href.split("settings")[0])[1]
            .split("image")[1]
        }
    })

    
    editMenu.style.display = "block";
}
const closeEditMenu = () => {
    document.querySelector("#editMenu").style.display = "none";
}
const clearEditMenu = () => {
    document.querySelector("#editMenu")
    .querySelectorAll("input")
    .forEach(input => {
        input.value = ""
    })
    document.querySelector("#inputEditImage").src = ""
}

const getEditMenuData = () => {
    let data = {}

    document.querySelector("#editMenu")
    .querySelectorAll("input")
    .forEach(input => {
        if(input.type == 'number')
            data[input.name] = Number(input.value)
        else if(input.type == 'text')
            data[input.name] = input.value
        else if(input.type == 'file')
                if(document.querySelector("#inputEditImage").src != "")
                    data[input.name] = getBase64Image(document.querySelector("#inputEditImage"))
    })

    return data
}

const updateItem = (oldData, newData) => {
    currImgURL = document.querySelector(".current")
                .querySelector("img").src
                .split(window.location.href.split("settings")[0])[1]
                .split("image")[1]
    newData.image = (newData.image)?newData.image.split(",")[1]:"" || currImgURL

    console.log(newData, oldData)

    Object.entries(newData).forEach(entery => {
        if(newData[entery[0]] != oldData[entery[0]]){

            path = `items.balance.${oldData["tag"]}.${entery[0]}`
            change["$set"][path] = entery[1]

            if(entery[0] != "image")
                document.querySelector(`#tag_${oldData.tag}`)
                .querySelector(`.${entery[0]} > td:nth-child(2)`).innerHTML = entery[1]
            else
                document.querySelector(`#tag_${oldData.tag}`)
                .querySelector('img').src = "data:image/png;base64," + entery[1]

            if(entery[0] == "tag")
                document.querySelector(`#tag_${oldData.tag}`).id = `#tag_${entery[1]}`
        }
    })
} 

var loadEditFile = function(event) {
	var image = document.getElementById('inputEditImage');
	image.src = URL.createObjectURL(event.target.files[0]);
};

document.querySelector("#editMenu")
.querySelector("input[type='file']")
.addEventListener("change", (e) => {
    loadEditFile(e)
})

const editMenuButton = () => {
    let editMenuFilled = true;

    document.querySelector("#editMenu")
    .querySelectorAll("input")
    .forEach(input => {
        if(input.type != 'file')
        editMenuFilled = editMenuFilled && input.value;
    })

    if(editMenuFilled){
        updateItem(editingItem, getEditMenuData())
        closeEditMenu()
        clearEditMenu()
    }
    else{
        alert("Заполните меню полностью!")
    }
    console.log("save changes")
}