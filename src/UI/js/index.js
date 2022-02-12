$(document).ready(function() {
    $('#prepare-schema-btn').click(function() {
        let question = $('#question').val();
        let apiUrl = $('#api').val();

        if (!apiUrl) {
            $('#api-label').addClass('[Error...]');
        }
        if (!question) {
            $('#input-label').addClass('[Error...]');
        }

        $('#predicted-query').text('[Preparing...]');

        axios.post('http://localhost:5000/question', {
            question,
            graphql_api_url: apiUrl
        }).then(res => {
            console.log(res.data);
        }).catch(err => {
            console.log(err);
         });

        $('#predicted-query').text('[Prepared!]');
    });

    $('#get-query-btn').click(function() {
        $('#predicted-query').text('[Loading...]');

        axios.get('http://localhost:5000/prediction')
            .then(res => {
                console.log(res.data);
                $('#predicted-query').text(res.data);
            })
            .catch(err => {
                console.log(err);
                $('#predicted-query').text('[Error!]');
            });
    });

    $('#send-query-btn').click(function() {
        // $("#response-query").text('Marco!');

        let apiUrl = $('#api').val();
        let prediction = $('#predicted-query').text();

        if (!apiUrl) {
            $('#api-label').addClass('[Error...]');
        }
        if (!prediction || !prediction.includes('query')) {
            $('#response-query').text('[Error...]')
        }

        $('#response-query').text('[Sending...]');

        axios.post('http://localhost:5000/predictedQuery', {
            query: prediction,
            graphql_api_url: apiUrl
        }).then(res => {
            console.log(res.data);
        }).catch(err => {
            console.log(err);
        });

        $('#response-query').text('[Sent!]');
    });

    $('#get-response-btn').click(function() {
        $("#response-query").text('[Loading...]');

        axios.get('http://localhost:5000/response')
            .then(res => {
                console.log(res.data);
                $('#response-query').text(res.data);
            })
            .catch(err => {
                console.log(err);
                $('#response-query').text('[Error!]');
            });
    });
});