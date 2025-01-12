def validate_segmentation_inputs(y_true, y_pred):
    """
    Validate the inputs for type and shape.
    """
    if not isinstance(y_true, (list, tuple)) or not isinstance(y_pred, (list, tuple)):
        raise TypeError("Both y_true and y_pred must be lists or tuples.")

    if len(y_true) != len(y_pred):
        raise ValueError("Length of y_true and y_pred must be the same.")

    if not all(isinstance(x, (int, float)) for x in y_true + y_pred):
        raise TypeError("All elements in y_true and y_pred must be numeric.")

def dice_score(y_true, y_pred, threshold=0.5):
    """
    Compute the Dice Score.
    
    Args:
        y_true (list or tuple): Ground truth binary values.
        y_pred (list or tuple): Predicted values (probabilities or binary).
        threshold (float): Threshold to binarize y_pred if necessary.
        
    Returns:
        float: Dice Score.
    """
    validate_segmentation_inputs(y_true, y_pred)
    
    # Binarize predictions based on threshold
    y_pred = [1 if p >= threshold else 0 for p in y_pred]
    
    # Calculate intersection and union
    intersection = sum(yt * yp for yt, yp in zip(y_true, y_pred))
    total = sum(y_true) + sum(y_pred)
    
    if total == 0:
        return 1.0  # Perfect match if both are completely empty

    return 2 * intersection / total
