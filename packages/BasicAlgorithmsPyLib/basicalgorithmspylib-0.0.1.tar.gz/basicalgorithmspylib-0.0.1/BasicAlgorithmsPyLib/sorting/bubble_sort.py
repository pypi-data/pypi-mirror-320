from typing import List, Any


def bubble_sort(array: List[Any]) -> List[Any]:
  """
  Алгоритм пузырьковая сортировки.
  
  Описание: сравнивает соседние элементы и меняет их местами, 
  если они в неправильном порядке. 
  Повторяет проходы по списку, пока он не будет отсортирован.
  
  Когда пригодится: 
  Проста для понимания, но неэффективна для больших списков.
  """
  n = len(array)
  
  for i in range(n):
    for j in range(0, n - i - 1):
      if array[j] > array[j + 1]:
        array[j], array[j + 1] = array[j + 1], array[j]
  
  return array