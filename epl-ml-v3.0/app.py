# Import dependencies
from flask import Flask, render_template, request
import os
#from Scripts import eplWebscraperV3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/copies', methods=['POST'])
def copies():
    if request.method=='POST':
        os.popen('cp rankings/DefenderRank.csv rankings/DefenderRank\ copy.csv')
        os.popen('cp rankings/ForwardRank.csv rankings/ForwardRank\ copy.csv')
        os.popen('cp rankings/GoalieRank.csv rankings/GoalieRank\ copy.csv')
        os.popen('cp rankings/MidfielderRank.csv rankings/MidfielderRank\ copy.csv')
        return render_template('copies.html')

@app.route('/update', methods=['POST'], gameweek=request.args.get("gameweek"))
def runScript():
    if request.method=='POST':
        #eplWebscraperV3.webscrape()
        return render_template('update.html')

@app.route('/defenders')
def defenders():
    return render_template('defenders.html')

@app.route('/goalies')
def goalies():
    return render_template('goalies.html')

@app.route('/midfielders')
def midfielders():
    return render_template('midfielders.html')

@app.route('/forwards')
def forwards():
    return render_template('forwards.html')


if __name__ == '__main__':
    app.run
