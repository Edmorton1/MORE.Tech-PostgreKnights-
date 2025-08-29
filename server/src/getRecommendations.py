from typing import List
from recommendations.post_recommendations import PostRecommendations
from recommendations.pre_recommendations import PreRecommendations



def getRecommendations(query: str) -> List[str]:
    preRecsList = PreRecommendations(query).preprocessing()
    postRecsList = PostRecommendations(query).postprocessing()
    recsList = preRecsList + postRecsList
    print(recsList)

    return recsList
