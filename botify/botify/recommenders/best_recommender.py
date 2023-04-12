from .toppop import TopPop
from .recommender import Recommender
import random

LIKE_THRESHOLD = 0.5


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
            self.history[user] = []

        previous_track = self.tracks_redis.get(prev_track)
        if previous_track is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        self.history[user].append((prev_track, prev_track_time))
        all_recommendations = []
        listened_tracks = set()
        for track, time in self.history[user]:
            listened_tracks.add(track)
            if time > LIKE_THRESHOLD:
                t = self.tracks_redis.get(track)
                track_data = self.catalog.from_bytes(t)
                rec = track_data.recommendations
                if rec:
                    all_recommendations.extend(list(rec))

        random.shuffle(all_recommendations)
        for t in all_recommendations:
            if t not in listened_tracks:
                return t
        return self.fallback.recommend_next(user, prev_track, prev_track_time)
