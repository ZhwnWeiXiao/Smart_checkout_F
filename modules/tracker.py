# modules/tracker.py
import numpy as np
from .sort import Sort  # 相對 import

class Tracker:
    def __init__(self,
                 max_age=30,         # 斷開後最多還能維持幾幀
                 min_hits=10,        # 物件至少要持續偵測幾幀才算正式生效
                 iou_thresh=0.3):   # 匹配時最小 IOU
        self.sorter = Sort(max_age=max_age,
                           min_hits=min_hits,
                           iou_threshold=iou_thresh)
        self.min_hits = min_hits
        self.seen_ids = set()

    def update(self, dets: np.ndarray):
        """
        dets: np.array of shape [N,5] -> [x1,y1,x2,y2,conf]
        回傳 tracks: list of (x1,y1,x2,y2,track_id)，
        只包含 hit_streak >= min_hits 的穩定 track
        """
        raw_tracks = self.sorter.update(dets) if dets.size else np.empty((0,5))
        stable = []
        # self.sorter.trackers 是按順序存放 KalmanBoxTracker，
        # 它的 id = index，hit_streak 在 tracker.hit_streak
        for t in raw_tracks:
            x1,y1,x2,y2,tid = map(int, t)
            trk = next((tk for tk in self.sorter.trackers if tk.id+1 == tid), None)
            if trk and trk.hit_streak >= self.min_hits:
                stable.append((x1,y1,x2,y2,tid))
        return stable
