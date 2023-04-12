from .toppop import TopPop
from .recommender import Recommender
import random


class BestRecommender(Recommender):
    """
    Recommend tracks closest to the previous one.
    Fall back to the random recommender if no
    recommendations found for the track.
    """

    def __init__(self, tracks_redis, catalog, history):
        self.tracks_redis = tracks_redis
        self.fallback = TopPop(tracks_redis, catalog.top_tracks[:100])
        self.catalog = catalog
        self.history = history

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        if user not in self.history:
            self.history[user] = set()

        previous_track = self.tracks_redis.get(prev_track)
        if previous_track is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        self.history[user].add(prev_track)
        previous_track = self.catalog.from_bytes(previous_track)
        recommendations = previous_track.recommendations
        if not recommendations:
            t = self.fallback.recommend_next(user, prev_track, prev_track_time)
            if t in self.history[user]:
                t = self.fallback.recommend_next(user, prev_track, prev_track_time)
            return t

        shuffled = list(recommendations)
        random.shuffle(shuffled)
        for t in shuffled:
            if t not in self.history[user]:
                return t
        return shuffled[0]
