from typing import Literal, Optional, Tuple, Union

import numpy as np
from scipy.optimize import basinhopping
from scipy.stats import percentileofscore
from sklearn.metrics import matthews_corrcoef
from sklearn.utils import check_array


def negative_mcc_threshold(threshold: Union[int, float],
                           scores: Union[np.ndarray, list],
                           labels: Union[np.ndarray, list],) -> float:
    """Caculate the coresponding MCC score."""

    pred = np.zeros(len(scores), dtype=int)
    pred[scores >= threshold] = 1

    return -(matthews_corrcoef(labels, pred) + 1)


def optimize_threshold(fit_scores: Union[np.ndarray, list],
                       eval_scores: Union[np.ndarray, list],
                       labels: Union[np.ndarray, list],
                       policy: Optional[Literal['balanced',
                                                'hard', 'soft']] = 'balanced',
                       ) -> Tuple[float, float]:
    r"""Find the optimal threshold for the fitted OutlierDetector class.

    Given even a set of labeled data the optimize_threshold can be used to find the
    best threshold based on the user's criterion. This threshold can be used to
    refit the training data with the same model with the new threshold.

    Args:
        fit_scores (array-like): The array of the fitted decsion scores of the OutlierDetector class.
        eval_scores (array-like): The array of the evaluated decsion scores  from the labeled data using the OutlierDetector class.
        labels (array-like): The array of the binary labels for the threshold optimization.
        policy (str, optional): Policy type that dictates the handling of the optimization. It can be one of the following:
            - 'balanced': Uses a balanced approach by maximizing the Matthews Correlation Coefficient
            - 'hard': Uses a strict approach by setting the threshold as the minimum between the max inlier or min outlier score
            - 'soft': Uses a lenient approach by setting the threshold as the maximum between the max inlier or min outlier score
            Defaults to 'balanced'.


    Returns:
        tuple: A tuple containing two float values.
            - The first value represents thresholded decision score.
            - The second value represents the percentile of the threshold with respect to the fitted model.

    """

    fit_scores = check_array(fit_scores, ensure_2d=False)
    eval_scores = check_array(eval_scores, ensure_2d=False)
    labels = check_array(labels, ensure_2d=False)

    min_out = np.min(eval_scores[labels == 1])
    max_in = np.max(eval_scores[labels == 0])

    fit_max = np.max(fit_scores)

    if policy == 'hard':

        best_thresh = min(min_out, max_in)

    elif policy == 'soft':

        best_thresh = max(min_out, max_in)

    else:

        fit_mean = np.mean(fit_scores)
        fit_median = np.median(fit_scores)
        fit_std = np.std(fit_scores)

        # Find a global minimum option
        minimizer_kwargs = {'method': 'L-BFGS-B', 'args': (eval_scores, labels),
                            'bounds': [(fit_median, 2*fit_max)]}

        result = basinhopping(negative_mcc_threshold, niter=200,
                              x0=fit_mean + fit_std,
                              minimizer_kwargs=minimizer_kwargs,
                              stepsize=fit_std, seed=1234)

        best_thresh = result.x[0]

    if best_thresh > fit_max:
        perc = best_thresh/fit_max * 100

    else:
        perc = percentileofscore(fit_scores, best_thresh, kind='rank')

    return best_thresh, perc
