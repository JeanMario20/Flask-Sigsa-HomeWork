from flask import Flask, render_template, request, jsonify
import requests
app = Flask(__name__)




#app 2
@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'GET':
        return render_template('index.html')
    
    if request.form['search']:
        url = "https://api.giphy.com/v1/gifs/search?api_key=O5ZFkyH3iuUYObyXroXxXc4sL7uAALE9&limit10&q=" + request.form['search']
        giphy = requests.get(url)
        dataGiphy = giphy.json()
        #print(dataGiphy)
        return render_template('index.html', data = dataGiphy['data'])
    else:
        return render_template('index.html')


#app 2
@app.route("/video")
def show_video():
    videos = requests.get("http://127.0.0.1:5000/api/v1/videos/").json()
    return render_template("pelis.html", videos=videos)

if __name__ == "__main__":
    app.run(debug=True, port=3000)
    