
class InputDataReceiver{
    #text;
    #textFile;
    #JsonFile;

    constructor(text, textFile=0, JsonFile=0){
           this.#text = text;
           this.#textFile = textFile;
           this.#JsonFile = JsonFile;
    };

    getText(){
        if(this.#text != null){
            console.log("Everything is ok with the text: " + this.#text);
            return this.#text;
        }
        else
            console.log("There are problems with the text...");
    };

    async getTextFile(){
        try {
            const response = await fetch(this.#textFile);
            const data = await response.text();
            console.log(data);
            return data
        } catch(err) {
            console.log(err);
            return err;
        }
    };
    
    async getJsonFile(){
        try {
            const response = await fetch(this.#JsonFile);
            const data = await response.text();
            console.log(data);
            return data
        } catch(err) {
            console.log(err);
            return err;
        }
    };
}

module.exports.InputDataReceiver = InputDataReceiver