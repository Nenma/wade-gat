$(document).ready(function(){

    $("#generate-query-btn").click((e)=>{

        let apiUrl = $("#api").val();
        let question = $("#question").val();

        if (!apiUrl) {
            $("#api-label").addClass("ERROR...")
        }
        if (!question) {
            $("#input-label").addClass("ERROR...")
        }

        window.gat.uploadAPIandQuestion(apiUrl, question);
    });

    $("#get-query-btn").click((e)=>{

        window.gat.getPredictedQuery(); 
    });

    $("#send-query-btn").click((e)=>{

        let predictedQuery = $("#predicted-query").text();

        if (!predictedQuery) {
            $("#prediction-label").addClass("ERROR...")
        }

        window.gat.uploadResponse(predictedQuery);
    }); 

    $("#get-response-btn").click((e)=>{

        window.gat.getResponse(); 
    });

})