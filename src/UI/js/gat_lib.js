window.gat = {};

window.gat.uploadAPIandQuestion = function (apiUrl, question) {

    let fd = new FormData();
    fd.append('apiUrl', apiUrl);
    fd.append('question', question);

    console.log('API URL:   ', apiUrl)
    console.log('Question:  ', question)

    $.ajax({
        url: "http://localhost:3000/loader/APIandQuestion",
        method: 'post',
        data: fd,
        processData: false,
        contentType: false,

        success: function(data){
            console.log("Uploaded API URL and question...");
            window.gat.callNLPmodule();
        },
        error: function(e) {
           console.log("ERROR: ", e)
        },
    });
};

window.gat.callNLPmodule = function () {

    $.ajax({
        url: "http://localhost:3000/predictor/query",
        method: 'get',
        data: {},

        success: function(data){
            console.log("Calling the NLP module...");
        },
        error: function(e) {
           console.log("ERROR: ", e)
        },
    });
};

window.gat.getPredictedQuery = function () {

    $.ajax({
        url: "http://localhost:3000/loader/prediction",
        method: 'get',
        data: {},

        success: function(data){
            console.log("Writing prediction...", data);
            $("#predicted-query").text(data);
        },
        error: function(e) {
           console.log("ERROR: ", e)
        },
    });
};

window.gat.uploadResponse = function (predictedQuery) {

    let fd = new FormData();
    fd.append('predictedQuery', predictedQuery);

    console.log('Predicted query: ', predictedQuery)

    $.ajax({
        url: "http://localhost:3000/loader/predictedQuery",
        method: 'post',
        data: fd,
        processData: false,
        contentType: false,

        success: function(data){
            console.log("Uploaded predicted query...");
            window.gat.callExplorerModule();
        },
        error: function(e) {
           console.log("ERROR: ", e)
        },
    });
};

window.gat.callExplorerModule = function () {

    $.ajax({
        url: "http://localhost:3000/predictor/response",
        method: 'get',
        data: {},

        success: function(data){
            console.log("Calling the Explorer module...");
        },
        error: function(e) {
           console.log("ERROR: ", e)
        },
    });
};

window.gat.getResponse = function () {

    $.ajax({
        url: "http://localhost:3000/loader/response",
        method: 'get',
        data: {},

        success: function(data){
            console.log("Writing response...", data);
            $("#response-query").text(data);
        },
        error: function(e) {
           console.log("ERROR: ", e)
        },
    });
};