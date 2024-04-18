
function translate(id){
    document.getElementById('overlay').style.display = 'flex';
    console.log(id)
    var book_name = id.split("_") 
    var language = book_name.pop()
    var name=book_name.join("_")
    var username = document.getElementById("user_id").textContent
    console.log(name,"====>",language) 
    fetch(`translate/${username}/${name}/${language}`)
    .then(response => response.json())
    .then(data => {
        console.log(data['status'])
        document.getElementById('overlay').style.display = 'none';

        var ul = document.getElementById(name+"_ul")
        var li = document.createElement('li')
        li.setAttribute('data-hidden-value', data['status'])
        li.id = name+"_"+language+"_list"
        li.innerHTML = `${name}_${language} - <a href="download/B:%5CREST_API_env%5Cbtech_project%5Cmedia%5Cpdf%5C${username}%5C${name}/${name}/${language}/">⇩</a>&nbsp&nbsp&nbsp<button onclick="delete_by_id('${name}','${language}')">❌</button>`
        ul.appendChild(li)

        var ul2 = document.getElementById(`${name}_name_list`)
        var li2 = document.getElementById(`${name}_${language}_to_translate`)
        ul2.removeChild(li2) 

    })
    .catch(error => {
        console.log('error while translation...!')
        document.getElementById('overlay').style.display = 'none';
    })                              
}
window.translate = translate

const form = document.getElementById('form');
                form.addEventListener('submit', function(e) {
                    document.getElementById('overlay').style.display = 'flex';
                    e.preventDefault()
                    var form_data = new FormData(form)
                    
                    fetch('insert_data/', {
                        method: 'POST',
                        body: form_data,
                    })
                    .then(response => response.json())
                    .then(data => {
                        if( data[0] == 1){
                            console.log(data)
                            var file_rec = data[0]['status']
                            console.log("Submitted successfully");   
                            document.getElementById('overlay').style.display = 'none';  
                            document.querySelector(".check").style.display = "inline-block";
                            window.location.reload(true);
                            
                        }
                        else if(data[0] == 0 ){
                            document.getElementById('overlay').style.display = 'none';
                            alert("Already exists...!")
                        }
                        else{
                            document.getElementById('overlay').style.display = 'none';
                            alert("Error while translation........!")
                        }
                            
                    })
                    .catch(error => {
                        console.log('error while translation...!')
                        document.getElementById('overlay').style.display = 'none';
                    })       
                    
                })

function sidelist_display(id){
    var p = document.getElementById(id)
    p.style.color='grey'
    var list = document.getElementById(id+"_list")
    list.style.display = 'block'
    console.log(1)
}

function sidelist_undisplay(id){
    var p = document.getElementById(id)
    p.style.color='black'
    var list = document.getElementById(id+"_list")
    list.style.display = 'block'
    console.log(2)
}

function sidelist_exit(id){
    var l = document.getElementById(id)
    l.style.display = 'none'
    console.log(3)

}


window.sidelist_display = sidelist_display
window.sidelist_undisplay = sidelist_undisplay
window.sidelist_exit = sidelist_exit


var buttons = document.querySelectorAll('.translate_buttons');

// Add click event listener to each button
buttons.forEach(function(button) {
    button.addEventListener('click', function() {
        // Get the ID of the clicked button
        var buttonId = this.id;

        // Call a function or perform actions based on the button ID
        translate(buttonId);
    });
});


// function simulateLoading() {
//     // Show the overlay
//     document.getElementById('overlay').style.display = 'flex';

//     // Simulate an asynchronous operation (e.g., AJAX request)
//     setTimeout(function() {
//         // Hide the overlay after the operation is complete
//         document.getElementById('overlay').style.display = 'none';
//     }, 3000); // Simulated delay of 3 seconds
// } 

function delete_by_id(name,lang){
    document.getElementById('overlay').style.display = 'flex';
    if(lang != 'original'){
            fetch(`delete/${name}/${lang}`)
            .then(response => response.json())
            .then(data => {
                console.log(data)
                document.getElementById('overlay').style.display = 'none';
                var elementToRemove = document.getElementById(name+"_"+lang+"_list");
                var parentElement = elementToRemove.parentNode;
                parentElement.removeChild(elementToRemove);

                //add to do translation list
                var liElement = document.createElement('li');
                liElement.className = 'list';
                liElement.textContent = `${name}_${lang} `;

                var buttonElement = document.createElement('button');
                buttonElement.id = `${name}_${lang}`; // Set the dynamic ID for the button
                buttonElement.className = 'translate_buttons';
                buttonElement.textContent = '↺';

                liElement.appendChild(buttonElement);

                var ulElement = document.getElementById(name + '_name_list');
                if (ulElement) {
                    ulElement.appendChild(liElement);
                } else {
                    console.log("error")
                }
            })
            .catch(error => {
                console.log(error)
                alert("error while deletion...!")
                document.getElementById('overlay').style.display = 'none';
            }) 
    }
    else{

        fetch(`delete_original/${name}`)
        .then(response => response.json())
        .then(data =>{
            console.log(data)
            var ele = document.getElementById(name)
            if (ele) {
                ele.parentNode.removeChild(ele);
                
                document.getElementById('overlay').style.display = 'none';
            } else {
                
                document.getElementById('overlay').style.display = 'none';
            }
        }).catch(error => {
            alert('error while deletion...!')
            document.getElementById('overlay').style.display = 'none';
        })
    }       
}

window.delete_by_id = delete_by_id

var search = document.getElementById('search')
search.addEventListener("keyup",function(event){
    filterListItems(event.target.value)
    console.log(event.target.value)
})

function filterListItems(searchString) {
    
    var listItems = document.querySelectorAll('.download_list');
    console.log(listItems)
    listItems.forEach(item => {
      const hiddenValue = item.getAttribute('data-hidden-value').toLowerCase();
      const itemId = item.id.toLowerCase();
      const isVisible = hiddenValue.includes(searchString.toLowerCase()) || itemId.includes(searchString.toLowerCase());

      // Toggle visibility based on the search string
      item.style.display = isVisible ? 'list-item' : 'none';
      console.log(item )
    });
}















