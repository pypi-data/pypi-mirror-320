from typing import List, Any
from random import randint
 

def quick_sort(array: List[Any]) -> List[Any]:
  """
  Алгоритм быстрой сортировки.
  
  Описание: 
  выбирает опорный элемент и делит список на две части: 
  элементы меньше опорного и элементы больше опорного. 
  Рекурсивно сортирует эти части.
  
  Оптимизация: 
  выбор опорного элемента может влиять на производительность. 
  Можно рандомизировать выбор.
  
  Когда пригодится: 
  очень эффективна для больших списков, 
  но может быть не так эффективна в худшем случае, 
  когда список уже отсортирован.
  
  Args:
    array: список элементов для сортировки.
  
  Returns:
    Копию отсортированного списка.
  """
  if len(array) <= 1:
    return array
  
  pivot = array[randint(0, len(array) - 1)]
  left: List[Any] = [x for x in array if x < pivot]
  middle: List[Any] = [x for x in array if x == pivot]
  right: List[Any] = [x for x in array if x > pivot]
  
  return quick_sort(left) + middle + quick_sort(right)