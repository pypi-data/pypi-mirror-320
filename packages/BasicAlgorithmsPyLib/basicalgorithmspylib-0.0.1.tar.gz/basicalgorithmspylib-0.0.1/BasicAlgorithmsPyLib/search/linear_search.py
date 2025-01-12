from typing import List, Any


def linear_search(array: List[Any], target) -> int:
  """
  Алгоритм линейного поиска.
  
  Описание: последовательно просматривает все элементы
  в списке до тех пор, пока не найдет нужный.
  
  Эффективен: в небольшом неотсортированном списке.
  """
  for index, element in enumerate(array):
    if element == target:
      return index
  
  return -1