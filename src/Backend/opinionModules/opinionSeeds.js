const fs = require('fs');
const { exec } = require("child_process");

async function callQueryGenerator() {

    console.log("___Calling NLP module___")
}

async function callExplorer() {

    console.log("___Calling Explorer module___")
}

const Opinion = {
    callQueryGenerator,
    callExplorer
}

module.exports = Opinion;