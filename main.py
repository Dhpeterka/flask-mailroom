import os
import base64
import peewee

from flask import Flask, render_template, request, redirect, url_for, session

from model import Donor, Donation

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('all'))

@app.route('/donations/')
def all():
    donations = Donation.select()
    return render_template('donations.jinja2', donations=donations)

@app.route('/donations/<name>')
def get_donor(name):
    if str(name) == 'all':
        redirect(url_for('all'))

    else:
        donor = Donor.select().where(Donor.name==name).get()
        donations = Donation.select().where(Donation.donor==donor)
    return render_template('donations.jinja2',
                           donations=donations)

@app.route('/new_donation', methods=['GET', 'POST'])
def new_donation():
    if request.method == 'POST':
        name = request.form['name']
        amount = request.form['amount']

        try:
            donor = Donor.select().where(Donor.name==name).get()
            Donation(donor=donor, value=amount).save()

        except peewee.DoesNotExist:
            return redirect(f"/dnf/{name}/{amount}")

        if donor:
            return redirect(url_for('all'))

    else:
        return render_template('add_donation.jinja2')


@app.route('/dnf/<name>/<int:amount>', methods=['GET', 'POST'])
def not_found(name, amount):
    if request.method == 'POST':
        donor = Donor(name=name)
        donor.save()

        Donation(donor=donor, value=amount).save()

        return redirect(url_for('all'))

    else:
        return render_template('donor_not_found.jinja2',
                        name=name,
                        amount=amount)


@app.route('/new_donor', methods=['GET', 'POST'])
def add_donor():
    if request.method == 'POST':
        try:
            donor = Donor(name=request.form['name'])
            donor.save()
    
            Donation(donor=donor,
                     value=request.form['amount']).save()
            return redirect(url_for('all'))

        except peewee.IntegrityError:
            return render_template('new_donor.jinja2',
                                   error=f'{request.form["name"]} already exists as a Donor.  Try Again.')

    else:
        return render_template('new_donor.jinja2')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)

