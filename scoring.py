"""
Simple module that interprets the leftover_ratio into a textual or numeric score.
"""


def compute_cleanup_score(leftover_ratio):
    """
    Convert the leftover_ratio into a simple label or numeric rating.
    leftover_ratio is typically between 0 and 1.

    You can define thresholds that suit your domain knowledge.
    For example:
      - < 0.02 -> 'Excellent'
      - < 0.05 -> 'Moderate'
      - else -> 'Significant'

    Adjust these thresholds as needed to match real surgical expectations.
    """
    if leftover_ratio < 0.2:
        return "Excellent"
    elif leftover_ratio < 0.5:
        return "Moderate"
    else:
        return "Significant"