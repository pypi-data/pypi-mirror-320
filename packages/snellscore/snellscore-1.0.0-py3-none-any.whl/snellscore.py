#!/usr/bin/env python
# coding: utf-8

# Copyright (C) 2024-2025 Igor Loschinin.
# Distributed under the lgplv3 software license, see the accompanying
# Everyone is permitted to copy and distribute verbatim copies
# of this license document, but changing it is not allowed.

__author__ = "Igor Loschinin (igor.loschinin@gmail.com)"
__all__ = ('Snell', )

import numpy as np
import pandas as pd


class Snell(object):
	""" Calculate Snell scores.

	This class calculates Snell scores given counts of scores by
	subpopulation.
	"""

	def __init__(self, standard: bool | None = None) -> None:
		""" Initialize the Snell scoring object.

		:param standard: If True, standardizes the scores to a 0-100 scale.
		"""
		self._standard = standard

		self._score = None
		self._score_std = None

	@property
	def score(self) -> pd.Series | None:
		""" Get the calculated Snell scores.

		:return: Series containing Snell scores, or None if not calculated.
		"""
		return self._score

	@property
	def score_standard(self) -> pd.Series | None:
		""" Get the standardized Snell scores.

		:return: Series containing standardized Snell scores, or None if
			not calculated.
		"""
		return self._score_std

	def run(self, table: pd.DataFrame | None) -> None:
		""" Main Snell scoring function to calculate Snell scores given a
		frequency table.

		:param table: Frequency table with group labels in rows and the
			original scores in columns. The table must have at least 3 columns.
		:raises ValueError: If the table has fewer than 3 columns.
		"""

		try:
			if table.shape[1] <= 2:
				raise ValueError(
					"Snell scoring requires at least 3 categories."
				)

			# Count of observations in each group
			group_counts = table.sum(axis=1).values

			# Count of observations in each scoring category
			category_totals = table.sum(axis=0)

			noncum_probabilities = table.div(group_counts, axis=0)
			cum_probabilities = self._build_cumprob(noncum_probabilities)

			pairwise_adjusted_probs = self._calc_pairwise_adjusted_probs(
				table, cum_probabilities
			)
			ranges = self._ranges(category_totals, pairwise_adjusted_probs)
			boundaries = self._boundaries(ranges)

			self._score = self._calc_scores(
				boundaries,
				noncum_probabilities,
				category_totals
			)

			if self._standard:
				self._score_std = self._standardization(self._score)

		except Exception as e:
			raise e

	@staticmethod
	def _build_cumprob(
			noncum_probabilities: pd.DataFrame
	) -> pd.DataFrame | None:
		""" Build a table of cumulative probabilities for each category.

		:param noncum_probabilities: Non-cumulative probabilities for each
			category.
		:return: DataFrame with cumulative probabilities for each category.
		"""
		return noncum_probabilities.cumsum(axis=1)

	@staticmethod
	def _calc_pairwise_adjusted_probs(
			observation_counts: pd.DataFrame,
			probabilities: pd.DataFrame
	) -> pd.Series:
		""" Compute the probability that an observation falls in a category
		or lower, multiplied by the category probabilities.

		:param observation_counts: Table with observation counts for each
			category.
		:param probabilities: Cumulative probabilities, as calculated
			by _build_cumprob.
		:return: Series with the computed values.
		"""
		pairwise_sums = observation_counts.iloc[:, :-1] + \
						observation_counts.iloc[:, 1:].values
		return (pairwise_sums * probabilities.iloc[:, :-1]).sum(axis=0)

	@staticmethod
	def _equation_first(
			nj: np.int64,
			nj1: np.int64,
			xj1: float,
			nnp: np.float64
	) -> np.float64:
		""" Calculate the range of all categories other than the second
		to last.

		:param nj: Count of observations in the current category.
		:param nj1: Count of observations in the next category.
		:param xj1: Boundary for the next category.
		:param nnp: Adjusted cumulative probability.
		:return: Calculated range.
		"""
		return np.log(nj / (nj1 / (np.exp(xj1) - 1) - nj + nnp) + 1)

	@staticmethod
	def _equation_last(
			nk1: np.int64,
			nnp: np.float64
	) -> np.float64:
		""" Calculate the range of the second to last category.

		:param nk1: Count of observations in the last category.
		:param nnp: Adjusted cumulative probability for the last category.
		:return: Calculated range.
		"""
		try:
			return np.log((nk1 / (nnp - nk1)) + 1)

		except ZeroDivisionError as er:
			raise er

	def _ranges(
			self,
			category_totals: pd.Series,
			pairwise_adjusted_probs: pd.Series
	) -> pd.Series:
		""" Compute the range between the two boundaries for the inner set of
		categories.

		:param category_totals: Totals for each scoring category.
		:param pairwise_adjusted_probs: Adjusted cumulative probabilities.
		:return: Series with calculated ranges.
		"""
		ranges = np.zeros(len(category_totals) - 2)
		xj1 = 0

		for i in reversed(range(len(ranges))):
			if i == len(ranges) - 1:
				ranges[i] = self._equation_last(
					category_totals.iloc[i + 1],
					pairwise_adjusted_probs.iloc[i + 1]
				)
			else:
				ranges[i] = self._equation_first(
					category_totals.iloc[i + 1],
					category_totals.iloc[i + 2],
					xj1,
					pairwise_adjusted_probs.iloc[i + 1]
				)
			xj1 = ranges[i]  # xj1 for the next iteration is the result from this one

		return pd.Series(ranges, index=category_totals.index[1:-1])

	@staticmethod
	def _boundaries(ranges: pd.Series) -> pd.Series:
		""" Calculate the rightmost boundary for each category.

		:param ranges: Ranges for each category.
		:return: Series with boundaries.
		"""
		# Initialize a vector to store the results
		boundaries = np.zeros(len(ranges) + 1)

		for i in range(1, len(boundaries)):
			boundaries[i] = boundaries[i - 1] + ranges.iloc[i - 1]

		return pd.Series(boundaries)

	@staticmethod
	def _calc_deflection(probabilities: pd.Series) -> np.float64:
		""" Determine how far from the outer boundaries the outermost
		category scores lie.

		:param probabilities: Probabilities for the category.
		:return: Calculated deflection value.
		"""
		mean_p = probabilities.mean()

		return -np.log(1 - mean_p) / mean_p

	def _calc_scores(
			self,
			boundaries: pd.Series,
			noncum_prob: pd.DataFrame,
			category_totals: pd.Series
	) -> pd.Series:
		""" Calculate scores for each category.

		:param boundaries: Boundary points for each category.
		:param noncum_prob: Non-cumulative probabilities for each
			category.
		:param category_totals: Totals for each scoring category.
		:return: Series with calculated scores.
		"""
		scores = np.zeros(len(category_totals))

		deflection_start = self._calc_deflection(noncum_prob.iloc[:, 0])
		deflection_end = self._calc_deflection(noncum_prob.iloc[:, -1])

		scores[0] = boundaries.iloc[0] - deflection_start
		scores[1:-1] = \
			boundaries.iloc[1:].values + (boundaries.iloc[:-1].values / 2)
		scores[-1] = boundaries.iloc[-1] + deflection_end

		return pd.Series(scores)

	@staticmethod
	def _standardization(value: pd.Series) -> pd.Series:
		""" Standardize score values from 0 to 100.

		:param value: Series with original score values.
		:return: Series with standardized scores.
		"""
		subtracting = value - value.iloc[0]

		return (subtracting * (100 / subtracting.values[-1])). \
			round().astype('Int16')


if __name__ == "__main__":

	# data = {
	# 	"Category1": [0, 0, 1, 0, 1],
	# 	"Category2": [4, 7, 0, 3, 1],
	# 	"Category3": [25, 44, 20, 28, 15]
	# }

	data = {
		"Category1": [0, 6, 0, 0, 0, 2, 3, 0, 1, 2, 0, 5],
		"Category2": [0, 3, 0, 4, 0, 4, 4, 0, 2, 2, 0, 1],
		"Category3": [0, 1, 3, 1, 0, 3, 3, 1, 0, 2, 0, 1],
		"Category4": [3, 0, 2, 2, 0, 1, 0, 1, 0, 0, 0, 0],
		"Category5": [3, 1, 2, 4, 2, 0, 1, 1, 1, 2, 4, 1],
		"Category6": [2, 1, 4, 0, 5, 2, 1, 5, 4, 4, 1, 3],
		"Category7": [4, 0, 1, 1, 5, 0, 0, 4, 4, 0, 7, 1],
	}

	# data = {
	# 	"Category1": [9, 7, 14, 11, 0],
	# 	"Category2": [5, 3, 13, 15, 2],
	# 	"Category3": [9, 10, 6, 3, 10],
	# 	"Category4": [13, 20, 7, 5, 30],
	# 	"Category5": [4, 4, 0, 8, 2],
	# 	# "Category4": [40, 45, 50]
	# }

	freq_table = pd.DataFrame(
		data,
		index=[f"Group{item}" for item in range(1, 13)]
		# index=[f"Group{item}" for item in range(1, 6)]
	)
	print(freq_table)

	# Расчёт Snell-оценок
	snell_scores = Snell(standard=True)
	snell_scores.run(freq_table)

	print("Snell Scores:")
	print(snell_scores.score)
	print(snell_scores.score_standard)
