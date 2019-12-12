import numpy as np
import scipy as sp
import scipy.stats
from collections import OrderedDict

from utilities import random_groups


class Simulator(object):

    def __init__(self, point_dim, landmark_dim, num_points, num_landmarks):

        self.point_dim = point_dim
        self.landmark_dim = landmark_dim
        self.num_points = num_points
        self.num_landmarks = num_landmarks

        self.num_classes = np.random.choice(10) + 1

        self.points = 10 * np.random.rand(self.num_points, self.point_dim)
        self.landmarks = 10 * np.random.rand(self.num_landmarks, self.landmark_dim)

        self.landmark_labels = np.random.choice(self.num_classes, self.num_landmarks)

        ortho_group = sp.stats.ortho_group
        if self.point_dim > 1:
            self.principal_dirs = [ortho_group.rvs(self.point_dim)[:self.landmark_dim, :] for _ in range(self.num_classes)]
        else:
            rvs = [np.random.rand(self.landmark_dim, 1) for _ in range(self.num_classes)]
            self.principal_dirs = [np.divide(x, np.linalg.norm(x)) for x in rvs]
        self.landmark_orientation = [self.principal_dirs[label] for label in self.landmark_labels]

        point_ids = np.arange(self.num_points).tolist()
        self.odometry_pairs = list(zip(point_ids, point_ids[1:]))

        landmark_ids, point_ids = np.meshgrid(np.arange(self.num_landmarks), np.arange(self.num_points))
        landmark_ids, point_ids = np.ravel(landmark_ids), np.ravel(point_ids)
        uncovered_landmarks = set(np.arange(self.num_landmarks))
        all_observation_ids = iter(np.random.permutation(self.num_points * self.num_landmarks))
        self.observation_pairs = []
        while len(uncovered_landmarks) > 0:
            i = next(all_observation_ids)
            self.observation_pairs.append((point_ids[i], landmark_ids[i]))
            uncovered_landmarks = uncovered_landmarks.difference({landmark_ids[i]})
        self.observation_pairs = sorted(self.observation_pairs, key=lambda x: x[0])
        self.num_observations = len(self.observation_pairs)

        self.observed_landmarks = list(OrderedDict.fromkeys(list(zip(*self.observation_pairs))[1]))

    def odometry_factors(self):

        if self.point_dim > 1:
            ortho_group = sp.stats.ortho_group
            rs = [ortho_group.rvs(self.point_dim) for _ in self.odometry_pairs]
        else:
            rs = [np.array([1.]) for _ in self.odometry_pairs]

        ts = [np.dot(rs[i].T, self.points[v, :] - self.points[u, :])
              for i, (u, v) in enumerate(self.odometry_pairs)]

        return self.odometry_pairs, rs, ts


    def observation_factors(self):

        hs = [self.landmark_orientation[v] for _, v in self.observation_pairs]

        ds = [self.landmarks[v, :] - np.dot(self.landmark_orientation[v], self.points[u, :])
              for (u, v) in self.observation_pairs]

        return self.observation_pairs, hs, ds


MAX_DIM = 3
MAX_POINTS = 2000
MAX_LANDMARKS = 100


def new_simulation(point_dim=None, landmark_dim=None, num_points=None, num_landmarks=None, seed=None):
    np.random.seed(seed)

    if point_dim is None:
        point_dim = np.random.choice(np.arange(1, MAX_DIM + 1))

    if landmark_dim is None:
        landmark_dim = np.random.choice(np.arange(1, MAX_DIM + 1))

    if num_points is None:
        num_points = np.random.choice(np.arange(np.floor_divide(MAX_POINTS, 5), MAX_POINTS + 1))

    if num_landmarks is None:
        num_landmarks = np.random.choice(
            np.arange(np.floor_divide(MAX_LANDMARKS, 5), MAX_LANDMARKS + 1))

    return Simulator(point_dim, landmark_dim, num_points, num_landmarks)
