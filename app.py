from flask import Flask, request, redirect, render_template, url_for
from bson import ObjectId
from pymongo.mongo_client import MongoClient

import certifi

ca = certifi.where()
############################################################
# SETUP
############################################################

app = Flask(__name__)
uri = "mongodb+srv://dbUSer:fgzgzNrEMHOvh5P1@marcodominicanu.bspya9y.mongodb.net/?retryWrites=true&w=majority"
# app.config["MONGO_URI"] = "mongodb://localhost:27017/plantsDatabase"
# mongo = PyMongo(app)

#Connection String
#mongodb+srv://dbUSer:fgzgzNrEMHOvh5P1@marcodominicanu.bspya9y.mongodb.net/?retryWrites=true&w=majority
client = MongoClient(uri, tlsCAFile=ca)

db = client.plantsDatabase
# username: dbUSer
# password: fgzgzNrEMHOvh5P1
############################################################
# ROUTES
############################################################

# Send a ping to confirm a successful connection

@app.route('/')
def plants_list():
    """Display the plants list page."""

    # Replace the following line with a database call to retrieve *all*
    # plants from the Mongo database's `plants` collection.
    plants_data_cursor = db.plants.find()
    plants_data = list(plants_data_cursor)

    context = {
        'plants': plants_data,
    }
    return render_template('plants_list.html', **context)

@app.route('/about')
def about():
    """Display the about page."""
    return render_template('about.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the plant creation page & process data from the creation form."""
    if request.method == 'POST':
        # Get the new plant's name, variety, photo, & date planted, and 
        # store them in the object below.
        name_new_plant = request.form.get('plant_name')
        variety_new_plant = request.form.get('variety')
        url_new_plant = request.form.get('photo')
        date_new_plant = request.form.get('date_planted')
        new_plant = {
            'name': name_new_plant,
            'variety': variety_new_plant,
            'photo_url': url_new_plant,
            'date_planted': date_new_plant
        }
        # Make an `insert_one` database call to insert the object into the
        # database's `plants` collection, and get its inserted id. Pass the 
        # inserted id into the redirect call below.
        db.plants.insert_one(new_plant)
        new_plant = db.plants.find_one({'name': name_new_plant})
        new_plant_id = str(new_plant['_id'])
        
        return redirect(url_for('detail', plant_id=new_plant_id))

    else:
        return render_template('create.html')

@app.route('/plant/<plant_id>')
def detail(plant_id):
    """Display the plant detail page & process data from the harvest form."""

    # Replace the following line with a database call to retrieve *one*
    # plant from the database, whose id matches the id passed in via the URL.


    plant_id_object = ObjectId(plant_id)
    plant_to_show = db.plants.find_one({'_id': plant_id_object})

    # Use the `find` database operation to find all harvests for the
    # plant's id.
    # HINT: This query should be on the `harvests` collection, not the `plants`
    # collection.
    harvests = db.harvests.find({'plant_id': plant_id})

    context = {
        'plant' : plant_to_show,
        'harvests': harvests
    }
    return render_template('detail.html', **context)

@app.route('/harvest/<plant_id>', methods=['POST'])
def harvest(plant_id):
    """
    Accepts a POST request with data for 1 harvest and inserts into database.
    """
    if request.method == 'POST':
        quantity_harvest = request.form.get('harvested_amount')
        date_harvest = request.form.get('date_harvested')

    # Create a new harvest object by passing in the form data from the
    # detail page form.
    new_harvest = {
        'quantity': quantity_harvest, # e.g. '3 tomatoes'
        'date': date_harvest,
        'plant_id': plant_id
    }
    db.harvests.insert_one(new_harvest)
    # Make an `insert_one` database call to insert the object into the 
    # `harvests` collection of the database.

    return redirect(url_for('detail', plant_id=plant_id))

@app.route('/edit/<plant_id>', methods=['GET', 'POST'])
def edit(plant_id):
    """Shows the edit page and accepts a POST request with edited data."""
    if request.method == 'POST':
        # Make an `update_one` database call to update the plant with the
        # given id. Make sure to put the updated fields in the `$set` object.
        new_name = request.form.get('plant_name')
        new_variety = request.form.get('variety')
        new_photo = request.form.get('photo')
        new_date = request.form.get('date_planted')

        plant_id_object = ObjectId(plant_id)

        searchParam = {'_id': plant_id_object}
        changeParam = {
            '$set': {
                'name': new_name, 
                'variety': new_variety,
                'photo_url': new_photo,
                'date_planted': new_date
                }
                }
       
        db.plants.update(searchParam, changeParam)

        return redirect(url_for('detail', plant_id=plant_id))
    else:
        # Make a `find_one` database call to get the plant object with the
        # passed-in _id.
        plant_id_object = ObjectId(plant_id)
        plant_to_show = db.plants.find_one({'_id': plant_id_object})

        context = {
            'plant': plant_to_show
        }

        return render_template('edit.html', **context)

@app.route('/delete/<plant_id>', methods=['POST'])
def delete(plant_id):
    # Make a `delete_one` database call to delete the plant with the given
    # id.
    plant_id_object = ObjectId(plant_id)
    db.plants.delete_one({'_id': plant_id_object})

    # Also, make a `delete_many` database call to delete all harvests with
    # the given plant id.
    db.harvests.delete_many({'plant_id': plant_id})

    return redirect(url_for('plants_list'))

if __name__ == '__main__':
    app.run(debug=True)

