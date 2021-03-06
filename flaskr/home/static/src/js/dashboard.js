// Remove Alert on Close

const alertButton = document.querySelector('.alert button');

if (alertButton){
  alertButton.addEventListener('click', function (event) {
  	event.preventDefault();
    alertButton.parentNode.style.display = 'none';
  }, false);
}

const myDict = {
    1: "Close",
    2: "Open",
    3: "High",
    4: "Low",
    5: "Volume"
};

function getSumms(json){
        emptySumms();
        let obj = JSON.stringify(json);
        console.log(obj);
        let arr = JSON.parse(obj);
        console.log(arr);
        let var1Name = myDict[arr[0]];
        console.log("arr[0] ="+arr[0]);
        console.log("myDict[1]="+myDict[1]);
        let var2Name = myDict[arr[4]];
        for(let i=1;i<arr.length;i++){
            let elem;
            switch(i){
                case 1:
                    elem = document.getElementById("var1-mode");
                    elem.innerText = var1Name +" mode = " + arr[i];
                    break;
                case 2:
                    elem = document.getElementById("var1-median");
                    elem.innerText = var1Name +" median = " + arr[i];
                    break;
                case 3:
                    elem = document.getElementById("var1-mean");
                    elem.innerText = var1Name + " mean = " + arr[i];
                    break;
                case 5:
                    elem = document.getElementById("var2-mode");
                    elem.innerText = var2Name + " mode = " + arr[i];
                    break;
                case 6:
                    elem = document.getElementById("var2-median");
                    elem.innerText = var2Name +" median = " + arr[i];
                    break;
                case 7:
                    elem = document.getElementById("var2-mean");
                    elem.innerText = var2Name + " mean = " + arr[i];
                    break;
            }
        }
}

function emptySumms(){
    let elem = document.getElementById("var1-mode");
    elem.innerText = "";
    elem = document.getElementById("var1-median");
    elem.innerText ="";
    elem = document.getElementById("var1-mean");
    elem.innerText = "";
    elem = document.getElementById("var2-mode");
    elem.innerText = "";
    elem = document.getElementById("var2-median");
    elem.innerText = "";
    elem = document.getElementById("var2-mean");
    elem.innerText = "";
}

function show(name){
    document.getElementById(name).classList.toggle("show");
}

function addTicker(){
    let elem = document.getElementById("stock-list");
    let input = document.getElementById("search-bar").value;
    let favSize = elem.childElementCount;
    if (favSize >= 5){
        return alert('You must remove a stock from the list before you can add another. The max is five.')
    }
    //send data to python for model build
    let modelInfo = {
        "stockName" : input,
        "favSize" : favSize
    };
    let modelJson = JSON.stringify(modelInfo);

    fetch('/addTicker', {
        headers: {
            'Content-Type': 'application/json'
        },

        method: 'POST',

        body: modelJson

    }).then(function (response){
        return response.text();
    }).then(function (text){

        if (text === 'OK') {
            elem.innerHTML += '</li><a href="#" id="'+input+'" class="ticker"' +
                ' onclick="sendPlotJson(this.id,false);return false;">'+input+'</a></li>';
        }
        console.log('ajax res:');
        console.log(text);
        window.location.reload();
    });
}

function sendPlotJson(data, isFav=false){
    let val;
    let vars = [];
    let ticker;


    if(isFav) {
        try {
            val = 'Tick';
            ticker = data.toString();
            let plotObj = {
                "plotType": val,
                "variables": vars,
                "ticker": ticker
            };
            let json = JSON.stringify(plotObj);
            fetch('/graph.png', {

                headers: {
                    'Content-Type': 'application/json'
                },

                method: 'POST',

                body: json

            }).then(function (response) {
                return response.json();
            }).then(function (json) {
                let img = document.getElementById("data-visual");
                img.src = '/graph.png';
                let dataTitle = document.getElementById("data-title");
                dataTitle.innerHTML = ticker.toUpperCase() + " Data Visualizer";
                getSumms(json);
                let scoreElem = document.getElementsByClassName("model-score")[0];
                scoreElem.innerText = "";
                let predictElem = document.getElementsByClassName("predicted-price")[0];
                predictElem.innerText = "";
            });
        }catch (e) {
            alert("there was an error= "+e);
        }
    } else {

        let vals = document.getElementsByClassName("graph-types");
        let variables = document.getElementsByClassName("variables");
        ticker = document.getElementById("data-title").innerText.split(" ")[0];

        for(let i=0;i<vals.length;i++){
            if(vals[i].checked){
                val=vals[i].id;
                console.log(val)
                break;
            }
        }
        for(let i=0;i<variables.length;i++){
            if(variables[i].checked){
                vars.push(variables[i].id)
            }
        }

        if(val === undefined || vars.length === 0){
            alert("Please make sure you have selected both a variable and a " +
                "graph type");
            return;
        }

        console.log("plotType is equal to = "+ val);

        let plotObj = {
            "plotType" : val,
            "variables" : vars,
            "ticker" : ticker
        };
        let json = JSON.stringify(plotObj);
        try {
            fetch('/graph.png', {

                headers: {
                    'Content-Type': 'application/json'
                },

                method: 'POST',

                body: json

            }).then(function (response) {
                return response.json();
            }).then(function (json) {
                let img = document.getElementById("data-visual");
                img.src = '/graph.png';
                getSumms(json);
                let dataTitle = document.getElementById("data-title");
                dataTitle.innerHTML = ticker.toUpperCase() + " Data Visualizer";
                let scoreElem = document.getElementsByClassName("model-score")[0];
                scoreElem.innerText = "";
                let predictElem = document.getElementsByClassName("predicted-price")[0];
                predictElem.innerText = "";
            });
        }catch (e) {
            alert("there was an error = "+e);
        }
    }

}

function getGraph(){
    let splitString = document.getElementById("data-title");
    let name = document.getElementsByClassName("ticker")[0].id;
    if (name === undefined)return;

    splitString.innerText = name.toUpperCase() + " Data Visualizer";
    let vars = [];
    vars.push('Close');
    let obj = {
        "ticker": name,
        "plotType": 'Tick',
        "variables": vars,
    };
    let json = JSON.stringify(obj);
    fetch('/graph.png', {
        headers: {
            'Content-Type': 'application/json'
        },

        method: 'POST',

        body: json
    }).then(function (response){
        return response.json();
    }).then(function (json){
        console.log(json);
        //identifies are stored at 0 for var1 and 4 for var2
        getSumms(json);
        let img = document.getElementById("data-visual");
        img.src ="/graph.png";
    });

}

function createModel(){
    try {
        let stockName = document.getElementById("data-title").innerText.split(" ")[0];

        let jsonObj = {
            "stockName": stockName
        }
        let json = JSON.stringify(jsonObj);

        fetch('/createModel', {
            headers: {
                'Content-Type': 'application/json'
            },

            method: 'POST',

            body: json
        }).then(function (response) {
            return response.text();
        }).then(function (text) {
            console.log("ajax response: " + text);
            if (text === 'OK') {
                alert('Model Successfully Created.');
            }
        });
    }catch (e){
        alert("there was an error = "+e);
    }
}

function graphModel() {
    let stockName = document.getElementById("data-title").innerText.split(" ")[0];
    try {
        let jsonObj = {
            "stockName": stockName
        };
        let json = JSON.stringify(jsonObj);

        fetch('/graphModel.png', {

            headers: {
                'Content-Type': 'application/json'
            },

            method: 'POST',

            body: json
        }).then(function (response) {
            return response.json();
        }).then(function (json) {
            let score = json.score;
            console.log(score);
            emptySumms();
            let scoreElem = document.getElementsByClassName("model-score")[0];
            scoreElem.innerText = "The model score is: " + score;
            let predictElem = document.getElementsByClassName("predicted-price")[0];
            predictElem.innerText = "";
            fetch('/graphModel.png', {}).then(function (response) {
                return response.text();
            }).then(function (text) {
                let name = document.getElementById("data-title").innerText.split(" ")[0];
                let img = document.getElementById("data-visual");
                img.src = "/graphModel.png";
                let splitString = document.getElementById("data-title");
                splitString.innerText = name.toUpperCase() + " Data Visualizer";
            });
        });
    } catch (e) {
        alert("there was an error = " + e);
    }

}

function restrict(id){
    let graphs = document.getElementsByClassName("graph-types");
    let active = document.getElementById(id);
    if(active.checked){
        for(let i=0;i<graphs.length;i++){
            if(graphs[i].id !== id){
                graphs[i].disabled = true;
            }
        }
    }
    else {
        for(let i=0;i<graphs.length;i++){
            if(graphs[i].id !== id){
                graphs[i].disabled = false;
            }
        }
    }
}

function restrictVars(id){
    let variables = document.getElementsByClassName("variables");
    let idItem = document.getElementById(id);
    let id2 = undefined;
    if (idItem.checked) {
        for (let i = 0; i < variables.length; i++) {
            if (variables[i].checked && variables[i].id !== id) {
                id2 = variables[i].id;
            }
        }
        if (id2 !== undefined) {
            for (let i = 0; i < variables.length; i++) {
                if (!variables[i].checked) {
                    variables[i].disabled = true;
                }
            }
        }
    }
    else {
        for (let i = 0; i < variables.length; i++) {
            if (!variables[i].checked) {
                variables[i].disabled = false;
            }
        }
    }
}

function predictPrice(){
    let stockName = document.getElementById("data-title").innerText.split(" ")[0];
    try {
        let Obj = {
            "stockName": stockName
        };

        let json = JSON.stringify(Obj);

        fetch('/getPrediction', {
            headers: {
                'Content-Type': 'application/json'
            },

            method: 'POST',

            body: json
        }).then(function (response){
            return response.text();
        }).then(function (text){
            console.log(text);
            try{
                fetch('/getPrediction',{

                }).then(function (response){
                    return response.json();
                }).then(function (json){
                    let price = json.prediction;
                    let predictElem = document.getElementsByClassName("predicted-price")[0];
                    predictElem.innerText = "The closing price predicted for tomorrow is: " + price;
                });
            }catch(e){
                alert("there was an error retrieving the prediction. e=" +e);
            }
        })
    }catch(e){
        alert("there was an error posting stock name. e="+e);
    }
}

function deleteTicker(){
    let input = document.getElementById("search-bar").value;

    let info = {
        "stockName" : input
    };
    let json = JSON.stringify(info);
    try {
        fetch('/deleteTicker', {
            headers: {
                'Content-Type': 'application/json'
            },

            method: 'POST',

            body: json
        }).then(function (response) {
            return response.text();
        }).then(function (text) {
            console.log(text);
            let temp = "";
            if(text !== 'OK'){
                temp = text;
            }
            try {
                fetch('/deleteTicker', {}).then(function (response) {

                }).then(function (text) {
                    window.location.reload();
                });
            }catch (e) {
                alert("there was an issue deleting the ticker. e="+e);
            }
        });
    }catch (e){
        alert("there was an error deleting the ticker. e ="+e);
    }
}

function search() {
    let elem = document.getElementById('search-bar').value;

    let obj =  {
        "stockName": elem
    };
    let json = JSON.stringify(obj);
    fetch('/search.png', {
        headers: {
                'Content-Type': 'application/json'
            },

        method: 'POST',

        body: json
    }).then(function (response){
        return response.text();
    }).then(function (text){
        console.log(text);
        fetch('search.png', {

        }).then(function (response){
            return response.text();
        }).then(function (text){
            let img = document.getElementById("data-visual");
            img.src = '/search.png';
            let dataTitle = document.getElementById("data-title");
            dataTitle.innerHTML = elem.toUpperCase() + " Data Visualizer";
            let scoreElem = document.getElementsByClassName("model-score")[0];
            scoreElem.innerText = "";
            let predictElem = document.getElementsByClassName("predicted-price")[0];
            predictElem.innerText = "";
        });
    });
}