var express = require('express');
const path = require('path');
const fileUpload = require('express-fileupload');
const cors = require('cors')
const uuid = require('uuid')
const bodyParser = require("body-parser");;
var expressPooling = require("express-longpoll")
const ConnectorService = require("./ConnectorService");

// const SecurityMiddleware = require("../monitoring/SecurityMiddleware");
const OpinionModule = require("../opinionModules/opinionSeeds");
// const { securityMiddleware, originMiddleware, middlewareResolver } = SecurityMiddleware;

const pipe = (...fns) => (x) => fns.reduce((v, f) => f(v), x);

// const middleware = middlewareResolver(pipe(securityMiddleware, originMiddleware));

class ServerManager{

    static store = {
        file: "",
    };

    static startInstance(){

        var app = express();
        app.use(cors())
        app.use(bodyParser.json());
        app.use(fileUpload());

        app.post('/loader/APIandQuestion', (
            function (req, res) {
                const data = req.body.apiUrl + "\n" + req.body.question; 
                console.log("API URL and question: " + data);

                ConnectorService.writeAPIandQuestion(data, "APIandQuestion");
                res.send("");
            }
        ));

        app.get('/predictor/query', (
            function (req, res) {
                console.log('\x1b[32m%s\x1b[0m','Calling query generator...');

                const rez = OpinionModule.callQueryGenerator("APIandQuestion");
                res.send("");
            }    
        ));

        app.get('/loader/prediction', (
            function (req, res) {
                console.log('\x1b[32m%s\x1b[0m','Waiting for prediction...');

                const result = ConnectorService.getPredictedQuery("APIandQuestion");
                res.send(result);
            }    
        ));

        app.post('/loader/predictedQuery', (
            function (req, res) {
                const data = req.body.predictedQuery; 
                console.log("Predicted query: " + data);

                ConnectorService.writePredictedQuery(data, "predictedQuery");
                res.send("");
            }
        ));

        app.get('/predictor/response', (
            function (req, res) {
                console.log('\x1b[32m%s\x1b[0m','Calling Explorer module...');

                const rez = OpinionModule.callExplorer("predictedQuery");
                res.send("");
            }    
        ));

        app.get('/loader/response', (
            function (req, res) {
                console.log('\x1b[32m%s\x1b[0m','Waiting for response...');

                const result = ConnectorService.getResponse("predictedQuery");
                res.send(result);
            }    
        ));

        app.listen(3000, function () {
            console.log('The application is listening on port 3000!');
        });
        
    } 
}

module.exports.ServerManager = ServerManager