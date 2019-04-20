from flask import Flask, render_template, jsonify, request, session, send_file
from plotting import generate_plot, generate_data
from bokeh.embed import components
from sqlalchemy import and_
from database import *
from random import sample

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.secret_key = 'mykey'
db.init_app(app)


def create_trial_list(participant_id):
    """
    Creates a list of trial dicts by subsampling the inner table for each of the items in the outer.
    (As described and discussed in the report)

    :param participant_id:
    :return:
    """
    result = []
    outer_sorted = db.session.query(TrialTableOuter).filter(TrialTableOuter.participant_id == participant_id).all()
    all_inner = db.session.query(TrialTableInner).filter(TrialTableInner.participant_id == participant_id).all()
    for i, outer in enumerate(outer_sorted):
        for j, inner in enumerate(sample(all_inner, 33)):
            result.append(dict(slope_type=outer.slope_type,
                               plot_type=inner.plot_type,
                               residual=inner.residual,
                               slope=inner.slope,
                               id=i * 33 + j))
    return result

@app.route('/')
def entry_point():
    return render_template("demography.html")

@app.route('/start/', methods=['POST'])
def start_survey():
    d = request.json
    participant = User(gender=d['gender'], birth_year=d['year'], field=d['major'], experience=d['experience'])
    db.session.add(participant)
    db.session.commit()
    session['participant_id'] = participant.id
    session['trial_table'] = create_trial_list(participant.id)
    session['current_trial_index'] = 0
    return render_template("index.html")

@app.route('/survey/')
def survey_page():
    return render_template("index.html")

@app.route('/get_plot/', methods=['POST'])
def get_plot():
    try:
        # This fails if it is the first time get_plot is called
        # Get all necessary values from the session and add it to the database
        set_slope = request.json['slope']
        last_trial = session['current_trial']
        d = DataEntry(
            sigma=last_trial['residual'],
            sign = 1,
            slope_type = last_trial['slope_type'],
            graph_type = last_trial['plot_type'],

            user_slope = set_slope,
            true_slope =  float(last_trial['slope']),

            error = set_slope - float(last_trial['slope']),
            unsigned_error = abs(set_slope - float(last_trial['slope'])),
            user_id = session['participant_id']
        )

        db.session.add(d)
        db.session.commit()
    except Exception as e:
        pass
    participant_id = session['participant_id']
    trial_table = session['trial_table']

    current_trial_index = session['current_trial_index'] + 1
    session['current_trial_index'] = current_trial_index

    # If there are more trials for this participant, get the next
    # from the session.
    if len(trial_table) > current_trial_index:
        trial = trial_table[current_trial_index]
        session['current_trial'] = trial
        residuals = float(trial['residual'])
        slope = float(trial['slope'])
        amplitude = 1.0 + slope
        exponent = 1.0 + slope
        ds, trendline = generate_data(slope_type=trial['slope_type'],
                                      plot_type=trial['plot_type'],
                                      slope=slope,
                                      amplitude=amplitude,
                                      exponent=exponent,
                                      mu=residuals)
        script, div = components(generate_plot(ds, trendline, plot_type=trial['plot_type'], slope_type=trial['slope_type']))
        return jsonify(dict(plot=script+div, finished = False))
    else:
        return jsonify(dict(plot="", finished = True))

@app.route('/done')
def done():
    return render_template("index.html")

@app.route('/export_file/')
def export():
    zip_name = export_all_tables()
    return send_file(zip_name,  as_attachment=True, attachment_filename=zip_name)


if __name__ == '__main__':
    # if the database is empty, import the touchstone data
    import_trial_tables("resources/Experiment 3_ Inner - 190419 125015.csv",
                        "resources/Experiment 3_ Outer - 190419 125010.csv")

    app.run(debug=True)