$(document).ready(function() {
    /**
     * General case: waiting to receive url and question,
     * so we disable the last 3 buttons to force the starting
     * order
     */
    $('#get-query-btn').attr('disabled', true);
    $('#get-query-btn').css('border-style', 'solid');
    $('#get-query-btn').css('border-color', 'gray');

    $('#send-query-btn').attr('disabled', true);
    $('#send-query-btn').css('border-style', 'solid');
    $('#send-query-btn').css('border-color', 'gray');

    $('#get-response-btn').attr('disabled', true);
    $('#get-response-btn').css('border-style', 'solid');
    $('#get-response-btn').css('border-color', 'gray');

    $('#prepare-schema-btn').click(function() {
        let question = $('#question').val();
        let apiUrl = $('#api').val();

        if (!apiUrl || !question) {
            $('#predicted-query').text('[Error: Missing API URL or question/query...]');
        } else {
            /**
             * If the "question" is in fact a graphql query, we
             * disable the first 2 buttons and enable the last 2,
             * it not, we proceed normally
             */
            if (question.includes('query')) {
                // Enable the third one
                $('#send-query-btn').attr('disabled', false);
                $('#send-query-btn').css('border-style', 'none');
            } else {
                // Enable the second button
                $('#get-query-btn').attr('disabled', false);
                $('#get-query-btn').css('border-style', 'none');

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
            }
            // In both cases, ww disable the first button after
            $('#prepare-schema-btn').attr('disabled', true);
            $('#prepare-schema-btn').css('border-style', 'solid');
            $('#prepare-schema-btn').css('border-color', 'gray');
        }
    });

    $('#get-query-btn').click(function() {
        $('#predicted-query').text('[Loading...]');

        // Disable this button
        $('#get-query-btn').attr('disabled', true);
        $('#get-query-btn').css('border-style', 'solid');
        $('#get-query-btn').css('border-color', 'gray');

        axios.get('http://localhost:5000/prediction')
            .then(res => {
                console.log(res.data);
                $('#predicted-query').text(res.data);

                // Enable the third button
                $('#send-query-btn').attr('disabled', false);
                $('#send-query-btn').css('border-style', 'none');
            })
            .catch(err => {
                console.log(err);
                $('#predicted-query').text('[Error!]');
            });
    });

    $('#send-query-btn').click(function() {
        let apiUrl = $('#api').val();
        let question = $('#question').val();
        let prediction = $('#predicted-query').text();

        if (!apiUrl || !question) {
            $('#response-query').text('[Error: Missing API URL or question/query...]');
        } else {
            /**
             * If this is a question, and not a query, we proceed normally,
             * if not we send the the query given instead of the prediction
             */
            $('#response-query').text('[Sending...]');
            if (!question.includes('query')) {        
                axios.post('http://localhost:5000/predictedQuery', {
                    query: prediction,
                    graphql_api_url: apiUrl
                }).then(res => {
                    console.log(res.data);
                }).catch(err => {
                    console.log(err);
                });
            } else {
                axios.post('http://localhost:5000/predictedQuery', {
                    query: question,
                    graphql_api_url: apiUrl
                }).then(res => {
                    console.log(res.data);
                }).catch(err => {
                    console.log(err);
                });
            }
    
            $('#response-query').text('[Sent!]');
    
            // Disable this button and enable the last one
            $('#send-query-btn').attr('disabled', true);
            $('#send-query-btn').css('border-style', 'solid');
            $('#send-query-btn').css('border-color', 'gray');
    
            $('#get-response-btn').attr('disabled', false);
            $('#get-response-btn').css('border-style', 'none');
        }
    });

    $('#get-response-btn').click(function() {
        $("#response-query").text('[Loading...]');

        axios.get('http://localhost:5000/response')
            .then(res => {
                console.log(res.data);
                $('#response-query').text(JSON.stringify(res.data));
            })
            .catch(err => {
                console.log(err);
                $('#response-query').text('[Error!]');
            });

        /**
         * After pressing the last button, reset to original setup,
         * so disable this button and enable the first one again
         */
         $('#get-response-btn').attr('disabled', true);
         $('#get-response-btn').css('border-style', 'solid');
         $('#get-response-btn').css('border-color', 'gray');
 
         $('#prepare-schema-btn').attr('disabled', false);
         $('#prepare-schema-btn').css('border-style', 'none');
    });
});