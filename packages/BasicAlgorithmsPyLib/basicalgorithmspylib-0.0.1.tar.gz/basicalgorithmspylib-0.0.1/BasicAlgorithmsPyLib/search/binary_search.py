from typing import List, Any


def binary_search(array: List[Any], target) -> int:
  """
  Алгоритм бинарного поиска.
  
  Описание: эффективно ищет элемент в отсортированном списке, 
  постоянно деля диапазон поиска пополам.
  
  Эффективен: в большом отсортированном списке.
  """
  left, right = 0, len(array) - 1
  
  while left <= right:
    mid: int = (left + right) // 2  # Находим индекс посередине, знак '//' - целочисленное деление, так как мы ищем именно индекс. 
    
    if array[mid] == target:
      return mid
    elif array[mid] < target:
      left = mid + 1
    else:
      right = mid - 1
  
  return -1