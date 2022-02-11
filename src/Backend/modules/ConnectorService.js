const fs = require('fs');
const path = require('path');
var idr = require('./InputDataReceiver');
const { FILE } = require('dns');

function writeAPIandQuestion (data, filename) {
    console.log('\x1b[32m%s\x1b[0m','Wrinting API URL and question in file: ' + filename);
    const filePath = path.resolve(__dirname, './data-upload-storage/' + filename + ".txt");

    fs.writeFile(filePath, data, function (err) {
        if (err) return console.log(err);

        console.log('\x1b[32m%s\x1b[0m','Successfully saved to disk the file: ' + filename);
    });
}

function getPredictedQuery (file) {
    console.log('\x1b[36m%s\x1b[0m', "Getting prediction from file: ");

    let filename = file;
    let data = "no data"
    const filePath = path.resolve(__dirname, './data-upload-storage/' + filename + '.json')

    console.log('\x1b[36m%s\x1b[0m', filePath);
    data = fs.readFileSync(filePath, {encoding:'utf8', flag:'r'});
    return data;
}

function writePredictedQuery (data, filename) {
    console.log('\x1b[32m%s\x1b[0m','Wrinting the predicted query in file: ' + filename);
    const filePath = path.resolve(__dirname, './data-upload-storage/' + filename + ".txt");

    fs.writeFile(filePath, data, function (err) {
        if (err) return console.log(err);

        console.log('\x1b[32m%s\x1b[0m','Successfully saved to disk the file: ' + filename);
    });
}

function getResponse (file) {
    console.log('\x1b[36m%s\x1b[0m', "Getting response from file: ");

    let filename = file;
    let data = "no data"
    const filePath = path.resolve(__dirname, './data-upload-storage/' + filename + '.json')

    console.log('\x1b[36m%s\x1b[0m', filePath);
    data = fs.readFileSync(filePath, {encoding:'utf8', flag:'r'});
    return data;
}


module.exports = {
    writeAPIandQuestion,
    getPredictedQuery,
    writePredictedQuery,
    getResponse
}