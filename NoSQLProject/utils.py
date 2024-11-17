from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:Wl3Y3BsOs5FEbXa0@nosqltestcluster.5q339.mongodb.net/')
db = client['NoSQL_ProjectDatabase']
user_fitness_data = db['user_fitness_data']
users = db['users']