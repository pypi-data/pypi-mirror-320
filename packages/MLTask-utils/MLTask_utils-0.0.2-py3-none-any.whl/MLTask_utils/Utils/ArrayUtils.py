def get_first_middle_and_last_item(array):
    """
    Returns the first, last, and middle items from an array of strings.

    Args:
        array (list): The input array of strings.

    Returns:
        list: A list containing the first, last, and middle items from the array. If the array is empty,
              an empty list is returned.

    Example usage:
        >>> items = get_items(['apple', 'banana', 'cherry', 'date', 'elderberry'])
        >>> print(items)
        ['apple', 'elderberry', 'cherry']

    """
    if not array:
        return []

    first_item = array[0]
    last_item = array[-1]
    middle_item = array[len(array) // 2]
    return [first_item, last_item, middle_item]
