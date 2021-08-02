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
    }
}

const addNewItem = (data) => {
    Object.entries(data).forEach(entery => {
        path = `items.toys.${data["tag"]}.${entery[0]}`
        
        change[path] = entery[1]
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

var loadFile = function(event) {
	var image = document.getElementById('inputAddImage');
	image.src = URL.createObjectURL(event.target.files[0]);
};

document.querySelector("#addMenu")
.querySelector("input[type='file']")
.addEventListener("change", (e) => {
    loadFile(e)
})

// edit menu

const openEditMenu = (tag) => {
    editMenu = document.querySelector("#editMenu")
    tag = document.querySelector(`#tag_${tag}`)
    
    editMenu.querySelectorAll("input").forEach(input => {
        if(input.type != "file"){
            cl = input.name
            if(cl != "price"){
                input.value = tag.querySelector(`.${cl} > td:nth-child(2)`).innerText
            }else{
                input.value = tag.querySelector(`.${cl} > td:nth-child(2)`).innerText.split(" ")[0]
            }
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

const updateItem = (data) => {
    currImgURL = document.querySelector(".current")
                .querySelector("img").src
                .split(window.location.href.split("settings")[0])[1]
                .split("image")[1]
    data.image = data.image || currImgURL
    currTag = document.querySelector(".current").querySelector(".tag").querySelector("td:nth-child(2)").innerText

    deleteItem(currTag, true)
    addNewItem(data)
} 

const editMenuButton = () => {
    let editMenuFilled = true;

    document.querySelector("#editMenu")
    .querySelectorAll("input")
    .forEach(input => {
        if(input.type != 'file')
        editMenuFilled = editMenuFilled && input.value;
    })

    if(editMenuFilled){
        updateItem(getEditMenuData())
        closeEditMenu()
    }
    else{
        alert("Заполните меню полностью!")
    }
    console.log("save changes")
}