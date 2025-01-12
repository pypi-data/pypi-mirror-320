from typing import List, Tuple


def find_min_max(array: List[int]) -> Tuple[int, int]:
  """
  Алгоритм нахождения минимума и максимума.
  
  Описание: проходит по списку и находит минимальный или максимальный элемент.
  
  Применение: когда нужно определить крайние значения в данных.
  """
  if not array:
    return None, None  # Если список пустой - возвращаем None, None
  
  minimum = maximum = array[0]
  
  for element in array:
    if element < minimum:
      minimum = element
    if element > maximum:
      maximum = element
  
  return minimum, maximum