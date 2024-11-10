from pymongo import MongoClient

client = MongoClient('mongodb+srv://dminer:Aahp9NXCLPGO7Pdk@nosqltestcluster.5q339.mongodb.net/')
db = client['NoSQL_ProjectDatabase']
user_fitness_data = db['user_fitness_data']