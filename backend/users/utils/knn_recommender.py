import numpy as np
from sklearn.neighbors import NearestNeighbors
from django.db.models import Avg
from users.models import ClientProfile, WorkoutPlanRating, WorkoutPlan

#Function that encodes client as a feature vector to compare similarity to other clients
def encode_client_features(client):
    #Takes categorical features and numerically encodes them
    activity_map = {
        "sedentary": 1,
        "lightly_active": 2,
        "moderately_active": 3,
        "very_active": 4,
        "super_active": 5
    }
    gender_map = {"male": 0, "female": 1, "other": 2}
    goal_map = {"lose_weight": 0, "maintain_weight": 1, "gain_muscle": 2}

    #Returns the feature map for the client passed to the function
    return [
        client.age or 0,
        client.height or 0,
        client.weight or 0,
        activity_map.get(client.activity_level, 3),
        gender_map.get(client.gender, 2),
        goal_map.get(client.goal, 1)
    ]

#Function to return workouts from similar clients, relative totarget client
def get_top_recommended_workouts_for_client(target_client, k=5):
    all_clients = ClientProfile.objects.filter(workout_ratings__isnull=False).distinct()

    #If there are less than 2 clients, not enough data so return nothing
    if len(all_clients) < 2:
        return []  
    
    #Array for storing each client's feature vector
    features = []

    #Array for storing each feature vector's corresponding client ID
    index_to_client = []

    #Dictionary where keys will be Client IDs, values will be list of their top rated workouts
    plan_ids_by_client = {}

    #For each client, does the following:
    #1. Encodes them as a feature vector
    #2. Appends their feature vector to features array
    #3. Appends client's ID to another corresponding array, indexes match for both arrays
    for client in all_clients:
        vector = encode_client_features(client)
        features.append(vector)
        index_to_client.append(client.id)

        #For each client, gets every workout they've rated
        #Sorts them in descending rating order (so top rated workouts are first)
        top_plans = (
            WorkoutPlanRating.objects
            .filter(client=client)
            .order_by('-rating')
            .values_list('workout_plan_id', flat=True)
        )

        #Populates dictionary of clientID: [top rated workout] pairs
        plan_ids_by_client[client.id] = list(top_plans)

    #Sets up KNN model to find K nearest neighbours to the target
    #len(features) - 1 ensures that if there's less than k values, avoids requesting more neighbours than available
    knn = NearestNeighbors(n_neighbors=min(k, len(features) - 1), metric='euclidean')

    #Converts list of features into a matrix
    #Each row corresponds to a client, each column corresponds to a specific feature
    knn.fit(np.array(features))

    #Takes target client, encodes them into feature vector, reshapes into 2d array with 1 row
    target_vector = np.array(encode_client_features(target_client)).reshape(1, -1)

    #Indices stores the row numbers of the nearest neighbours in the 2d features array
    #Distances aren't needed
    distances, indices = knn.kneighbors(target_vector)

    #Holds IDs of all workout plans recommended to target
    recommended_plan_ids = []

    #Indices is a 2d array, so to access the first/only row have to access index 0
    for neighbour_client_index in indices[0]:
        #Gets id of neighbour client
        neighbor_client_id = index_to_client[neighbour_client_index]

        #.extend() used instead of append so that individual plan ids are added, rather than arrays of plan ids
        recommended_plan_ids.extend(plan_ids_by_client[neighbor_client_id])


    #Remove duplicates and workouts already rated by the target user
    already_rated = set(
        WorkoutPlanRating.objects.filter(client=target_client).values_list("workout_plan_id", flat=True)
    )

    final_plan_ids = []
    #Loops through and adds plan ids to final_plan_ids array
    for plan_id in recommended_plan_ids:
        if plan_id not in already_rated and plan_id not in final_plan_ids:
            final_plan_ids.append(plan_id)

    #Return top 5 recommendations
    #Filters WorkoutPlan where the ids match the final plan ids
    return WorkoutPlan.objects.filter(id__in=final_plan_ids[:5])  
