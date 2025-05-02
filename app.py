from flask import Flask, request, jsonify
from neo4j_handler import *

app = Flask(__name__)

@app.route('/users/count', methods=['GET'])
def users_count():
    try:
        count = count_users()
        return jsonify({"user_count": count}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# UC-1
@app.route('/create', methods=['POST'])
def create_new_user():
    data = request.get_json()
    name = data.get("name")
    age = data.get("age")
    city = data.get("city")

    if not name or not age or not city:
        return jsonify({"error": "All attributes of a user are required."}), 400

    try:
        message = create_user(name, age, city)
        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# UC-5
@app.route('/follow', methods=['POST'])
def follow_endpoint():
    data = request.get_json()
    current_user = data.get("current_user")
    target = data.get("target")

    if not current_user or not target:
        return jsonify({"error": "Both 'current_user' and 'target' are required."}), 400

    try:
        message = follow(current_user, target)
        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# UC-6
@app.route('/unfollow', methods=['POST'])
def unfollow_endpoint():
    data = request.get_json()
    current_user = data.get("current_user")
    target = data.get("target")

    if not current_user or not target:
        return jsonify({"error": "Both 'current_user' and 'target' are required."}), 400

    try:
        message = unfollow(current_user, target)
        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# UC-7
@app.route('/connections/<user_name>', methods=['GET'])
def connections_of_user(user_name):
    try:
        followers = get_followers(user_name)
        following = get_following(user_name)
        return jsonify({"user": user_name, "followers": followers, "following": following}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# UC-8
@app.route('/mutuals/<user_name1>/<user_name2>', methods=['GET'])
def mutual_friends(user_name1, user_name2):
    try:
        mutuals = get_mutual_friends(user_name1, user_name2)
        return jsonify({"user 1": user_name1, "user 2": user_name2, "mutual friends": mutuals}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#UC-10
@app.route('/users/<name_substring>', methods=['GET'])
def search_users(name_substring):
    try:
        users = get_users_by_name(name_substring)
        return jsonify({"users": users}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True)
