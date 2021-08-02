var numberOfItems;

const setItems = (items) => {
    numberOfItems = items.length
    placeItemsInCarousel(items)
}

const itemTemplate = (item, i) => {
    let i = i || null;
    if(i === null) console.error(`value for i not set`)

    if(!(item.image.indexOf("blob") + 1) && !(item.image.indexOf("data:image/") + 1)){ 
        // if not a blob or a data:image/ 
        item.image = "image/" + item.image
    }

    return `
<div  class="item" id="${item.tag}">
    <button>🖊️</button>
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

const deleteItem = (itemTag) => {
    if(confirm("Вы уверены, что хотите удалить?")){
        if(document.querySelectorAll(".item").length > 1)
            scrollMove("left")
        else
            openMenu()

        document.querySelector("#items")
        .removeChild(document.querySelector(`#${itemTag}`))
    }
}

const addNewItem = (data) => {
    Object.entries(data).forEach(entery => {
        path = "items.1." + entery[0]
        
        change[path] = entery[1]
    })
    
    document.querySelector("#items").innerHTML += itemTemplate(data)
    setCurr(document.querySelector(`#${data.tag}`))
}

// MENU

const openMenu = () => {
    document.querySelector("#menu").style.display = "block";
}
const closeMenu = () => {
    document.querySelector("#menu").style.display = "none";
}
const clearMenu = () => {
    document.querySelector("#menu")
    .querySelectorAll("input")
    .forEach(input => {
        input.value = ""
    })
    document.querySelector("#inputImage").src = ""
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

const getMenuData = () => {
    let data = {}

    document.querySelector("#menu")
    .querySelectorAll("input")
    .forEach(input => {
        if(input.type == 'number')
            data[input.name] = Number(input.value)
        else if(input.type == 'text')
            data[input.name] = input.value
        else if(input.type == 'file')
            data[input.name] = getBase64Image(document.querySelector("#inputImage"))
    })

    return data
}

const menuAddButton = () => {
    let menuFilled = true;

    document.querySelector("#menu")
    .querySelectorAll("input")
    .forEach(input => {
        menuFilled = menuFilled && input.value;
    })

    if(menuFilled){
        addNewItem(getMenuData())
        closeMenu()
        clearMenu()
    }
    else{
        alert("Заполните меню полностью!")
    }
}

// display loaded image

var loadFile = function(event) {
	var image = document.getElementById('inputImage');
	image.src = URL.createObjectURL(event.target.files[0]);
};

document.querySelector("#menu")
.querySelector("input[type='file']")
.addEventListener("change", (e) => {
    loadFile(e)
})