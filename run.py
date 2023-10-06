from flask import Flask
from flask import render_template, request, jsonify
from utils import ga
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        
        # Get the markers data from the post request
        marker_data = eval(request.form.get('markerData'))
        nlocations = len(marker_data)
        
        # Determine GA parameters depending on the problem size
        pop_size = 100 + 10*nlocations
        mut_rate = min(0.01 + nlocations*0.001, 0.1)
        elitism_rate = pop_size//20

        # Initialize the GA object and run it
        ga_obj = ga.GA(locations=marker_data, pop_size=pop_size, mut_rate=mut_rate, elitism_rate=elitism_rate)
        sol_locations, sol_distance = ga_obj.run_ga(termination_criteria=30)

        # Prepare the response for the client and send it
        sol_locations.insert(0, 0)
        sol_locations.append(0)
        sol_latlngs = [{"lat": marker_data[loc]["lat"], "lng": marker_data[loc]["lng"]} for loc in sol_locations]

        response = {"path": sol_latlngs, "distance": round(sol_distance, 2)}
        return jsonify(response)

    return render_template("index.html")

@app.route('/tutorial/')
def tutorial():
    return render_template("tutorial.html")

@app.route('/about/')
def about():
    return render_template("about.html")