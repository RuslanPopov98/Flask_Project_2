from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField
import data
import json
import numpy as np

app = Flask(__name__)
app.secret_key = 'my-super-secret-phrase-I-dont-tell-this-to-nobody'


class Profiles:

    def __init__(self, id_prof):
        self.id = id_prof
        for profile in data.teachers:
            if profile['id'] == id_prof:
                self.name = profile['name']
                self.about = profile['about']
                self.rating = profile['rating']
                self.picture = profile['picture']
                self.price = profile['price']
                self.goals = []
                for i in profile['goals']:
                    self.goals.append(data.goals[i])
                self.free = profile['free']


class UserForm(FlaskForm):
    name = StringField('Имя пользователя')
    phone = StringField('Телеофон пользователя')
    week_day = StringField('День недели')
    time = StringField('Время')
    teacher_id = StringField('Преподаватель')


def check_free_time_in_day(timetable):
    for check_flag in timetable.values():
        if check_flag:
            return True
    return False


def sorted_list_of_dict(dictionary, key, reverse=True):
    return sorted(dictionary, key=lambda x: x[key], reverse=reverse)


@app.route('/')
def render_main():
    rand_profiles = np.random.choice([i for i in range(len(data.teachers))], 6, replace=False)
    list_profiles = []

    for idx in rand_profiles:
        list_profiles.append(data.teachers[idx])

    return render_template("index.html", profiles=list_profiles)


@app.route('/all/', methods=["POST", "GET"])
def render_all_teachers():
    sort_flag = {'inlineFormCustomSelectPref': '4'}
    if request.method == "POST":
        sort_flag = dict(request.form)
    list_profiles = []

    # random case
    if int(sort_flag['inlineFormCustomSelectPref']) == 4:
        rand_profiles = np.random.choice([i for i in range(len(data.teachers))], len(data.teachers), replace=False)

        for idx in rand_profiles:
            list_profiles.append(data.teachers[idx])

    # sort on rating
    if int(sort_flag['inlineFormCustomSelectPref']) == 3:
        list_profiles = sorted_list_of_dict(data.teachers, 'rating')

    # sort on expensiv
    if int(sort_flag['inlineFormCustomSelectPref']) == 1:
        list_profiles = sorted_list_of_dict(data.teachers, 'price')

    # sort on cheap
    if int(sort_flag['inlineFormCustomSelectPref']) == 2:
        list_profiles = sorted_list_of_dict(data.teachers, 'price', False)

    return render_template("all.html", profiles=list_profiles)


@app.route('/goals/<goal>/')
def render_goals(goal):
    list_profiles = []
    for prof in data.teachers:
        if goal in prof["goals"]:
            list_profiles.append(prof)
    list_profiles = sorted_list_of_dict(list_profiles, 'rating')

    return render_template("goal.html", profiles=list_profiles, goal=data.goals[goal].lower())


@app.route('/profiles/<id_teacher>/')
def render_profile(id_teacher):
    profile = Profiles(int(id_teacher))

    for day in profile.free:
        #profile.free[day] = data.days_week[day]
        try:
            if not check_free_time_in_day(profile.free[day]):
                profile.free[day] = "Нет свободных уроков"
        except:
            profile.free[day] = profile.free[day]

    return render_template("profile.html", profile=profile, days_week=data.days_week)


@app.route('/request/')
def render_request():
    return render_template("request.html")


@app.route('/request_done/', methods=["POST"])
def render_request_done():
    user_form = dict(request.form)
    user_form["goal"] = data.purpose_lesson[user_form["goal"]]
    with open('request.json', 'w') as outfile:
        json.dump(user_form, outfile)
    return render_template("request_done.html", user_form=user_form)


@app.route('/booking/<id_teacher>/<day_of_week>/<time>/')
def render_booking(id_teacher, day_of_week, time):
    profile = Profiles(int(id_teacher))
    return render_template("booking.html", profile=profile, day_of_week=data.days_week[day_of_week], time=time)


@app.route('/booking_done/', methods=["POST"])
def render_booking_done():
    user_form = dict(request.form)
    with open('booking.json', 'w') as outfile:
        json.dump(user_form, outfile)
    return render_template("booking_done.html", user_form=user_form)


if __name__ == '__main__':
    app.run()


#app.run(debug=True)

'''
@app.route('/data/')
def render_data():
    return render_template("data_render.html", tours=data.tours)


@app.route('/data/departures/<departure>/')
def render_data_departure(departure):
    return render_template("data_departures.html", dep=departure, data=data)


@app.route('/data/tours/<id>/')
def render_data_tours(id):
    return render_template("data_tours.html", dic=data.tours[int(id)])
'''