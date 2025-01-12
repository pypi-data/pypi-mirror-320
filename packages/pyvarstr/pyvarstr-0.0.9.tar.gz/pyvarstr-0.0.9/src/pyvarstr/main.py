def help():
  return "dec exdec exlist exsort exclass sort list numpy pandas json visualization kr1 ms5i1 ms5i2 ms5i3"

def dec():
  return """
#1 декоратор, который будет выводить время выполнения функции и сохра-нять его в файл

import time

def measure_running_time(function):
    def wrapper(*args, **kwargs):
      bt = time.time()
      result = function(*args, **kwargs)
      et = time.time()
      f = open("01-log.txt", "a")
      f.write(f'{function.__name__}: Код выполнялся {et-bt} секунд(ы)\n')
      f.close()
      return result
    return wrapper

@measure_running_time
def api_call():
  time.sleep(1)  
  print("API call")

api_call()

#2 декоратор, который будет выводить на экран результат выполненияфункции

def print_result(function):
    def wrapper(*args, **kwargs):
      result = function(*args, **kwargs)
      print(result)
      return result
    return wrapper

@print_result
def api_call():
  return "API called successfully!"

api_call()

#3 декоратор, который будет выводить на экран аргументы функции и ихтипы

def print_args(function):
    def wrapper(*args, **kwargs):
      result = function(*args, **kwargs)
      for a in args:
        print(a, type(a))            
      for k,v in kwargs.items():
        print(v, type(v))
      return result
    return wrapper

@print_args
def api_call(a, b, c, flag):
  return True

api_call(1, "a", 0.1, flag=True)

#4 декоратор, который будет выводить на экран имя функции и модуль, гдеона определена

def print_function_name(function):
    def wrapper(*args, **kwargs):
      result = function(*args, **kwargs)
      print(function.__name__, function.__module__)
      return result
    return wrapper

@print_function_name
def api_call():
  return True

api_call()

#5 декоратор, который будет выводить на экран количество вызовов функ-ции за определенный период времени.

import functools
import time

def num_calls_per_period(period_sec):
  calls = []
  def decorator(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
      nonlocal calls
      now = time.time()
      calls.insert(0, now)
      result = function(*args, **kwargs)
      num_calls = 0
      for c in calls:
        if now - c > period_sec:
          break
        num_calls += 1
      print(f"Function called {num_calls} times during last {period_sec} seconds")
      return result
    return wrapper
  return decorator

@num_calls_per_period(period_sec=5)
def api_call():
  time.sleep(1)
  return 1

for i in range(10):
  api_call()

#7 декоратор, который будет кэшировать результаты выполнения функциии очищать кэш при превышении заданного размера

import functools
import math

def use_cache(max_entries):
    cache_dict = {}
    def decorator(function):
      @functools.wraps(function)
      def wrapper(*args, **kwargs):
        nonlocal cache_dict
        if len(args) != 1 or len(kwargs) !=0:
          raise ArgumentError("wrong number of arguments! only functions with 1 argument are supported!")
        arg = args[0]
        if arg in cache_dict:
          print("cache hit!")
          return cache_dict[arg]
        else:
          print("cache miss!")
          result = function(arg)
          if len(cache_dict) > max_entries:
            print("cache emptied!")
            cache_dict = {}
          cache_dict[arg] = result
          return result
      return wrapper
    return decorator

@use_cache(max_entries=5)
def calc_exp(x):
  return math.exp(x)

print(calc_exp(100))
print(calc_exp(100))

print('first run')
for i in range(6):
  calc_exp(i)
print('second run')
for i in range(6):
  calc_exp(i)

#8 декоратор, который будет логировать ошибки, возникающие при выпол-нении функции, и отправлять уведомления об этих ошибках

import functools
import smtplib

def exception_handler(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
      try:
        result = function(*args, **kwargs)
        return result
      except Exception as e:
        print("ОШИБКА!", repr(e))
        f = open("08-log.txt", "a")
        f.write(f"ОШИБКА! {repr(e)}\n")
        f.close()
        try:
          # ниже должен быть указан настоящий IP адрес почтового сервера
          # и настоящий e-mail адрес получателя
          s = smtplib.SMTP('localhost')
          s.sendmail('robot@nowhere.nn', ['admin@nowhere.nn'], repr(e))
          s.quit()
        except:
          print("Не удалось отправить уведомление об ошибке на e-mail адрес администратора!")
        return None
    return wrapper

@exception_handler
def div2(a, b):
  return a / b

print(div2(10,2))
print(div2(10,0))

#9 декоратор, который будет проверять аргументы функции на корректностьи выбрасывать исключение при обнаружении некорректных данных

import functools

def validate_arguments(check_function):
  def decorator(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
      for a in args:
        if not check_function(a):
          raise ValueError('function argument check failed!')
      for k,v in kwargs.items():
        if not check_function(v):
          raise ValueError('function argument check failed!')
      result = function(*args, **kwargs)
      return result
    return wrapper
  return decorator

@validate_arguments(lambda x: x > 0)
def calculate_cube_volume(x):
  return x**3

print(calculate_cube_volume(3))
print(calculate_cube_volume(-3))

#10 декоратор, который будет проверять возвращаемое значение функции накорректность и заменять его на предопределенное значение при обнаружении не-корректных данных

import functools

def validate_return_value(check_function):
  def decorator(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
      result = function(*args, **kwargs)
      if not check_function(result):
        return 0
      return result
    return wrapper
  return decorator

@validate_return_value(lambda x: x > 0)
def calculate_cube_volume(x):
  return x**3

print(calculate_cube_volume(3))
print(calculate_cube_volume(-3))

#11 декоратор, который будет заменять исключения, возникающие при вы-полнении функции, на заданное значение и логировать эти замены

import functools
import smtplib

def exception_handler(exception_retvalue):
  def decorator(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
      try:
        result = function(*args, **kwargs)
        return result
      except Exception as e:
        print("ОШИБКА!", repr(e))
        f = open("11-log.txt", "a")
        f.write(f"ОШИБКА! {repr(e)}\n")
        f.close()
        return exception_retvalue
    return wrapper
  return decorator

@exception_handler(exception_retvalue = 0)
def div2(a, b):
  return a / b

print(div2(10,2))
print(div2(10,0))

#13 декоратор, который будет ограничивать количество вызовов функцииза определенный период времени

import functools
import time

def limit_calls_per_period(max_calls, period_sec):
  calls = []
  def decorator(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
      nonlocal calls
      now = time.time()
      calls.insert(0, now)
      num_calls = 0
      for c in calls:
        if now - c > period_sec:
          break
        num_calls += 1
      print(f"Function called {num_calls} times during last {period_sec} seconds")
      if (num_calls <= max_calls):
        print("Calling the function...")
        result = function(*args, **kwargs)
        return result
      else:
        print("Function call limit reached!")
        return None
    return wrapper
  return decorator

@limit_calls_per_period(max_calls = 5, period_sec=1)
def api_call():
  return 1

for i in range(10):
  api_call()

#14 декоратор, который будет принимать аргументы и передавать их в функ-цию в ОБРАТНОМ порядке

def reverse_args(function):
    def wrapper(*args):
      aa = []
      for a in args:
        aa.insert(0, a)
      result = function(*aa)
      return result
    return wrapper

@reverse_args
def api_call(a, b, c):
  print(a, b, c)

api_call(1, 2, 3)

#15 декоратор, который будет принимать аргументы и передавать их в функ-цию в качестве ключевых параметров с заданными значениями по умолчанию

def kvargs_default(default_value):
  def decorator(function):
    def wrapper(*args):
      a = default_value
      b = default_value
      c = default_value
      if len(args) > 0:
        a = args[0]
      if len(args) > 1:
        b = args[1]
      if len(args) > 2:
        c = args[2]
      result = function(a=a, b=b, c=c)
      return result
    return wrapper
  return decorator

@kvargs_default(-1)
def api_call(a, b, c):
  print(a, b, c)

api_call(4, 2)

#16 декоратор, который будет принимать аргументы и передавать их в функ-цию в качестве позиционных параметров с заданными значениями по умолчанию

from inspect import signature

def args_default(default_value):
  def decorator(function):
    def wrapper(*args):
      sig = signature(function)
      num_args = len(sig.parameters)
      aa = [default_value]*num_args
      for i in range(num_args):
        if i < len(args):
          aa[i] = args[i]
      result = function(*aa)
      return result
    return wrapper
  return decorator

@args_default(-1)
def api_call(a, b, c):
  print(a, b, c)

api_call(4, 2)

#22 декоратор, который будет принимать список аргументов и передавать егов функцию в ОБРАТНОМ порядке

from inspect import signature

def args_list_reverse(function):
    def wrapper(*args):
      aa = list(args[0])
      aa.reverse()
      result = function(*aa)
      return result
    return wrapper

@args_list_reverse
def api_call(a, b, c):
  print(a, b, c)

api_call([3, 2, 1])

#23 декоратор, который будет принимать словарь аргументов и передаватьего в функцию с заданными значениями по умолчанию.

from inspect import signature

def args_dict(function):
    def wrapper(*args):
      result = function(**args[0])
      return result
    return wrapper

@args_dict
def api_call(a, b, c):
  print(a, b, c)

api_call({'a':3, 'b':2, 'c':1})

#25 декоратор, который будет заменять значение аргумента на заданное зна-чение только если оно удовлетворяет определенному условию

import functools

def fix_arguments(check_function, fix_value):
  def decorator(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
      aa = []
      for a in args:
        if not check_function(a):
          aa.append(fix_value)
        else:
          aa.append(a)
      kv = {}
      for k, v in kwargs.items():
        if not check_function(v):
          kv[k] = fix_value
        else:
          kv[k] = v
      result = function(*aa, **kv)
      return result
    return wrapper
  return decorator

@fix_arguments(lambda x: x > 0, 1)
def calculate_cube_volume(x):
  return x**3

print(calculate_cube_volume(3))
print(calculate_cube_volume(-3))
"""

def exdec():
  return """

#1-2 перехватывает исключения и выдаёт своё сообщение об ошибке

import functools

def exception_handler(def_response="An error occurred!"):
  def decorator(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
      try:
        result = function(*args, **kwargs)
        return result
      except:
        print(def_response)
        return None
    return wrapper
  return decorator

@exception_handler(def_response="Division failed!")
def div2(a, b):
  return a / b

@exception_handler()
def sum2(a, b):
  return a + b

print(div2(10,2))
print(div2(10,0))

print(sum2(2, 2))
print(sum2(2, "a"))

#2-2 выдаёт исключение, если возвращаемое значение не проходит проверку

import functools

def validate_arguments(check_function):
  def decorator(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
      result = function(*args, **kwargs)
      if not check_function(result):
        raise ValueError('function return value check failed!')
      return result
    return wrapper
  return decorator

@validate_arguments(lambda x: x > 0)
def calculate_cube_volume(x):
  return x**3

print(calculate_cube_volume(3))
print(calculate_cube_volume(-3))

#8-2 задерживает выполнение функции на заданное время

import functools
import time

def delay_execution(delay):
  def decorator(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
      time.sleep(delay)
      result = function(*args, **kwargs)
      return result
    return wrapper
  return decorator

@delay_execution(delay=10)
def api_call():
  print("API call delayed...")

api_call()

#21-2 ограничивает кол-во вызовов функции

import functools

def limit_calls(max_calls):
  calls = 0
  def decorator(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
      nonlocal calls
      calls += 1
      if calls <= max_calls:
        result = function(*args, **kwargs)
        return result
      return None
    return wrapper
  return decorator

@limit_calls(max_calls=6)
def api_call():
  print("API call executed succesfully...")

for i in range(10):
  api_call()

#24-2 - преобразует тип возвращаемого значения функции

import functools

def convert_to_data_type(dt_func):
  def decorator(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
      result = function(*args, **kwargs)
      return dt_func(result)
    return wrapper
  return decorator

@convert_to_data_type(str)
def concatenate_strings(x, y):
  return x + y

@convert_to_data_type(int)
def sum2(x, y):
  return x + y

a = concatenate_strings("1","2")
print(a, type(a))
b = sum2("1","2")
print(b, type(b))

#15-2 - новый - вызывает декорированную функцию несколько раз, пока не получит возвращаемое значение не None

import functools
import random

def retry_on_failure(max_retries=3):
  def decorator(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
      for i in range(max_retries):
        result = function(*args, **kwargs)
        if result is not None:
          return result
      return None
    return wrapper
  return decorator

@retry_on_failure()
def api_call():
  print("API call")
  return None if random.randint(0, 1)==0 else 1

api_call()
"""

def exlist():
  return """
#1-3 стэк

class Stack():
  def __init__(self):
    self.stack = []

  def print(self):
    print(self.stack)

  def push(self, item):
    self.stack.append(item)

  def pop(self):
    return self.stack.pop()

s = Stack()
s.push(1)
s.push(2)
s.push(3)
s.print()
a = s.pop()
print(a)
s.print()

#2-3 двусвязный список (заказы в инетмагазине)

from datetime import date

class Item:
  def __init__(self, name, quantity, cost):
    self.name = name
    self.quantity = quantity
    self.cost = cost
  def print(self):
    print(self.name, self.quantity, self.cost)

class Order:
  def __init__(self, number, date, items):
    self.number = number
    self.date = date
    self.items = items
    self.next = None
    self.prev = None
  def print(self):
    print(self.number, self.date)
    for item in self.items:
      item.print()
    print()

class Orders:
  def __init__(self):
    self.head = None
    self.tail = None

  def append(self, order):
    if self.head is None:
      self.head = order
    order.prev = self.tail
    if self.tail is not None:
      self.tail.next = order
    self.tail = order

orders = Orders()
orders.append(Order(1, date.today(), [Item("Болты", 10, 20), Item("Гайки", 10, 30)]))
orders.append(Order(2, date.today(), [Item("Саморезы", 20, 40)]))
orders.append(Order(3, date.today(), [Item("Шайбы", 20, 30), Item("Втулки", 10, 50), Item("Скобы", 15, 35)]))

order = orders.head
while order is not None:
  order.print()
  order = order.next

#25-3 односвязный список
class Item:
  def __init__(self, value):
    self.value = value
    self.next = None

class LinkedList:
  def __init__(self):
    self.head = None

  def append(self, value):
    if self.head is None:
      self.head = Item(value)
    else:
      item = self.head
      while item.next is not None:
        item = item.next
      item.next = Item(value)

  def delete_last(self):
    if self.head is None:
      return
    elif self.head.next is None:
      self.head = None
    else:
      prev = None
      item = self.head
      while item.next is not None:
        prev = item
        item = item.next
      prev.next = None

  def print(self):
    item = self.head
    while item is not None:
      print(item.value)
      item = item.next

l = LinkedList()
l.append(1)
l.append(2)
l.append(3)
l.append(4)
l.print()
print("\n")
l.delete_last()
l.delete_last()
l.print()
"""

def exsort():
  return """
#8-3 сортировка фильмов по годам по возрастанию и по убыванию быстрой сортировкой

def quick_sort(arr, compare_function):
  quick_sort_helper(arr, 0, len(arr) - 1, compare_function)
  return arr

def quick_sort_helper(arr, first, last, compare_function):
  if first < last:
    split_point = partition(arr, first, last, compare_function)
    quick_sort_helper(arr, first, split_point - 1, compare_function)
    quick_sort_helper(arr, split_point + 1, last, compare_function)

def partition(arr, first, last, compare_function):
  pivot_value = arr[first]
  left_mark = first + 1
  right_mark = last
  done = False
  
  while not done:
    while left_mark <= right_mark and compare_function(arr[left_mark], pivot_value) <= 0:
      left_mark += 1
    while compare_function(arr[right_mark], pivot_value) >= 0 and right_mark >= left_mark:
      right_mark -= 1

    if right_mark < left_mark:
      done = True
    else:
      arr[left_mark], arr[right_mark] = arr[right_mark], arr[left_mark]

  arr[first], arr[right_mark] = arr[right_mark], arr[first]

  return right_mark

def compare_movies_by_year(a, b):
  an, ay = a
  bn, by = b
  return ay - by

def compare_movies_by_year_descending(a, b):
  an, ay = a
  bn, by = b
  return by - ay

List = [("Inception", 2010), ("The Matrix", 1999), ('Pulp Fiction', 1994),
("The Godfather", 1972), ("The Dark Knight", 2008),("Forrest Gump", 1994), 
("Fight Club", 1999), ('Interstellar', 2014), ('The Shawshank Redemption', 1994),
('Gladiator', 2000), ('Avatar', 2009), ('Titanic', 1997), 
('The Lord of the Rings', 2001), ('Star Wars', 1977), ('Jurassic Park', 1993)]

print(f'Sorted list ascending: {quick_sort(List, compare_movies_by_year)}\n')
print(f'Sorted list descending: {quick_sort(List, compare_movies_by_year_descending)}\n')

#23-3 сортировка строк по возрастанию и убыванию длины быстрой сортировкой с измерением времени выполнения

import time

def measure_running_time(function):
    def wrapper(*args, **kwargs):
      bt = time.time()
      result = function(*args, **kwargs)
      et = time.time()
      print(f'Код выполнялся {et-bt} секунд(ы)')
      return result
    return wrapper

@measure_running_time
def selection_sort(arr, compare_function):
  n = len(arr)
  for i in range(n):
    min_idx = i
    for j in range(i + 1, n):
      if compare_function(arr[j], arr[min_idx]) < 0:
        min_idx = j
    arr[i], arr[min_idx] = arr[min_idx], arr[i]
  return arr

@measure_running_time
def quick_sort(arr, compare_function):
  quick_sort_helper(arr, 0, len(arr) - 1, compare_function)
  return arr

def quick_sort_helper(arr, first, last, compare_function):
  if first < last:
    split_point = partition(arr, first, last, compare_function)
    quick_sort_helper(arr, first, split_point - 1, compare_function)
    quick_sort_helper(arr, split_point + 1, last, compare_function)

def partition(arr, first, last, compare_function):
  pivot_value = arr[first]
  left_mark = first + 1
  right_mark = last
  done = False
  
  while not done:
    while left_mark <= right_mark and compare_function(arr[left_mark], pivot_value) <= 0:
      left_mark += 1
    while compare_function(arr[right_mark], pivot_value) >= 0 and right_mark >= left_mark:
      right_mark -= 1

    if right_mark < left_mark:
      done = True
    else:
      arr[left_mark], arr[right_mark] = arr[right_mark], arr[left_mark]

  arr[first], arr[right_mark] = arr[right_mark], arr[first]

  return right_mark

def compare_strings_by_len(a, b):
  return len(a) - len(b)

def compare_strings_by_len_descending(a, b):
  return len(b) - len(a)

List = ["Inception", "The Matrix", 'Pulp Fiction', "The Godfather", "The Dark Knight", 
"Forrest Gump", "Fight Club", 'Interstellar', 'The Shawshank Redemption',
'Gladiator', 'Avatar', 'Titanic', 'The Lord of the Rings', 'Star Wars', 'Jurassic Park']

print(f'Quicksorted list ascending: {quick_sort(List, compare_strings_by_len)}\n')
print(f'Quicksorted list descending: {quick_sort(List, compare_strings_by_len_descending)}\n')

print(f'Selectionsorted list ascending: {selection_sort(List, compare_strings_by_len)}\n')
print(f'Selectionsorted list descending: {selection_sort(List, compare_strings_by_len_descending)}\n')

List *= 100
print("Quick sort")
quick_sort(List, compare_strings_by_len)
print("Selection sort")
selection_sort(List, compare_strings_by_len)

#24-3 бинарный поиск

import random

def binary_search(arr, x):
  low = 0
  high = len(a) - 1
  while low <= high:
    mid = (low + high) // 2
    if arr[mid] == x:
      return mid
    elif arr[mid] < x:
      low = mid + 1
    else:
      high = mid - 1
  return -1

a = []
for i in range(10):
    a.append(random.randint(1, 50))
a.sort()
print(a)

v = random.choice(a)
print(v)

print(binary_search(a, v))

#1-3 - новый - сортировка вставками товаров по продажам

import time

def measure_running_time(function):
    def wrapper(*args, **kwargs):
      bt = time.time()
      result = function(*args, **kwargs)
      et = time.time()
      print(f'Код выполнялся {et-bt} секунд(ы)')
      return result
    return wrapper

@measure_running_time
def insertion_sort(arr, compare_function):
    for i in range(1, len(arr)):
        val = arr[i]
        j = i - 1
        while j >= 0 and compare_function(arr[j], val) > 0:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = val
    return arr

def compare_goods_by_sales(a, b):
  a1, a2 = a
  b1, b2 = b
  return a2 - b2

def compare_goods_by_sales_descending(a, b):
  a1, a2 = a
  b1, b2 = b
  return b2 - a2

List = [('Товар1', 53), ('Товар2', 72), ('Товар3', 30), ('Товар4', 85), ('Товар5', 47)]

print(f'Insertion sorted list ascending: {insertion_sort(List, compare_goods_by_sales)}\n')
print(f'Insertion sorted list descending: {insertion_sort(List, compare_goods_by_sales_descending)}\n')

#13-3 - новый - сортировка пузырьком и шейкерная чисел по сумме цифр

import time
import random

def measure_running_time(function):
    def wrapper(*args, **kwargs):
      bt = time.time()
      result = function(*args, **kwargs)
      et = time.time()
      print(f'Код выполнялся {et-bt} секунд(ы)')
      return result
    return wrapper

@measure_running_time
def bubble_sort(arr, compare_function):
  n = len(arr)
  for i in range(n):
    for j in range(0, n-i-1):
      if compare_function(arr[j], arr[j+1]) > 0:
        arr[j], arr[j+1] = arr[j+1], arr[j]
  return arr

@measure_running_time
def cocktail_sort(arr, compare_function):
  n = len(arr)
  start = 0
  end = n - 1
  swapped = True
  while swapped:
    swapped = False
    for i in range(start, end):
      if (compare_function(arr[i], arr[i + 1]) > 0):
        arr[i], arr[i + 1] = arr[i + 1], arr[i]
        swapped = True
    if not swapped:
      break
    swapped = False
    end = end - 1
    for i in range(end - 1, start - 1, -1):
      if (compare_function(arr[i], arr[i + 1]) > 0):
        arr[i], arr[i + 1] = arr[i + 1], arr[i]
        swapped = True
    start = start + 1
  return arr

def sum_digits(number):
  return sum(int(digit) for digit in str(number))

def compare_numbers_by_sum_of_digits(a, b):
  return sum_digits(a) - sum_digits(b)

def compare_numbers_by_sum_of_digits_descending(a, b):
  return sum_digits(b) - sum_digits(a)

List = []
for i in range(100):
    List.append(random.randint(1, 12))


print(f'Bubble sorted list ascending: {bubble_sort(List, compare_numbers_by_sum_of_digits)}\n')
print(f'Bubble sorted list descending: {bubble_sort(List, compare_numbers_by_sum_of_digits_descending)}\n')

print(f'Cocktail sorted list ascending: {cocktail_sort(List, compare_numbers_by_sum_of_digits)}\n')
print(f'Cocktail sorted list descending: {cocktail_sort(List, compare_numbers_by_sum_of_digits_descending)}\n')

#5-3 - новый - сортировка чисел выбором по сумме цифр

import time

def selection_sort(arr, compare_function):
  n = len(arr)
  for i in range(n):
    min_idx = i
    for j in range(i + 1, n):
      if compare_function(arr[j], arr[min_idx]) < 0:
        min_idx = j
    arr[i], arr[min_idx] = arr[min_idx], arr[i]
  return arr

def sum_digits(number):
  return sum(int(digit) for digit in str(number))

def compare_numbers_by_sum_of_digits(a, b):
  return sum_digits(a) - sum_digits(b)

List = [12,45,67,23,89,12,77,54,31,90,68,35,101,211,13,17]

print(f'Selection sorted list: {selection_sort(List, compare_numbers_by_sum_of_digits)}\n')

#15-3 - новый - сортировка чисел выбором по сумме цифр. СПИСОК НЕ ДАН!!!

import random

def selection_sort(arr, compare_function):
  n = len(arr)
  for i in range(n):
    min_idx = i
    for j in range(i + 1, n):
      if compare_function(arr[j], arr[min_idx]) < 0:
        min_idx = j
    arr[i], arr[min_idx] = arr[min_idx], arr[i]
  return arr

def sum_digits(number):
  return sum(int(digit) for digit in str(number))

def compare_numbers_by_sum_of_digits(a, b):
  return sum_digits(a) - sum_digits(b)

List = []
for i in range(100):
    List.append(random.randint(1, 12))

print(f'Selection sorted list: {selection_sort(List, compare_numbers_by_sum_of_digits)}\n')
"""

def exclass():
  return """

#19-3 студенты с оценками

class Student:
  def __init__(self, firstname, lastname, age, marks):
    self.firstname = firstname
    self.lastname = lastname
    self.age = age
    self.marks = marks
  def __len__(self):
    return len(self.marks)
  def add_mark(self, mark):
    self.marks.append(mark)
  def mean_mark(self):
    if len(self):
      return sum(self.marks) / len(self)
    else:
      return 0
  def print(self):
    print(f'Студент {self.firstname} {self.lastname}, возраст - {self.age}, cр.балл - {self.mean_mark()}')

a = Student('Ivan', 'Ivanov', 18, [5,4,4,4])
a.print()
a.add_mark(5)
a.print()

#21-3 автомобили со скоростью

class Car:
  def __init__(self, brand, model, year, speed):
    self.brand = brand
    self.model = model
    self.year = year
    self.speed = speed
  def speed_up(self, speed_increment):
    self.speed += speed_increment
  def speed_down(self, speed_decrement):
    self.speed -= speed_decrement
  def __eq__(self, other):
    return self.speed == other.speed
  def print(self):
    print(f'Автомобиль {self.brand} {self.model}, год выпуска - {self.year}, скорость - {self.speed}')

a = Car('Ford', 'Focus', 2008, 90)
a.print()
a.speed_up(10)
a.print()
a.speed_down(10)
a.print()
b = Car('Lada', 'Vesta', 2022, 90)
b.print()
if a == b:
  print('У двух автомобилей скорость одинакова')
else:
  print('У двух автомобилей скорость разная')

#23-2 геометрические фигуры с вычислением площади

import math

class Shape:
  def area(self):
    raise NotImplementedError("Method not implemented")

class Rectangle(Shape):
  def __init__(self, a, b):
    self.a = a
    self.b = b
  def area(self):
    return self.a*self.b

class Circle(Shape):
  def __init__(self, r):
    self.r = r
  def area(self):
    return math.pi*self.r**2

objects = [Rectangle(2,2), Circle(1)]
for o in objects:
  print(o.area())

#12-3 - новый - персоны с определением возраста

from datetime import datetime
from dateutil.relativedelta import relativedelta

class Person:
  def __init__(self, name, country, birthdate):
    self.name = name
    self.country = country
    self.birthdate = birthdate
  def get_age(self):
    delta = relativedelta(datetime.utcnow(), self.birthdate)
    return delta.years
  def print(self):
    print(f'Имя - {self.name}; страна - {self.country}, дата рождения - {self.birthdate}, возраст - {self.get_age()}')

a = Person('Иван Иванов', 'Russia', datetime(1981, 12, 2))
b = Person('Jean Dubois', 'France', datetime(1958, 6, 15))
a.print()
b.print()
"""

def sort():
  return """
import time

def measure_time(func):
  def wrapper(*args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    print(f"Время выполнения функции {func.__name__}: {end - start:.6f} ceк.\n")
    return result
  return wrapper

#сортировка выбором

students = {3.25 : 'Ivanov', 4.2 : 'Petrov', 2.1 : 'Sidorov', 5.0 : 'Losev'}

@measure_time
def selection_sort(a_dict):
  lst = list(a_dict.keys())
  for i in range(len(lst) - 1):
    pos_of_min = i
    for j in range(i + 1, len(lst)):
      if lst[j] < lst[pos_of_min]:
        pos_of_min = j
    lst[pos_of_min], lst[i] = lst[i], lst[pos_of_min]

  new_dict = dict()
  for i in range(len(lst)):
    new_dict[lst[i]] = a_dict[lst[i]]
  return new_dict

print(selection_sort(students))

#быстрая сортировка

students = {3.25 : 'Ivanov', 4.2 : 'Petrov', 2.1 : 'Sidorov', 5.0 : 'Losev'}

@measure_time
def sort_quick(ss):
  arr = list(ss.keys())
  l = quick_sort(arr)
  d = dict()
  for i in range(len(l)):
    d[l[i]] = ss[l[i]]
  return d

def quick_sort(arr):
  quick_sort_helper(arr, 0, len(arr) - 1)
  return arr

def quick_sort_helper(arr, first, last):
  if first < last:
    split_point = partition(arr, first, last)
    quick_sort_helper(arr, first, split_point - 1)
    quick_sort_helper(arr, split_point + 1, last)

def partition(arr, first, last):
  pivot_value = arr[first]
  left_mark = first + 1
  right_mark = last
  done = False

  while not done:
    while left_mark <= right_mark and arr[left_mark] <= pivot_value:
      left_mark += 1
    while arr[right_mark] >= pivot_value and right_mark >= left_mark:
      right_mark -= 1
    if right_mark < left_mark:
      done = True
    else:
      arr[left_mark], arr[right_mark] = arr[right_mark], arr[left_mark]

  arr[first], arr[right_mark] = arr[right_mark], arr[first]

  return right_mark

sort_quick(students)

#сортировка Шелла

students = {3.25 : 'Ivanov', 4.2 : 'Petrov', 2.1 : 'Sidorov', 5.0 : 'Losev'}

@measure_time
def sort_shell(ss):
   arr = list(ss.keys())
   l = shell_sort(arr)
   d = dict()
   for i in range(len(l)):
       d[l[i]] = ss[l[i]]
   return d

def shell_sort(arr):
  gap = len(arr) // 2
  while gap > 0:
    for i in range(gap, len(arr)):
      temp = arr[i]
      j = i
      while j >= gap and arr[j - gap] > temp:
        arr[j] = arr[j - gap]
        j -= gap
      arr[j] = temp
    gap //= 2
  return arr

arr = [64, 34, 25, 12, 22, 11, 90]
print(sort_shell(students))

#сортировка слиянием

students = {3.25 : 'Ivanov', 4.2 : 'Petrov', 2.1 : 'Sidorov', 5.0 : 'Losev'}

@measure_time
def sort_sliyanie(ss):
  arr = list(ss.keys())
  l = merge_sort(arr)
  d = dict()
  for i in range(len(l)):
    d[l[i]] = ss[l[i]]
  return d

def merge_sort(arr):
  if len(arr) <= 1:
    return arr
  mid = len(arr) // 2
  left_half = arr[:mid]
  right_half = arr[mid:]
  left_half = merge_sort(left_half)
  right_half = merge_sort(right_half)
  return merge(left_half, right_half)

def merge(left_half, right_half):
  result = []
  i = 0
  j = 0
  while i < len(left_half) and j < len(right_half):
    if left_half[i] <= right_half[j]:
      result.append(left_half[i])
      i += 1
    else:
      result.append(right_half[j])
      j += 1
  result += left_half[i:]
  result += right_half[j:]
  return result

print(sort_sliyanie(students))

#2

class Book():
  def __init__(self, author, name, year):
    self.author = author
    self.name = name
    self.year = year

  def __info__(self):
        return f"Book(author='{self.author}', title='{self.name}', year={self.year})"

books = [
    Book("George Orwell", "1984", 1949),
    Book("Fyodor Dostoevsky", "Crime and Punishment", 1866),
    Book("Leo Tolstoy", "War and Peace", 1869),
    Book("Mark Twain", "Adventures of Huckleberry Finn", 1885),
    Book("Gabriel Garcia Marquez", "One Hundred Years of Solitude", 1967),
    Book('Steven King', 'It', 1986),
    Book('Alexander Pushkin', 'Evgeniy Onegin', 1830),
    Book('Fyodor Dostoevski', 'The Brothers Karamazov', 1880),
    Book('Natalia Makuni', 'Ikarus', 2013)
]

#пузырьковая сортировка

@measure_time
def bubble_sort(arr, key):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if key(arr[j]) > key(arr[j+1]):
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# реализация алгоритма шейкерной сортировки
def cocktail_sort(arr):
  n = len(arr)
  start = 0
  end = n - 1
  swapped = True
  while swapped:
    swapped = False
    for i in range(start, end):
      if (arr[i] > arr[i + 1]):
        arr[i], arr[i + 1] = arr[i + 1], arr[i]
        swapped = True
    if not swapped:
      break
    swapped = False
    end = end - 1
    for i in range(end - 1, start - 1, -1):
      if (arr[i] > arr[i + 1]):
        arr[i], arr[i + 1] = arr[i + 1], arr[i]
        swapped = True
    start = start + 1
  return arr

# реализация алгоритма сортировки расчёской
def comb_sort(arr):
  n = len(arr)
  gap = n
  shrink = 1.3
  swapped = True
  while swapped:
    gap = int(gap/shrink)
    if gap < 1:
      gap = 1
    i = 6
    swapped = False
    while i + gap < n:
      if arr[i] > arr[i + gap]:
        arr[i], arr[i + gap] = arr[i + gap], arr[i]
        swapped = True
      l += 1
  return arr

#сортировка вставками

@measure_time
def insertion_sort(arr, key):
    for i in range(1, len(arr)):
        current_book = arr[i]
        j = i - 1
        while j >= 0 and key(arr[j]) > key(current_book):
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = current_book
    return arr

#быстрая сортировка

@measure_time
def quick_sort(arr, key):
  quick_sort_helper(arr, 0, len(arr) - 1, key)
  return arr

def quick_sort_helper(arr, first, last, key):
  if first < last:
    split_point = partition(arr, first, last, key)
    quick_sort_helper(arr, first, split_point - 1, key)
    quick_sort_helper(arr, split_point + 1, last, key)

def partition(arr, first, last, key):
  pivot_value = key(arr[first])
  left_mark = first + 1
  right_mark = last
  done = False

  while not done:
    while left_mark <= right_mark and key(arr[left_mark]) <= pivot_value:
      left_mark += 1
    while key(arr[right_mark]) >= pivot_value and right_mark >= left_mark:
      right_mark -= 1
    if right_mark < left_mark:
      done = True
    else:
      arr[left_mark], arr[right_mark] = arr[right_mark], arr[left_mark]

  arr[first], arr[right_mark] = arr[right_mark], arr[first]

  return right_mark

#сортировка Шелла

@measure_time
def shell_sort(arr, key):
  gap = len(arr) // 2
  while gap > 0:
    for i in range(gap, len(arr)):
      temp = arr[i]
      j = i
      while j >= gap and key(arr[j - gap]) > key(temp):
        arr[j] = arr[j - gap]
        j -= gap
      arr[j] = temp
    gap //= 2
  return arr

#сортировка слиянием

@measure_time
def sort_merge(arr, key):
  return merge_sort(arr, key)

def merge_sort(arr, key):
  if len(arr) <= 1:
    return arr
  mid = len(arr) // 2
  left_half = arr[:mid]
  right_half = arr[mid:]
  left_half = merge_sort(left_half, key)
  right_half = merge_sort(right_half, key)
  return merge(left_half, right_half, key)

def merge(left_half, right_half, key):
  result = []
  i = 0
  j = 0
  while i < len(left_half) and j < len(right_half):
    if key(left_half[i]) <= key(right_half[j]):
      result.append(left_half[i])
      i += 1
    else:
      result.append(right_half[j])
      j += 1
  result += left_half[i:]
  result += right_half[j:]
  return result

sort_criteria = input("Введите критерий сортировки (author, name, year): ")

if sort_criteria == "author":
    sorted_books_bubble = bubble_sort(books.copy(), key=lambda x: x.author)
    print(sorted_books_bubble)
    sorted_books_insertion = insertion_sort(books.copy(), key=lambda x: x.author)
    print(sorted_books_insertion)
    sorted_books_quick = quick_sort(books.copy(), key=lambda x: x.author)
    print(sorted_books_quick)
    sorted_books_shell = shell_sort(books.copy(), key=lambda x: x.author)
    print(sorted_books_shell)
    sorted_books_merge = sort_merge(books.copy(), key=lambda x: x.author)
    print(sorted_books_merge)
elif sort_criteria == "name":
    sorted_books_bubble = bubble_sort(books.copy(), key=lambda x: x.name)
    print(sorted_books_bubble)
    sorted_books_insertion = insertion_sort(books.copy(), key=lambda x: x.name)
    print(sorted_books_insertion)
    sorted_books_quick = quick_sort(books.copy(), key=lambda x: x.name)
    print(sorted_books_quick)
    sorted_books_shell = shell_sort(books.copy(), key=lambda x: x.name)
    print(sorted_books_shell)
    sorted_books_merge = sort_merge(books.copy(), key=lambda x: x.name)
    print(sorted_books_merge)
elif sort_criteria == "year":
    sorted_books_bubble = bubble_sort(books.copy(), key=lambda x: x.year)
    print(sorted_books_bubble)
    sorted_books_insertion = insertion_sort(books.copy(), key=lambda x: x.year)
    print(sorted_books_insertion)
    sorted_books_quick = quick_sort(books.copy(), key=lambda x: x.year)
    print(sorted_books_quick)
    sorted_books_shell = shell_sort(books.copy(), key=lambda x: x.year)
    print(sorted_books_shell)
    sorted_books_merge = sort_merge(books.copy(), key=lambda x: x.year)
    print(sorted_books_merge)
else:
    print("Некорректный критерий сортировки. Пожалуйста, выберите из 'author', 'name', 'year'.")

#3

#сортировка пузырьком

strings = ['banana', 'apple', 'kiwi', 'orange', 'grape', 'pear', 'plum', 'cherry', 'apricot', 'lemon']

@measure_time
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

bubble_sort(strings)

#сортировка слиянием

strings = ['banana', 'apple', 'kiwi', 'orange', 'grape', 'pear', 'plum', 'cherry', 'apricot', 'lemon']

@measure_time
def sort_merge(arr):
  return merge_sort(arr)

def merge_sort(arr):
  if len(arr) <= 1:
    return arr
  mid = len(arr) // 2
  left_half = arr[:mid]
  right_half = arr[mid:]
  left_half = merge_sort(left_half)
  right_half = merge_sort(right_half)
  return merge(left_half, right_half)

def merge(left_half, right_half):
  result = []
  i = 0
  j = 0
  while i < len(left_half) and j < len(right_half):
    if left_half[i] <= right_half[j]:
      result.append(left_half[i])
      i += 1
    else:
      result.append(right_half[j])
      j += 1
  result += left_half[i:]
  result += right_half[j:]
  return result

print(sort_merge(strings))

#быстрая сортировка

strings = ['banana', 'apple', 'kiwi', 'orange', 'grape', 'pear', 'plum', 'cherry', 'apricot', 'lemon']

@measure_time
def quick_sort(arr):
  quick_sort_helper(arr, 0, len(arr) - 1)
  return arr

def quick_sort_helper(arr, first, last):
  if first < last:
    split_point = partition(arr, first, last)
    quick_sort_helper(arr, first, split_point - 1)
    quick_sort_helper(arr, split_point + 1, last)

def partition(arr, first, last):
  pivot_value = arr[first]
  left_mark = first + 1
  right_mark = last
  done = False

  while not done:
    while left_mark <= right_mark and arr[left_mark] <= pivot_value:
      left_mark += 1
    while arr[right_mark] >= pivot_value and right_mark >= left_mark:
      right_mark -= 1
    if right_mark < left_mark:
      done = True
    else:
      arr[left_mark], arr[right_mark] = arr[right_mark], arr[left_mark]

  arr[first], arr[right_mark] = arr[right_mark], arr[first]

  return right_mark

quick_sort(strings)

#сортировка Шелла

@measure_time
def shell_sort(arr):
  gap = len(arr) // 2
  while gap > 0:
    for i in range(gap, len(arr)):
      temp = arr[i]
      j = i
      while j >= gap and arr[j - gap] > temp:
        arr[j] = arr[j - gap]
        j -= gap
      arr[j] = temp
    gap //= 2
  return arr

strings = ['banana', 'apple', 'kiwi', 'orange', 'grape', 'pear', 'plum', 'cherry', 'apricot', 'lemon']
shell_sort(strings)

#сортировка слиянием

@measure_time
def sort_merge(arr):
  return merge_sort(arr)

def merge_sort(arr):
  if len(arr) <= 1:
    return arr
  mid = len(arr) // 2
  left_half = arr[:mid]
  right_half = arr[mid:]
  left_half = merge_sort(left_half)
  right_half = merge_sort(right_half)
  return merge(left_half, right_half)

def merge(left_half, right_half):
  result = []
  i = 0
  j = 0
  while i < len(left_half) and j < len(right_half):
    if left_half[i] <= right_half[j]:
      result.append(left_half[i])
      i += 1
    else:
      result.append(right_half[j])
      j += 1
  result += left_half[i:]
  result += right_half[j:]
  return result

strings = ['banana', 'apple', 'kiwi', 'orange', 'grape', 'pear', 'plum', 'cherry', 'apricot', 'lemon']
sort_merge(strings)
"""

def list():
  return """

#1.1 сбалансированные скобки deque

from collections import deque

class Stack(deque):
  def push(self, a):
    self.append(a)

def is_balanced(expression):
  stack = Stack()
  opening_brackets = ['(', '{', '[']
  closing_brackets = [')', '}', ']']
  for char in expression:
    if char in opening_brackets:
      stack.push(char)
    elif char in closing_brackets:
      if len(stack)==0:
        return False
      top = stack.pop()
      if opening_brackets.index(top) != closing_brackets.index(char):
        return False
  return len(stack) == 0

def check_balance(expression):
  print('Скобки сбалансированы' if is_balanced(expression) else 'Скобки не сбалансированы')

expression1 = input('Введите математическое выражение: ')
check_balance(expression1)

expression2 = input('Введите математическое выражение: ')
check_balance(expression2)

#1.2 сбалансированные скобки без deque

class Stack():
  def __init__(self, l):
    self.__stack = []
    self.__maxlen = l
  def push(self, e):
    if len(self.__stack)<self.__maxlen:
      self.__stack.append(e)
    else:
      raise ValueError("Stack is full")
  def pop(self):
    return self.__stack.pop()
  def top(self):
    return self.__stack[-1]
  def is_empty(self):
    if len(self.__stack)==0:
      return True
    return False
  def __len__(self):
    return len(self.__stack)
  def __str__(self):
    return str(self.__stack)
    
def is_balanced(expression):
  stack = Stack(100)
  opening_brackets = ['(', '{', '[']
  closing_brackets = [')', '}', ']']
  for char in expression:
    if char in opening_brackets:
      stack.push(char)
    elif char in closing_brackets:
      if len(stack)==0:
        return False
      top = stack.pop()
      if opening_brackets.index(top) != closing_brackets.index(char):
        return False
  return len(stack) == 0

def check_balance(expression):
  print('Скобки сбалансированы' if is_balanced(expression) else 'Скобки не сбалансированы')

expression1 = input('Введите математическое выражение: ')
check_balance(expression1)

expression2 = input('Введите математическое выражение: ')
check_balance(expression2)

#2.1 стэк

class Stack():
  def __init__(self, l):
    self.__stack = []
    self.__maxlen = l
  def push(self, e):
    if len(self.__stack)<self.__maxlen:
      self.__stack.append(e)
    else:
      raise ValueError("Stack is full")
  def pop(self):
    return self.__stack.pop()
  def top(self):
    return self.__stack[-1]
  def is_empty(self):
    if len(self.__stack)==0:
      return True
    return False
  def __len__(self):
    return len(self.__stack)
  def __str__(self):
    return str(self.__stack)
    
s=Stack(2)
s.push(5)
s.push(5)
print(s)

s.push(5)

s.pop()
s.pop()
print(str(s))
print(len(s))
s.is_empty()

s.top()

#2.2 стэк на array

import array

class Stack:
    def __init__(self, l):
        self.__stack = array.array('i')
        self.__maxlen = l
    def push(self, e):
        if len(self.__stack) < self.__maxlen:
            self.__stack.append(e)
        else:
            raise ValueError("Stack is full")
    def pop(self):
        return self.__stack.pop()
    def top(self):
        return self.__stack[-1]
    def is_empty(self):
        return len(self.__stack) == 0
    def length(self):
        return len(self.__stack)
    def __str__(self):
        return str(list(self.__stack))

stack = Stack(5)
stack.push(1)
stack.push(2)
stack.push(3)

print(stack.length())
print(stack.top())
print(stack)
stack.push(4)
stack.push(5)
print(stack)
stack.pop()
print(stack)

#3) Реализовать класс однонаправленного связанного списка.

class ListItem:
  def __init__ (self,elem):
    self.elem = elem
    self.nextitem = None

class LinkedList:
  def __init__(self):
    self.head = None

class ListItem:
  def __init__ (self,elem):
    self.elem = elem
    self.nextitem = None

class LinkedList:
  def __init__(self):
    self.head = None
  def AddToBegin(self, newelem):
    newitem = ListItem(newelem)
    newitem.nextitem = self.head
    self.head = newitem
  def __str__(self):
    l = []
    item = self.head
    if item is None:
      return ''
    l.append(item.elem)
    while (item.nextitem):
      item = item.nextitem
      l.append(item.elem)
    return str(l)

l = LinkedList()
l.AddToBegin(1)
l.AddToBegin(2)
l.AddToBegin(3)
print(l)

#4) На базе класса однонаправленного связанного списка реализовать двунаправленный связанный список.

class ListItem:
  def __init__ (self,elem):
    self.elem = elem
    self.nextitem = None
    self.previtem = None

class LinkedList:
  def __init__(self):
    self.head = None
    
#4.1) Реализовать метод добавления элемента в начало списка.

class ListItem:
  def __init__ (self,elem):
    self.elem = elem
    self.nextitem = None
    self.previtem = None

class LinkedList:
  def __init__(self):
    self.head = None
  def AddToBegin(self, newelem):
    newitem = ListItem(newelem)
    newitem.nextitem = self.head
    if self.head is not None:
      self.head.previtem = newitem
    self.head = newitem
  def __str__(self):
    l = []
    item = self.head
    if item is None:
      return ''
    l.append(item.elem)
    while (item.nextitem):
      item = item.nextitem
      l.append(item.elem)
    return str(l)
  def PrintReversed(self):
    i = self.head
    if i is None:
      return
    while (i.nextitem):
      i = i.nextitem
    while (i.previtem):
      print(i.elem)
      i = i.previtem
    print(i.elem)

l = LinkedList()
l.AddToBegin(1)
l.AddToBegin(2)
l.AddToBegin(3)
l.PrintReversed()

#5) При помощи класса связанного списка реализовать очередь.

class ListItem:
  def __init__ (self,elem):
    self.elem = elem
    self.nextitem = None
    self.previtem = None

class LinkedList:
  def __init__(self):
    self.head = None
    self.tail = None
  def AddToBegin(self, newelem):
    newitem = ListItem(newelem)
    newitem.nextitem = self.head
    if self.head is not None:
      self.head.previtem = newitem
    else:
      self.tail = newitem
    self.head = newitem
  def GetFromEnd(self):
    i = self.tail
    if i is None:
      return None
    if i.previtem:
      i.previtem.nextitem = None
      self.tail = i.previtem
    return i.elem
  def __str__(self):
    l = []
    item = self.head
    if item is None:
      return ''
    l.append(item.elem)
    while (item.nextitem):
      item = item.nextitem
      l.append(item.elem)
    return str(l)

l = LinkedList()
l.AddToBegin(1)
l.AddToBegin(2)
l.AddToBegin(3)
print(l)
a = l.GetFromEnd()
print(a)
print(l)

#5.2

class ListItem:
  def __init__ (self,elem):
    self.elem = elem
    self.nextitem = None
    self.previtem = None

class LinkedList:
  def __init__(self):
    self.head = None
    self.tail = None
  def AddToEnd(self, newelem):
    newitem = ListItem(newelem)
    if self.head == None:
      self.head = newitem
      self.tail = newitem
    else:
      self.tail.nextitem = newitem
      self.tail=newitem
  def GetFromBegin(self):
    i = self.head
    if i is None:
      return None
    if i.nextitem:
      i.nextitem.previtem = None
      self.head = i.nextitem
    return i.elem
  def __str__(self):
    l = []
    item = self.head
    if item is None:
      return ''
    l.append(item.elem)
    while (item.nextitem):
      item = item.nextitem
      l.append(item.elem)
    return str(l)

l = LinkedList()
l.AddToEnd(1)
l.AddToEnd(2)
l.AddToEnd(3)
print(l)
a = l.GetFromBegin()
print(a)
print(l)

#6) Реализовать генератор, который возвращает значение поочередно извлекаемое из конца двух очередей (в качестве очереди используется deque из collections). Если очередь из которой извлекается элемент пуста - генератор заканчивает работу.

from collections import deque

def alternatequeuevalue(queue1, queue2):
    while queue1 and queue2:
        if queue1:
            yield queue1.pop()
        if queue2:
            yield queue2.pop()

queue1 = deque([1, 2, 3, 4, 5, 0])
queue2 = deque([6, 7, 8, 9, 10])

gen = alternatequeuevalue(queue1, queue2)

for value in gen:
    print(value)

#1- Реализовать функцию, которая находит сумму всех элементов двусвязного списка, надо решать задачу двумя способами 1) сложность метода О(1), 2) сложность О(n).

class node:
    def __init__(self, data=None, linkn=None, linkp = None):
        self.data = data
        self.linkn = linkn
        self.linkp = linkp

class linklist2:
    def __init__(self):
        self.head = None
        self.tail = None
        self.__summ=0

    def addnode(self, data):
        newnode = node(data)
        if not self.head:
          self.head = newnode
          self.tail = newnode
        else:
          self.tail.linkn = newnode
          newnode.linkp = self.tail
          self.tail = newnode
        self.__summ+= data

    def addfirst(self, data):
        newnode = node(data)
        if not self.head:
          self.head = newnode
          self.tail = newnode
        else:
          newnode.linkn = self.head
          self.head.linkp = newnode
          self.head = newnode
        self.__summ+= data

    def printback(self):
        s = self.tail
        strr=""
        while s:
          strr+= str(s.data) + "<-"
          s = s.linkp
        return strr

    def printforward(self):
        s = self.head
        strr=""
        while s:
            strr+= str(s.data) + "->"
            s = s.linkn
        return strr

    def __len__(self):
        count = 0
        s = self.head
        while s:
          count += 1
          s = s.linkn
        return count

    def summ (self):
        "O(n)"
        summ = 0
        s = self.head
        while s:
          summ +=s.data
          s = s.linkn
        return summ

    def summo1 (self):
        "O(1)"
        return self.__summ

l = linklist2()
l.addnode(1)
l.addnode(2)
l.addnode(3)
print(l.summ())
l.summo1()

#2- реализовать функцию, которая удаляет все элементы с заданным значением из двусвязного списка.

class node:
    def __init__(self, data=None, linkn=None, linkp = None):
        self.data = data
        self.linkn = linkn
        self.linkp = linkp

class linklist2:
    def __init__(self):
        self.head = None
        self.tail = None
        self.__summ=0

    def addnode(self, data):
        newnode = node(data)
        if not self.head:
          self.head = newnode
          self.tail = newnode
        else:
          self.tail.linkn = newnode
          newnode.linkp = self.tail
          self.tail = newnode
        self.__summ+= data

    def printforward(self):
        s = self.head
        strr=""
        while s:
            strr+= str(s.data) + "->"
            s = s.linkn
        return strr

    def delfixed(self, number):
      s = self.head
      while s:
        if s.data == number:
          if s == self.head:
            #if s.linkn == None:
              #return None
            s.linkn.linkp = None
            self.head = s.linkn
          elif s != self.tail:
            s.linkn.linkp = s.linkp
            s.linkp.linkn = s.linkn
          elif s == self.tail:
            s.linkp.linkn = None
            s.linkp = None
        s = s.linkn

l = linklist2()
l.addnode(1)
l.addnode(2)
l.addnode(3)
l.addnode(2)
l.addnode(2)
l.addnode(1)
l.addnode(1)
print(l.printforward())
l.delfixed(1)
print(l.printforward())

#3- Реализовать функцию, которая удаляет все повторяющиеся элементы из двусвязного списка

class node:
    def __init__(self, data=None, linkn=None, linkp = None):
        self.data = data
        self.linkn = linkn
        self.linkp = linkp

class linklist2:
    def __init__(self):
        self.head = None
        self.tail = None
        self.__dict=dict()

    def addnode(self, data):
        newnode = node(data)
        if not self.head:
          self.head = newnode
          self.tail = newnode
        else:
          self.tail.linkn = newnode
          newnode.linkp = self.tail
          self.tail = newnode

    def printforward(self):
        s = self.head
        strr=""
        while s:
            strr+= str(s.data) + "->"
            s = s.linkn
        return strr

    def delpovtor(self):
      s = self.head
      while s:
        if s.data not in self.__dict:
          self.__dict[s.data] = 1
        else:
          if s == self.tail:
            s.linkp.linkn = None
          else:
            s.linkn.linkp = s.linkp
            s.linkp.linkn = s.linkn
        s = s.linkn

l = linklist2()
l.addnode(1)
l.addnode(2)
l.addnode(3)
l.addnode(2)
l.addnode(4)
l.addnode(1)
print(l.printforward())
l.delpovtor()
print(l.printforward())

#4- Реализовать функцию, которая разделяет двусвязный список на два списка, один из которых содержит все элементы, меньшие заданного значения, а другой — все элементы, большие или равные заданному значению.

class node:
    def __init__(self, data=None, linkn=None, linkp = None):
        self.data = data
        self.linkn = linkn
        self.linkp = linkp

class linklist2:
    def __init__(self):
        self.head = None
        self.tail = None
        self.__dict=dict()

    def addnode(self, data):
        newnode = node(data)
        if not self.head:
          self.head = newnode
          self.tail = newnode
        else:
          self.tail.linkn = newnode
          newnode.linkp = self.tail
          self.tail = newnode

    def printforward(self):
        s = self.head
        strr=""
        while s:
            strr+= str(s.data) + "->"
            s = s.linkn
        return strr

    def splitlist(self, number):
      minlist = linklist2()
      maxlist = linklist2()
      s = self.head
      while s:
        if s.data < number:
          minlist.addnode(s.data)
        else:
          maxlist.addnode(s.data)
        s = s.linkn
      return (minlist.printforward(), maxlist.printforward())

l = linklist2()
l.addnode(1)
l.addnode(2)
l.addnode(3)
l.addnode(3)
l.addnode(0)
l.addnode(5)
print(l.printforward())
l.splitlist(3)

# стэк на основе двусвязного списка

class node:
  def __init__(self, data=None, next=None, prev=None):
    self.data = data
    self.next = next
    self.prev = prev

class Stack:
  def __init__(self):
    self.head = None
    self.tail = None
  def addnodetoend(self, data):
    newnode = node(data)
    if not self.head:
      self.head = newnode
      self.tail = newnode
    else:
      self.tail.next = newnode
      self.tail = newnode
  def popnodefromend(self):
    if not self.tail:
      return None
    else:
      data = self.tail.data
      self.tail = self.tail.prev
    return data
  def __str__(self):
    l = []
    item = self.head
    if item is None:
      return ''
    l.append(item.data)
    while (item.next):
      item = item.next
      l.append(item.data)
    return str(l)

s = Stack()
s.addnodetoend(1)
s.addnodetoend(2)
s.addnodetoend(3)
print(s)
k = s.popnodefromend()
print(k)
print(s)
"""

def numpy():
  return """
#1. Сгенерировать двухмерный массив `arr` размерности (4, 7), состоящий из случайных действительных чисел, равномерно распределенных в диапазоне от 0 до 20. 
#Нормализовать значения массива с помощью преобразования вида ax+b так, что после нормализации максимальный элемент масcива будет равен 1.0, минимальный 0.0

import numpy as np
arr = np.random.uniform(0, 20, (4, 7))
arr_norm = (arr - arr.min())/ (arr.max() - arr.min())
print(arr)
print(arr_norm)

#2. Создать матрицу 8 на 10 из случайных целых (используя модуль `numpy.random`) чисел из диапозона от 0 до 10 и найти в ней строку (ее индекс и вывести саму строку), в которой сумма значений минимальна.

import numpy as np
m = np.random.randint(0, 11, (8, 10))
print(m)
mins = 10*10
mini = 10

for i in range(len(m)):
  s = 0
  for j in range(len(m[i])):
    s+=m[i][j]
  if s<mins:
    mins=s
    mini=i

print()
print(m[mini])

#3. Найти евклидово расстояние между двумя одномерными векторами одинаковой размерности.

import numpy as np
v1 = np.array((2, 0, 4))
v2 = np.array((2, 4, 4))

#способ1
square = np.square(v1 - v2)
sum_square = np.sum(square)
distance = np.sqrt(sum_square)
print(distance)

#способ2
distance = np.linalg.norm(v1-v2)
print(distance)

#4. Решить матричное уравнение A*X*B=-C - найти матрицу X. Где A = [[-1, 2, 4], [-3, 1, 2], [-3, 0, 1]], B=[[3, -1], [2, 1]], C=[[7, 21], [11, 8], [8, 4]].

import numpy as np
#A*X*B=-C
#X=-A^(-1)*C*B^(-1)
A = np.matrix([[-1, 2, 4], [-3, 1, 2], [-3, 0, 1]])
B = np.matrix([[3, -1], [2, 1]])
C = np.matrix([[7, 21], [11, 8], [8, 4]])
oA = np.linalg.inv(A)
oB = np.linalg.inv(B)
X = -1*oA.dot(C).dot(oB)
X1 = -1*oA*C*oB
print(X)
print(X1)

#Лабораторная работа 1

#Замечание: при решении данных задач не подразумевается использования циклов или генераторов Python, если в задании не сказано обратного. Решение должно опираться на использования функционала библиотеки numpy.

#1. Файл minutes_n_ingredients.csv содержит информацию об идентификаторе рецепта, времени его выполнения в минутах и количестве необходимых ингредиентов. Считайте данные из этого файла в виде массива numpy типа int32, используя np.loadtxt. Выведите на экран первые 5 строк массива.

import numpy as np

data = np.loadtxt('data/minutes_n_ingredients.csv', dtype=np.int32, delimiter=',', skiprows=1)
print(data[:5])

#2. Вычислите среднее значение, минимум, максимум и медиану по каждому из столбцов, кроме первого.

import numpy as np

data = np.loadtxt('data/minutes_n_ingredients.csv', dtype=np.int32, delimiter=',', skiprows=1)
print(data[:5])

#3. Ограничьте сверху значения продолжительности выполнения рецепта значением квантиля q0.75.

# Вычисляем квантиль 0.75
q75 = np.quantile(data[:, 1], 0.75)

# Ограничиваем значения сверху
data[:, 1] = np.clip(data[:, 1], a_min=None, a_max=q75)

print("Первые 5 строк массива после ограничения:")
print(data[:5])

#4. Посчитайте, для скольких рецептов указана продолжительность, равная нулю. Замените для таких строк значение в данном столбце на 1.

# Подсчитываем количество рецептов с продолжительностью выполнения равной нулю
num_zeros = np.count_nonzero(data[:, 1] == 0)

# Заменяем значения времени выполнения рецепта на 1 для рецептов с продолжительностью равной нулю
data[data[:, 1] == 0, 1] = 1

print("Количество рецептов с продолжительностью выполнения равной нулю:", num_zeros)
print("Первые 5 строк массива после замены:")
print(data[:5])

#5. Посчитайте, сколько уникальных рецептов находится в датасете.

# Подсчитываем количество уникальных рецептов
num_recipes = len(np.unique(data[:, 0]))

print("Количество уникальных рецептов:", num_recipes)

#6. Сколько и каких различных значений кол-ва ингредиентов присутвует в рецептах из датасета?

# Находим уникальные значения количества ингредиентов
unique_ingredient_counts = np.unique(data[:, 2])

# Подсчитываем количество уникальных значений
num_unique_ingredient_counts = len(unique_ingredient_counts)

print("Количество уникальных значений количества ингредиентов:", num_unique_ingredient_counts)
print("Уникальные значения количества ингредиентов:", unique_ingredient_counts)

#7. Создайте версию массива, содержащую информацию только о рецептах, состоящих не более чем из 5 ингредиентов.

# Выбираем только те строки, где количество ингредиентов не превышает 5
filtered_data = data[data[:, 2] <= 5]

print("Первые 5 строк отфильтрованного массива:")
print(filtered_data[:5])

#8. Для каждого рецепта посчитайте, сколько в среднем ингредиентов приходится на одну минуту рецепта. Найдите максимальное значение этой величины для всего датасета

# Создаем массив, содержащий отношение количества ингредиентов к продолжительности выполнения рецепта
ingredient_ratio = data[:, 2] / data[:, 1]

# Находим максимальное значение этого массива
max_ingredient_ratio = np.max(ingredient_ratio)

print("Максимальное значение количества ингредиентов на одну минуту в рецептах:", max_ingredient_ratio)

#9. Вычислите среднее количество ингредиентов для топ-100 рецептов с наибольшей продолжительностью

# Получаем индексы строк в порядке убывания значений времени выполнения рецепта
sorted_indices = np.argsort(data[:, 1])[::-1]

# Выбираем только топ-100 индексов
top_indices = sorted_indices[:100]

# Выбираем только топ-100 рецептов
top_recipes = data[top_indices]

# Вычисляем среднее количество ингредиентов в топ-100 рецептах
mean_ingredients = np.mean(top_recipes[:, 2])

print("Среднее количество ингредиентов для топ-100 рецептов с наибольшей продолжительностью:", mean_ingredients)

#10. Выберите случайным образом и выведите информацию о 10 различных рецептах

rng = np.random.default_rng()
d = rng.choice(data, 10, False)
print(d)

#11. Выведите процент рецептов, кол-во ингредиентов в которых меньше среднего.

# Вычисляем среднее значение количества ингредиентов в массиве
mean_ingredients = np.mean(data[:, 2])

# Вычисляем количество рецептов, кол-во ингредиентов в которых меньше среднего
less_than_mean = np.count_nonzero(data[:, 2] < mean_ingredients)

# Вычисляем процент таких рецептов от общего количества рецептов
percent_less_than_mean = less_than_mean / data.shape[0] * 100

print("Процент рецептов, кол-во ингредиентов в которых меньше среднего:", percent_less_than_mean, "%")

#12. Назовем "простым" такой рецепт, длительность выполнения которого не больше 20 минут и кол-во ингредиентов в котором не больше 5. Создайте версию датасета с дополнительным столбцом, значениями которого являются 1, если рецепт простой, и 0 в противном случае.

# Создаем булевы массивы, отражающие условия "длительность выполнения не больше 20 минут"
# и "количество ингредиентов не больше 5"
short_time = data[:, 1] <= 20
few_ingredients = data[:, 2] <= 5

# Объединяем булевы массивы с помощью оператора логического "И"
simple_recipe = short_time & few_ingredients

# Создаем новый столбец с помощью функции np.where()
data_with_simple_flag = np.insert(data, 3, np.where(simple_recipe, 1, 0), axis=1)

# Выводим первые 5 строк нового массива
print(data_with_simple_flag[:5])

#13. Выведите процент "простых" рецептов в датасете

# Создаем булевы массивы, отражающие условия "длительность выполнения не больше 20 минут"
# и "количество ингредиентов не больше 5"
short_time = data[:, 1] <= 20
few_ingredients = data[:, 2] <= 5

# Объединяем булевы массивы с помощью оператора логического "И"
simple_recipe = short_time & few_ingredients

# Создаем новый столбец с помощью функции np.where()
data_with_simple_flag = np.insert(data, 3, np.where(simple_recipe, 1, 0), axis=1)

# Вычисляем количество "простых" рецептов в массиве
simple_recipe_count = np.count_nonzero(data_with_simple_flag[:, 3] == 1)

# Вычисляем процент "простых" рецептов от общего количества рецептов
percent_simple_recipe = simple_recipe_count / data.shape[0] * 100

print("Процент 'простых' рецептов в датасете:", percent_simple_recipe, "%")

#14. Разделим рецепты на группы по следующему правилу. Назовем рецепты короткими, если их продолжительность составляет менее 10 минут; стандартными, если их продолжительность составляет более 10, но менее 20 минут; и длинными, если их продолжительность составляет не менее 20 минут. Создайте трехмерный массив, где нулевая ось отвечает за номер группы (короткий, стандартный или длинный рецепт), первая ось - за сам рецепт и вторая ось - за характеристики рецепта. Выберите максимальное количество рецептов из каждой группы таким образом, чтобы было возможно сформировать трехмерный массив. Выведите форму полученного массива.

# Создаем булевые массивы для каждой группы рецептов
short_time = data[:, 1] < 10
standard_time = (data[:, 1] >= 10) & (data[:, 1] < 20)
long_time = data[:, 1] >= 20

# Выбираем максимальное количество рецептов из каждой группы
max_short_time = np.count_nonzero(short_time)
max_standard_time = np.count_nonzero(standard_time)
max_long_time = np.count_nonzero(long_time)

# Создаем трехмерный массив
result_array = np.zeros((3, max(max_short_time, max_standard_time, max_long_time), data.shape[1]), dtype=np.int32)

# Добавляем рецепты в массив в соответствии с группами
result_array[0, :max_short_time, :] = data[short_time]
result_array[1, :max_standard_time, :] = data[standard_time]
result_array[2, :max_long_time, :] = data[long_time]

# Выводим форму полученного массива
print(result_array.shape)

#14. Еслли нужно, наоборот, получить массив, где одна из размерностей соответствует наименьшему кол-ву рецептов в группе, то делать так:
m = data
group1 = m[m[:, 1] < 10]
group2 = m[(m[:, 1] >= 10) * (m[:, 1] < 20)]
group3 = m[m[:, 1] >= 20]
max_size = min(len(group1), len(group2), len(group3))
group1c = group1[:max_size]
group2c = group2[:max_size]
group3c = group3[:max_size]
d3 = np.array([group1c, group2c, group3c])
print(d3.shape)
"""

def pandas():
  return """
#1.1 В файлах recipes_sample.csv и reviews_sample.csv находится информация об рецептах блюд и отзывах на эти рецепты 
#соответственно. Загрузите данные из файлов в виде pd.DataFrame с названиями recipes и reviews. Обратите внимание на 
#корректное считывание столбца с индексами в таблице reviews (безымянный столбец).
#2.1 Преобразуйте столбец submitted из таблицы recipes в формат времени. Модифицируйте решение задачи 1.1 так, чтобы считать столбец сразу в нужном формате.

import pandas as pd
import numpy as np
recipes = pd.read_csv('recipes_sample.csv', parse_dates=['submitted'])
reviews = pd.read_csv('reviews_sample.csv', index_col=[0])
recipes[:3]


#1.2 Для каждой из таблиц выведите основные параметры:

 #   количество точек данных (строк);
 #   количество столбцов;
 #   тип данных каждого столбца.

print('Количество строк для первой таблицы =',len(recipes.axes[0]),
      '\nКоличество столбцов для первой таблицы =', len(recipes.axes[1]))
for i in range(0,len(recipes.axes[1])):
    print('Тип данных для',i+1, 'столбца:',type(recipes.iloc[0, i]))

print('Количество строк для второй таблицы =',len(reviews.axes[0]),
      '\nКоличество столбцов для второй таблицы =', len(reviews.axes[1]))
for i in range(0,len(reviews.axes[1])):
    print('Тип данных для',i+1, 'столбца:',type(reviews.iloc[0,i]))


#1.3 Исследуйте, в каких столбцах таблиц содержатся пропуски. Посчитайте долю строк, содержащих пропуски, в отношении к общему количеству строк.

null_rows_total1 = recipes.shape[0] - recipes.dropna().shape[0]    
print('Количество пропусков в каждом столбце первой таблицы:\n', recipes.isna().sum())
print('Доля строк, содержащих пропуски: ', (null_rows_total1/len(recipes.axes[0]))*100,'%',sep='' )

null_rows_total2 = reviews.shape[0] - reviews.dropna().shape[0]
print('Количество пропусков в каждом столбце второй таблицы:\n', reviews.isna().sum())
print('Доля строк, содержащих пропуски: ', (null_rows_total2/len(reviews.axes[0]))*100,'%',sep='' )


#1.4 Рассчитайте среднее значение для каждого из числовых столбцов (где это имеет смысл).

print('Среднее значение для столбца minutes: ', recipes['minutes'].mean(), 
      '\nСреднее значение для столбца n_steps: ', recipes['n_steps'].mean(), 
      '\nСреднее значение для столбца n_ingredients: ', recipes['n_ingredients'].mean())

print('Среднее значение для столбца rating: ', reviews['rating'].mean())


#1.5 Создайте серию из 10 случайных названий рецептов.

ten_recipes = pd.Series(recipes['name'].sample(n = 10))
ten_recipes


#1.6 Измените индекс в таблице reviews, пронумеровав строки, начиная с нуля.

reviews.reset_index()


#1.7 Выведите информацию о рецептах, время выполнения которых не больше 20 минут и кол-во ингредиентов в которых не больше 5.

recipes[(recipes.minutes < 21) & (recipes.n_ingredients < 6)]

#2.1 Преобразуйте столбец submitted из таблицы recipes в формат времени. Модифицируйте решение задачи 1.1 так, чтобы считать столбец сразу в нужном формате.

import pandas as pd
import numpy as np
recipes = pd.read_csv('recipes_sample.csv', parse_dates=['submitted'])
reviews = pd.read_csv('reviews_sample.csv', index_col=[0])
print(recipes[:5]['submitted'])

#2.2 Выведите информацию о рецептах, добавленных в датасет не позже 2010 года.

recipes[recipes['submitted']>='2010-01-01']


#3.1 Добавьте в таблицу recipes столбец description_length, в котором хранится длина описания рецепта из столбца description.

recipes['description_length']  = recipes['description'].str.len()


#3.2 Измените название каждого рецепта в таблице recipes таким образом, чтобы каждое слово в названии начиналось с прописной буквы.

recipes['name'] = recipes['name'].str.capitalize()


#3.3 Добавьте в таблицу recipes столбец name_word_count, в котором хранится количество слов из названии рецепта (считайте, что слова в названии 
#разделяются только пробелами). Обратите внимание, что между словами может располагаться несколько пробелов подряд.

recipes['name_word_count'] = [len(x.split()) for x in recipes['name'].tolist()]


#4.1 Посчитайте количество рецептов, представленных каждым из участников (contributor_id). Какой участник добавил максимальное кол-во рецептов?

c = recipes.groupby("contributor_id").size()
print('Количество рецептов, представленных каждым из участников', c, 
      '\nУчастник, который добавил наибольшее кол-во рецептов: ', 
      c[c == c.max()].index[0])


#4.2 Посчитайте средний рейтинг к каждому из рецептов. Для скольких рецептов отсутствуют отзывы? Обратите внимание, что отзыв с нулевым рейтингом или не 
#с нулевым рейтингом или не заполненным текстовым описанием не считается отсутствующим.
print('Кол-во рецептов, для которых отсутствуют отзывы', 
      len(recipes.groupby('name').size()) - len(reviews.groupby('recipe_id').size()))
reviews.groupby('recipe_id').mean('rating').drop('user_id', axis=1)


#4.3 Посчитайте количество рецептов с разбивкой по годам создания.

recipes.groupby(recipes.submitted.dt.year).size()


#5.1 При помощи объединения таблиц, создайте DataFrame, состоящий из четырех столбцов: id, name, user_id, rating. Рецепты, на 
#которые не оставлен ни один отзыв, должны отсутствовать в полученной таблице. Подтвердите правильность работы вашего кода, 
#выбрав рецепт, не имеющий отзывов, и попытавшись найти строку, соответствующую этому рецепту, в полученном DataFrame.

import pandas as pd
import numpy as np
recipes = pd.read_csv('recipes_sample.csv', parse_dates=['submitted'])
reviews = pd.read_csv('reviews_sample.csv', index_col=[0])

df = recipes[['id','name']].copy()
dfm = df.merge(reviews[['user_id','rating', 'recipe_id']], left_on='id', right_on='recipe_id')
dfm = dfm.drop('recipe_id', axis=1)

print(dfm[:5])

dfa = df.merge(reviews[['user_id','rating', 'recipe_id']], left_on='id', right_on='recipe_id', how='left').drop('recipe_id', axis=1)

recipes_without_reviews = dfa[dfa['user_id'].isna()]
print(recipes_without_reviews[:5])
id_of_recipe_without_reviews = recipes_without_reviews.iloc[0, 0]
print(id_of_recipe_without_reviews)

print(dfm[dfm['id'] == id_of_recipe_without_reviews])

#5.2 При помощи объединения таблиц и группировок, создайте DataFrame, состоящий из трех столбцов: recipe_id, name, 
#review_count, где столбец review_count содержит кол-во отзывов, оставленных на рецепт recipe_id. У рецептов, на которые не 
#оставлен ни один отзыв, в столбце review_count должен быть указан 0. Подтвердите правильность работы вашего кода, выбрав 
#рецепт, не имеющий отзывов, и найдя строку, соответствующую этому рецепту, в полученном DataFrame.

import pandas as pd
import numpy as np
recipes = pd.read_csv('recipes_sample.csv', parse_dates=['submitted'])
reviews = pd.read_csv('reviews_sample.csv', index_col=[0])

df = recipes[['id','name']].copy()
c = reviews.groupby('recipe_id').size().reset_index(name='review_count')
dfm = df.merge(c, left_on='id', right_on='recipe_id', how='left')
dfm = dfm.drop('recipe_id', axis=1)
dfm = dfm.rename(columns={"id": "recipe_id"})
dfm = dfm.fillna(0)

print(dfm[:5])

print(dfm[dfm['review_count'] < 1])

#5.3. Выясните, рецепты, добавленные в каком году, имеют наименьший средний рейтинг?

df = recipes[['id','name']].copy()
df = df.merge(reviews[['recipe_id', 'rating', 'date']], right_on='recipe_id', left_on='id')
df = df.drop(['id', 'name', 'recipe_id'], axis=1)
df.date = pd.DatetimeIndex(df.date).to_period("Y")
df.groupby('date').mean().sort_values('rating')


#6.1 Отсортируйте таблицу в порядке убывания величины столбца name_word_count и сохраните результаты выполнения заданий 3.1-3.3 в csv файл. 

recipes = recipes.sort_values(by=['name_word_count'], ascending=False)
recipes.to_csv("my_data.csv", index=True)


#6.2 Воспользовавшись pd.ExcelWriter, cохраните результаты 5.1 и 5.2 в файл: на лист с названием Рецепты с оценками сохраните 
#результаты выполнения 5.1; на лист с названием Количество отзывов по рецептам сохраните результаты выполнения 5.2.

with pd.ExcelWriter("res.xlsx") as writer:
    df5_1.to_excel(writer, sheet_name="Рецепты с оценками")  
    df5_2.to_excel(writer, sheet_name="Количество отзывов по рецептам")
"""

def json():
  return """
#Задачи для совместного разбора

#1. Вывести все адреса электронной почты, содержащиеся в адресной книге addres-book.json

import json

with open("./data/addres-book.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for i, j in enumerate(data):
    print(data[i]["email"])

#2. Вывести телефоны, содержащиеся в адресной книге addres-book.json

for i in range(len(data)):
    # for _, j in enumerate(i):
    # print(i)
    for j in data[i]["phones"]:
        print(j["phone"])

#3. По данным из файла addres-book-q.xml сформировать список словарей с телефонами каждого из людей.

from bs4 import BeautifulSoup

with open("./data/addres-book-q.xml", "r", encoding="utf8") as f:
    data = BeautifulSoup(f)

l = []
for adr in data.find_all("address"):
    for name in adr.find_all("name"):
        na = name.getText()
    ph_l = []
    for phone in adr.find_all("phone"):
        
        ph_l.append(phone.text)

    l.append({na:ph_l})
        
print(l)

#Лабораторная работа №4

import json
import pickle

with open("./data/addres-book.json", "r", encoding="utf-8") as f:
    data = json.load(f)

#1.1 Считайте файл contributors_sample.json. Воспользовавшись модулем json, преобразуйте содержимое файла в соответствующие объекты python. Выведите на экран информацию о первых 3 пользователях.

class User:

    def __init__(self, username, name, sex, address, mail, jobs, id):
        self.username = username
        self.name = name
        self.sex = sex
        self.address = address
        self.mail = mail
        self.jobs = jobs
        self.id = id

    def __str__(self) -> str:
        jobs_str = ", ".join(self.jobs)
        return f"\nId: {self.id}\nUsername: {self.username}\nName: {self.name}\nSex: {self.sex}\naddress: {self.address}\nmail: {self.mail}\njobs: {jobs_str}\n\n#########################"


with open("./data/contributors_sample.json", "r", encoding="utf8") as f:
    data = json.load(f)

user_l = []
for i in data:
    user_l.append(User(**i))

for usr in user_l[:3]:
    print(usr)

#1.2 Выведите уникальные почтовые домены, содержащиеся в почтовых адресах людей

# l = []
# for i in data:
#     dom = i["mail"].split("@")[1]
#     if dom not in l:
#         l.append(i["mail"].split("@")[1])

# print(l)

list(set([(usr.mail.split("@")[1]) for usr in user_l]))

#1.3 Напишите функцию, которая по username ищет человека и выводит информацию о нем. Если пользователь с заданным username отсутствует, возбудите исключение ValueError


def find_by_username(usr_name):
    c = 0
    for i in data:
        if usr_name == i["username"]:
            print(i["username"])
            c += 1
    if c == 0:
        print("user not found")

find_by_username("uheber")

#1.4 Посчитайте, сколько мужчин и женщин присутсвует в этом наборе данных.

def male_female():
    m, f = 0, 0
    for i in data:
        if i["sex"] == "M":
            m += 1
        else:
            f += 1
    return f"мужчин: {m}, женщин: {f}"

male_female()

#1.5 Создайте pd.DataFrame contributors, имеющий столбцы id, username и sex.

import pandas as pd
    
contributors = pd.read_json("./data/contributors_sample.json").drop(["name", "address", "mail", "jobs"], axis=1)
col = contributors.pop("id")
contributors.insert(0, col.name, col)
print(contributors)

#1.6 Загрузите данные из файла recipes_sample.csv (ЛР2) в таблицу recipes. Объедините recipes с таблицей contributors с сохранением строк в том случае, если информация о человеке отсутствует в JSON-файле. Для скольких человек информация отсутствует?

recipes = pd.read_csv("./data/recipes_sample.csv", sep=",")
recipes = recipes.merge(contributors, left_on="contributor_id", right_on="id", how="left")
recipes = recipes[pd.isna(recipes["id_y"])] # если информация отсутствует
print(len(recipes["contributor_id"].unique()))

#2.1 На основе файла contributors_sample.json создайте словарь следующего вида:
#{
#    должность: [список username людей, занимавших эту должность]
#}

with open("./data/contributors_sample.json", "r", encoding="utf8") as f:
    data = json.load(f)

d = {}
for i in data:
    for job in i["jobs"]:
        if job not in d:
            d[job] = []
        d[job].append(i["username"])

print({k: d[k] for k in list(d)[:3]})

#2.2 Сохраните результаты в файл job_people.pickle и в файл job_people.json с использованием форматов pickle и JSON соответственно. Сравните объемы получившихся файлов. При сохранении в JSON укажите аргумент indent.

with open("./data/job_people.pickle", "wb") as f:
    pickle.dump(d, f)

with open("./data/job_people.json", "w") as f:
    json.dump(d, f, indent=1)

import os
print("pickle :", os.path.getsize("./data/job_people.pickle"))
print("json   :", os.path.getsize("./data/job_people.json"))

#2.3 Считайте файл job_people.pickle и продемонстрируйте, что данные считались корректно.

with open("./data/job_people.pickle", "rb") as f:
    d_pickle = pickle.load(f)

print({k: d_pickle[k] for k in list(d_pickle)[:3]})

#3.1 По данным файла steps_sample.xml сформируйте словарь с шагами по каждому рецепту вида {id_рецепта: ["шаг1", "шаг2"]}. Сохраните этот словарь в файл steps_sample.json

from bs4 import BeautifulSoup

with open("./data/steps_sample.xml", "r") as f:
    data_xml = BeautifulSoup(f)

cook = {}

for recipe in data_xml.find_all("recipe"):
    id = recipe.find("id")
    if id.text not in cook:
        cook[id.text] = []
    for step in recipe.find_all("step"):
        cook[id.text].append(step.text)

with open("./data/steps_sample.json", "w") as f:
    json.dump(cook, f, indent=1)

#3.2 По данным файла steps_sample.xml сформируйте словарь следующего вида: кол-во_шагов_в_рецепте: [список_id_рецептов]

step_recipe = {}
for recipe in data_xml.find_all("recipe"):
    step_count = len(recipe.find_all("step"))
    if step_count not in step_recipe:
        step_recipe[step_count] = []
    step_recipe[step_count].append(recipe.find("id").text)

# print({k: step_recipe[k] for k in list(step_recipe)[:2]})

#3.3 Получите список рецептов, в этапах выполнения которых есть информация о времени (часы или минуты). Для отбора подходящих рецептов обратите внимание на атрибуты соответствующих тэгов.

recipes_with_time_info = []

for recipe in data_xml.find_all("recipe"):
    for step in recipe.find_all("step"):
        
        if "has_minutes" in step.attrs or "has_hours" in step.attrs:
            recipes_with_time_info.append(recipe.find("id").text)
            break


print(recipes_with_time_info[:5])

#3.4 Загрузите данные из файла recipes_sample.csv (ЛР2) в таблицу recipes. Для строк, которые содержат пропуски в столбце n_steps, заполните этот столбец на основе файла steps_sample.xml. Строки, в которых столбец n_steps заполнен, оставьте без изменений.

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

recipes = pd.read_csv("./data/recipes_sample.csv", sep=',')
recipes_with_missing_steps = recipes[recipes['n_steps'].isnull()]

print(recipes_with_missing_steps[['name', 'n_steps']].head(5)) 

with open("./data/steps_sample.xml", "r") as f:
    data_xml = BeautifulSoup(f, 'xml')

for recipe in data_xml.find_all("recipe"):
    id = int(recipe.find("id").text)
    if np.isnan(recipes[recipes["id"] == id]["n_steps"].values[0]):
        recipes.loc[recipes.id == id, "n_steps"] = len(
            recipe.find_all("step"))

recipes_with_missing_steps_2 = recipes[recipes['n_steps'].isnull()]

print(recipes_with_missing_steps_2[['name', 'n_steps']].head(5)) 

#3.5 Проверьте, содержит ли столбец n_steps пропуски. Если нет, то преобразуйте его к целочисленному типу и сохраните результаты в файл recipes_sample_with_filled_nsteps.csv

import numpy as np
import pandas as pd

recipes = pd.read_csv("./data/recipes_sample.csv", sep=',')

if recipes["n_steps"].isna().sum() == 0:
    recipes["n_steps"] = recipes["n_steps"].astype(np.int)
    recipes.to_csv("./data/recipes_sample_with_filled_nsteps.csv", index=False)
else:
    print("n_steps column has gaps. unable to save csv")
"""

def visualization():
  return """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

#Задачи для совместного разбора

#1. При помощи пакета pandas_datareader загрузите данные о ценах акций Apple с 2017-01-01 по 2018-12-31. Визуализируйте временные ряд цен акций.

import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()

start_date = '2017-01-01'
end_date = '2018-12-31'
aapl = pdr.get_data_yahoo('AAPL', start=start_date, end=end_date)

plt.figure(figsize=(14, 7))
plt.plot(aapl['Close'], label='Цена')
plt.xlabel('Дата')
plt.ylabel('Цена')
plt.title('Цена акций Apple с ' + start_date + ' по ' + end_date)
plt.legend()
plt.show()

#2. Проанализируйте временной ряд максимальной цены акций на предмет выбросов.

# Вычисление скользящего среднего и стандартного отклонения с окном размером 30 дней
aapl['Rolling_Mean'] = aapl['High'].rolling(window=30).mean()
aapl['Rolling_STD'] = aapl['High'].rolling(window=30).std()

# Вычисление верхнего и нижнего порога выбросов с помощью межквартильного размаха (IQR)
q1 = aapl['High'].quantile(0.25)
q3 = aapl['High'].quantile(0.75)
iqr = q3 - q1
upper_bound = q3 + 1.5 * iqr
lower_bound = q1 - 1.5 * iqr

# Определение выбросов
outliers = aapl[(aapl['High'] > upper_bound) | (aapl['High'] < lower_bound)]

# Визуализация временного ряда максимальной цены акций и выбросов
plt.figure(figsize=(14, 7))
plt.plot(aapl['High'], label='Максимальная цена акций')
plt.scatter(outliers.index, outliers['High'], color='red', label='Выбросы')
plt.xlabel('Дата')
plt.ylabel('Цена')
plt.title('Максимальная цена акций Apple с 2017-01-01 по 2018-12-31 и выбросы')
plt.legend()
plt.show()

#Лабораторная работа 5.1

#1. В файле average_ratings.npy содержится информация о среднем рейтинге 3 рецептов за период с 01.01.2019 по 30.12.2021. При помощи пакета matplotlib в одной системе координат (на одной картинке) изобразите три временных ряда, соответствующих средним рейтингам этих рецептов.
#По горизонтальной оси располагается номер дня (0, 1, 2, ...), по вертикальной - средний рейтинг рецептов в этот день.
#Названия рецептов и их индексы в файле average_ratings.npy:
#0: waffle iron french toast
#1: zwetschgenkuchen bavarian plum cake
#2: lime tea
#Результатом работы является визуализация, на которой:
#
#    добавлена подпись горизонтальной оси с текстом "Номер дня"
#    добавлена подпись вертикальной оси с текстом "Средний рейтинг"
#    добавлена подпись рисунка с текстом "Изменение среднего рейтинга трех рецептов"
#    каждый из временных рядов имеет уникальный цвет
#    добавлена легенда, на которой отображается название каждого из рецептов

#Примечание : для считывания файла воспользуйтесь функцией np.load.

import matplotlib.pyplot as plt
import numpy as np

# Загрузка данных из файла
average_ratings = np.load("average_ratings.npy")

# Создание вектора дней
days = np.arange(0, average_ratings.shape[1])

# Инициализация графика
plt.figure(figsize=(10, 6))

# Построение графиков для каждого рецепта
plt.plot(days, average_ratings[0], label="waffle iron french toast", color="red")
plt.plot(days, average_ratings[1], label="zwetschgenkuchen bavarian plum cake", color="blue")
plt.plot(days, average_ratings[2], label="lime tea", color="green")

# Добавление меток осей и заголовка графика
plt.xlabel("Номер дня")
plt.ylabel("Средний рейтинг")
plt.title("Изменение среднего рейтинга трех рецептов")

# Добавление легенды
plt.legend()

# Отображение графика
plt.show()

#2.Измените визуализацию, полученную в задании 1, таким образом, чтобы по горизонтальной оси отображались года, а между двумя соседними годами располагались засечки, соответствующие месяцам. 
#Для этого создайте диапазон дат от 01.01.2019 по 30.12.2021 с шагом в один день (например, вот так) и используйте этот диапазон при вызове метода plot. 
#Далее настройте major_locator и minor_locator горизонтальной оси (подробнее см. здесь)
#Примените к получившемуся рисунку цвета графиков, подписи, легенду из задания 1. Измените подпись горизонтальной оси, написав там слово "Дата".

import matplotlib.pyplot as plt
import numpy as np
from datetime import date, timedelta
import matplotlib.dates as mdates

# Загрузка данных из файла
average_ratings = np.load("average_ratings.npy")

# Создание диапазона дат
start_date = date(2019, 1, 1)
end_date = date(2021, 12, 30)
date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

# Инициализация графика
fig, ax = plt.subplots(figsize=(10, 6))

# Построение графиков для каждого рецепта
ax.plot(date_range, average_ratings[0], label="waffle iron french toast", color="red")
ax.plot(date_range, average_ratings[1], label="zwetschgenkuchen bavarian plum cake", color="blue")
ax.plot(date_range, average_ratings[2], label="lime tea", color="green")

# Добавление меток осей и заголовка графика
ax.set_xlabel("Дата")
ax.set_ylabel("Средний рейтинг")
ax.set_title("Изменение среднего рейтинга трех рецептов")

# Настройка major_locator и minor_locator горизонтальной оси
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.xaxis.set_minor_locator(mdates.MonthLocator())

# Добавление легенды
ax.legend()

# Отображение графика
plt.show()

#3. Измените визуализацию, полученную в задании 2, разбив одну картинку на три, расположенных друг под другом. Три изображения должны иметь одну общую горизонтальную ось (каждое изображение засечки в нижней части, но значения этих засечек находятся только под самым нижним изображением). Примените к получившемуся рисунку цвета графиков, подписи, легенду из задания 2.

import matplotlib.pyplot as plt
import numpy as np
from datetime import date, timedelta
import matplotlib.dates as mdates

# Загрузка данных из файла
average_ratings = np.load("average_ratings.npy")

# Создание диапазона дат
start_date = date(2019, 1, 1)
end_date = date(2021, 12, 30)
date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

# Инициализация графика с тремя подграфиками
fig, axs = plt.subplots(3, 1, figsize=(10, 15), sharex=True)

# Названия рецептов
recipes = [
    "waffle iron french toast",
    "zwetschgenkuchen bavarian plum cake",
    "lime tea"
]

# Цвета графиков
colors = ["red", "blue", "green"]

# Построение графиков для каждого рецепта
for i in range(3):
    axs[i].plot(date_range, average_ratings[i], label=recipes[i], color=colors[i])
    axs[i].set_ylabel("Средний рейтинг")
    axs[i].legend()

# Настройка major_locator и minor_locator горизонтальной оси
axs[2].xaxis.set_major_locator(mdates.YearLocator())
axs[2].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
axs[2].xaxis.set_minor_locator(mdates.MonthLocator())

# Добавление метки для общей горизонтальной оси
fig.text(0.5, 0.04, "Дата", ha="center", va="center")

# Отображение графика
plt.show()

#4. В файле visitors.npy представлена информация о количестве посетителей сайта в течении первых 100 дней после объявления сайтом акции. Постройте график изменения количества пользователей в зависимости от дня в двух вариантах, расположенных рядом по горизонтале. В обоих случаях изобразите график в виде ломаной, но в первом случае оставьте линейный масштаб осей, а во втором случае сделайте вертикальную ось в логарифмическом масштабе. Добавьте на обе картинки подпись над этим графиком к текстом y(x)=λe−λx
#Добавьте на оба изображения красную горизонтальную линию на уровне y=100. Добавьте на обе картинки подпись над этой линией с текстом y(x)=100
#Добавьте на оба изображения подписи осей; горизонтальную ось подпишите текстом "Количество дней с момента акции", вертикальную - "Число посетителей".
#Добавьте общий заголовок для фигуры с текстом "Изменение количества пользователей в линейном и логарифмическом масштабе".

import matplotlib.pyplot as plt
import numpy as np

# Загрузка данных из файла
visitors = np.load("visitors.npy")

# Создание вектора дней
days = np.arange(0, len(visitors))

# Инициализация графика с двумя подграфиками, расположенными горизонтально
fig, axs = plt.subplots(1, 2, figsize=(14, 6))

# Настройка общего заголовка для фигуры
fig.suptitle("Изменение количества пользователей в линейном и логарифмическом масштабе")

# Построение графиков в линейном и логарифмическом масштабе
for ax, scale in zip(axs, ['linear', 'log']):
    ax.plot(days, visitors, label=r'y(x) = $\lambda e^{-\lambda x}$')
    ax.axhline(y=100, color='r', linestyle='-', label='y(x)=100')
    
    ax.set_title(f"Масштаб: {scale}")
    ax.set_xlabel("Количество дней с момента акции")
    ax.set_ylabel("Число посетителей")
    ax.set_yscale(scale)
    ax.legend()

# Отображение графика
plt.show()

#Лабораторная работа 5.2
#Визуализация данных на основе структур pandas.

#Для продолжения работы загрузите таблицы recipes и reviews (ЛР2)

import matplotlib.pyplot as plt
import pandas as pd

# Загрузка данных
reviews = pd.read_csv("reviews_sample.csv")
recipes = pd.read_csv("recipes_sample.csv")

#5. Назовем рецепты короткими, если они занимают строго меньше 5 минут; средними, если они занимают от 5 до 50 минут (не включая 50), и длинными, если они занимают от 50 минут и больше. 
#Сгруппируйте все рецепты по данному признаку и для каждой группы посчитайте 2 величины: среднее количество шагов рецептов в группе и размер группы. 
#При помощи методов структур pandas постройте столбчатую диаграмму, где каждый столбец означает группу (короткие, средние или длинные рецепты), а высота столбца обозначает среднее количество шагов рецептов в группе. 
#Рядом по горизонтали разместите круговую диаграмму, на которой отображены размеры каждой из групп.

#Добавьте следующие подписи:

#    по горизонтальной оси под столбчатой диаграммой напишите "Группа рецептов"
#    по вертикальной оси слева от столбчатой диаграммы напишите "Средняя длительность"
#    над круговой диаграммой напишите "Размеры групп рецептов"

# Группировка рецептов по длительности
def categorize_duration(duration):
    if duration < 5:
        return "Короткие"
    elif 5 <= duration < 50:
        return "Средние"
    else:
        return "Длинные"

recipes["group"] = recipes["minutes"].apply(categorize_duration)
grouped = recipes.groupby("group").agg({"n_steps": "mean", "group": "count"}).rename(columns={"group": "count"})

# Построение столбчатой диаграммы
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

grouped["n_steps"].plot(kind="bar", ax=ax1, rot=0)
ax1.set_xlabel("Группа рецептов")
ax1.set_ylabel("Средняя длительность")

# Построение круговой диаграммы
grouped["count"].plot(kind="pie", ax=ax2, autopct="%.1f%%", legend=False)
ax2.set_ylabel("")
ax2.set_title("Размеры групп рецептов")

plt.show()

#6. Из всего множества отзывов оставьте только те, которые были даны в 2008 и 2009 годах. Воспользовавшись возможностями метода pd.DataFrame.plot.hist, постройте 2 гистограммы столбца rating. Гистограммы должны быть расположены рядом по горизонтали. Левая гистограмма соотвествует 2008 году, правая - 2009 году. Добавьте общую подпись для рисунка с текстом "Гистограммы рейтинга отзывов в 2008 и 2009 годах". Добейтесь того, чтобы подпись вертикальной оси правого рисунка не "наезжала" на левый рисунок.

import matplotlib.pyplot as plt
import pandas as pd

reviews = pd.read_csv("reviews_sample.csv")
recipes = pd.read_csv("recipes_sample.csv")

# Фильтрация отзывов за 2008 и 2009 годы
reviews["date"] = pd.to_datetime(reviews["date"])
reviews_2008 = reviews[reviews["date"].dt.year == 2008]
reviews_2009 = reviews[reviews["date"].dt.year == 2009]

# Построение гистограмм
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

reviews_2008["rating"].plot.hist(ax=ax1, bins=20, edgecolor="black")
ax1.set_title("2008")
ax1.set_xlabel("Рейтинг")
ax1.set_ylabel("Количество отзывов")

reviews_2009["rating"].plot.hist(ax=ax2, bins=20, edgecolor="black")
ax2.set_title("2009")
ax2.set_xlabel("Рейтинг")
ax2.set_ylabel("Количество отзывов")

fig.suptitle("Гистограммы рейтинга отзывов в 2008 и 2009 годах")
plt.show()

#Визуализация данных при помощи пакета seaborn

#7. При помощи пакета seaborn постройте диаграмму рассеяния двух столбцов из таблицы recipes: n_steps и n_ingredients. Укажите в качестве группирующей переменной (hue) категориальную длительность рецепта (короткий, средний или длинные; см. задание 5).

#Добавьте заголовок рисунка "Диаграмма рассеяния n_steps и n_ingredients"

#Прокомментируйте, наблюдается ли визуально линейная зависимость между двумя этими переменными. Ответ оставьте в виде текстовой ячейки под изображением.

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sb

reviews = pd.read_csv("reviews_sample.csv")
recipes = pd.read_csv("recipes_sample.csv")

# Создание столбца с категориями длительности рецепта
def group_by_duration(minutes):
    if minutes < 5:
        return "Короткий"
    elif 5 <= minutes < 50:
        return "Средний"
    else:
        return "Длинный"

recipes["duration_category"] = recipes["minutes"].apply(group_by_duration)

# Построение диаграммы рассеяния
plt.figure(figsize=(12, 6))
sb.scatterplot(data=recipes, x="n_steps", y="n_ingredients", hue="duration_category")
plt.title("Диаграмма рассеяния n_steps и n_ingredients")
plt.show()

#На основе диаграммы рассеяния сложно сделать вывод о наличии линейной зависимости между n_steps и n_ingredients. Визуально наблюдается некоторая концентрация точек в левом нижнем углу графика, что указывает на то, что короткие рецепты имеют меньшее количество ингредиентов и шагов. Однако точки на графике разбросаны, и нет четкой линии, которая бы показывала линейную зависимость между этими переменными.

8. Объедините две таблицы recipes и reviews и постройте корреляционную матрицу на основе столбцов "minutes", "n_steps", "n_ingredients" и "rating". При помощи пакета seaborn визуализируйте полученную матрицу в виде тепловой карты (heatmap).

Добавьте в ячейки тепловой карты подписи (значения к-та корреляции). Измените цветовую палитру на YlOrRd.

Добавьте заголовок рисунка "Корреляционная матрица числовых столбцов таблиц recipes и reviews"

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sb

reviews = pd.read_csv("reviews_sample.csv")
recipes = pd.read_csv("recipes_sample.csv")

# Объединение таблиц
merged_df = pd.merge(recipes, reviews, left_on='id', right_on='recipe_id')

# Вычисление корреляционной матрицы
corr_matrix = merged_df[["minutes", "n_steps", "n_ingredients", "rating"]].corr()

# Визуализация корреляционной матрицы в виде тепловой карты
plt.figure(figsize=(10, 6))
sb.heatmap(corr_matrix, annot=True, cmap="YlOrRd", fmt=".2f")
plt.title("Корреляционная матрица числовых столбцов таблиц recipes и reviews")
plt.show()
"""

def kr1():
  return """
#1. Выберите случайным образом и выведите информацию о 15 различных пассажирах с именами, которые начинаются на букву "А".
#Для расчётов использовать numpy

import numpy as np

import csv
 
with open("train.csv", 'r') as x:
    sample_data = list(csv.reader(x, delimiter=","))
 
data = np.array(sample_data)
 
#dat = pd.read_csv('train.csv')
#data = dat.to_numpy()
 
a_passengers = [row for row in data if row[3][0]=='A']
 
#data = data[data[:,3][0]=='A']
#print(data)

# Выбор 15 случайных пассажиров
#random_passengers = np.random.choice(a_passengers, size=15, replace=False)
#random_passengers
# Вывод информации о выбранных пассажирах
#for passenger in random_passengers:
    #print(passenger)

rng = np.random.default_rng()
random_passengers = rng.choice(a_passengers, 15, False)
for passenger in random_passengers:
    print(passenger)

#print(d)

#2. Выведите информацию, хранящуюся в файле train.csv, о пассажирах Титаника женского пола, кабины которых известны
#Для расчётов использовать pandas

import pandas as pd
train = pd.read_csv('train.csv')
#print(train)

passengers = train[train['Cabin'].notna() * train['Sex']=='female']

print(passengers[['Sex', 'Cabin']])
"""

def ms5i1():
  return """
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as sts

data_str = '''NA; More; Less; More; NA; Unkn; NA; More; Less; Unkn; Less; More; More; NA; More; Norm; Less; NA; Norm; More; Norm; Less; Unkn; Unkn; More; More; More; Unkn; More; Unkn; Less; More; NA; More; More; Unkn; Unkn; NA; Unkn; More; More; Unkn; Unkn; Unkn; Norm; Norm; NA; NA; More; More; More; Norm; Unkn; Less; More; NA; Unkn; Norm; Norm; More; More; More; Unkn; NA; More; Unkn; Norm; More; Less; Norm; Norm; NA; Unkn; Less; Unkn; Less; Norm; Unkn; Less; Norm; Less; Unkn; Less; More; More; Unkn; Unkn; Less; Less; Unkn; Unkn; Norm; More; Unkn; Unkn; NA; More; More; More; NA; More; More; Unkn; Norm; NA; Less; More; More; More; Norm; More; Unkn; Unkn; Unkn; Unkn; NA; NA; More; Unkn; More; Unkn; More; NA; More; More; More; More; More; NA; Norm; More; Less; NA; Unkn; Norm; More; Less; More; Less; Unkn; Unkn; Less; More; More; More; Less; Unkn; NA; More; More; Unkn; Unkn; More; More; NA; Less; Less; NA; NA; NA; Norm; More; More; Norm; Less; Less; Less; Unkn; Norm; Unkn; Unkn; Less; Unkn; Less; Less; More; Unkn; Unkn; Norm; Unkn; Less; NA; More; More; Norm; Unkn; Less; NA; More; More; More; Norm; Unkn; Unkn; Unkn; Less; NA; More; Less; Unkn; Unkn; More; Less; More; Less; Norm; Unkn; Norm; More; Norm; More; More; Norm; Unkn; Less; Less; Less; NA; Unkn; Unkn; Unkn; NA; Less; Unkn; Norm; More; Unkn; Less; More; Unkn; NA; Less; More; NA; More; Unkn; Unkn; Norm; Unkn; Unkn; NA; More; Less; Norm; Unkn; More; More; Unkn; NA; More; Unkn; More; Unkn; More; More; NA; NA; More; Norm; More; More; More; Less; More; More; More; NA; Less; Less; Less; Norm; Unkn; Less; Less; Norm; Norm; More; Less; More; More; Norm; Less; Unkn; Unkn; Unkn; Less; Norm; Unkn; More; More; More; NA; NA; Norm; Norm; NA; More; Norm; More; More; Norm; Less; More; Unkn; Norm; More; Norm; More; More; NA; More; Less; Unkn; Unkn; More; Norm; Less; More; Less; Less'''
data = pd.Series(data_str.replace('NA; ', '').replace('; NA', '').replace(' ', '').split(';'))
print(data.head())

print()
print('Kоличество различных вариантов ответов респондентов, встречающиеся в очищенной выборке =', len(data.unique()))
print(data.unique())

print()
print('Объем очищенной от "NA" выборки =', len(data))

print()
#print(data[data=="L1"].head())
#print('Kоличество респондентов, которые дали ответ "L1" =', len(data[data=="L1"]))
print('Kоличество пропущенных данных "NA" в исходной выборке =', data_str.count('NA'))

print()
print('Доля респондентов, которые дали ответ "More" =', len(data[data=="More"]) / len(data))

n = len(data)
p = len(data[data=="More"]) / len(data)
q = 1 - p
gamma = 0.9
z = sts.norm.ppf((1+gamma)/2)
delta = z * np.sqrt(p*q/n)

print()
print('Левая граница 0.9-доверительного интервала для истинной доли ответов "More" =', p - delta)
print('Правая граница 0.9-доверительного интервала для истинной доли ответов "More" =', p + delta)

alpha = 0.05
ni_obs = []
for i in sorted(data.unique()):
    ni_obs.append(len(data[data==i]))
ni_obs = np.array(ni_obs)
print()
print('ni_obs =', ni_obs)

pi = np.array([1/len(data.unique())]*len(data.unique()))
print('pi =', pi)

n = sum(ni_obs)
l = len(ni_obs)
ni_exp = n*pi
print('ni_exp =', ni_exp)

chi2_obs = sum((ni_obs - ni_exp)**2/ni_exp)
print('chi2_obs =', chi2_obs)

chi2_right_cr = sts.chi2.isf(alpha, l-1)
print('chi2_right_cr =', chi2_right_cr)

print('Количество степеней свободы =', l - 1)
print('H0 не отвергается') if chi2_obs < chi2_right_cr else print('H0 отвергается')

plt.hist(data)
#plt.hist(data, bins = 6)
plt.show()  
"""

def ms5i2():
  return """
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as sts

data2_str = '''(255.4105, -253.15); (243.7803, -275.74); (228.7959, -258.14); (229.3319, -250.39); (233.3861, NA); (269.9092, -280.62); (202.303, NA); (210.9884, -263.35); (234.0089, -284.62); (244.3579, -277.5); (226.8919, -225.61); (236.7923, -297.6); (228.431, -289.36); (217.5431, NA); (322.5126, -251.8); (241.8376, -292.33); (220.3509, -228.18); (NA, -248.97); (214.4076, -272.53); (268.6563, -230.77); (192.614, NA); (258.5836, -259.92); (254.3837, -292.96); (247.7287, -266.2); (240.2835, -319.4); (NA, -273.15); (262.1739, -234.77); (280.7547, -243.68); (194.9311, -252.4); (234.2897, -288.5); (258.6198, -284.84); (224.1644, -233.6); (226.2993, -219.4); (174.8306, -276.25); (248.0166, -259.08); (251.3936, -249.28); (245.2212, -287.85); (220.1741, NA); (204.9634, -260.04); (NA, -287.24); (NA, -248.57); (240.7583, -281.76); (268.2492, -259.21); (220.2528, -205.43); (256.2648, -219.91); (NA, -280.12); (NA, -262.83); (303.6843, -270.06); (249.0596, NA); (193.3267, NA); (227.628, -240.52); (264.958, -194.2); (271.4568, -242.4); (NA, -236.48); (293.038, -216.29); (227.8075, NA); (216.9755, -286.05); (273.7833, -293.18); (NA, -233.47); (273.8847, -249.49); (252.536, -224.27); (263.5997, -232.96); (208.5429, -325.94); (234.5393, NA); (241.4325, -236.23); (215.2, -275.25); (NA, -277.67); (223.6072, -231.9); (214.332, -238.32); (232.6875, -259.09); (228.3214, NA); (238.6967, -224.82); (257.8638, -247.11); (186.3718, -262.24); (195.9218, -259.06); (273.1004, -262.08); (205.5066, -278.41); (197.9086, -229.42); (168.1917, NA); (NA, -248.93); (NA, -281.64); (212.8216, -254.78); (199.8364, NA); (279.5461, -281.9); (255.1225, -211.91); (229.5242, -299.81); (229.6714, -225.98); (NA, -250.74); (237.4413, -248.93); (241.7766, -195.81); (291.3587, -275.12); (NA, -308.46); (258.5031, -288.51); (232.3787, -261.09); (228.4212, -193.58); (233.0912, -244.6); (238.5418, -222.17); (248.6548, -240.71); (260.2826, -271.51); (236.8718, -252.47); (258.1758, -256.62); (273.8823, NA); (208.4837, -306.19); (239.8302, -257.38); (NA, -237.11); (274.7391, -253.43); (280.1018, -243.47); (275.7511, NA); (292.4302, -236.13); (254.0945, -263.82); (305.1476, -286.9); (240.2813, -294.77); (249.6823, -220.18); (245.0505, -240.55); (244.0719, -278.86); (234.2264, -240.97); (244.8872, -262.63); (245.0034, -259.61); (247.5337, NA); (238.3164, -288.74); (239.57, -227.33); (250.159, NA); (233.7068, -198.52); (252.5969, -267.27); (NA, -207.13); (232.7191, -252.18); (254.9181, NA); (255.1942, NA); (217.9629, -204.61); (217.0407, -233.86); (236.2114, -254.57); (238.5378, -260.52); (232.7524, -287.79); (262.582, -314.57); (212.8096, -228.2); (201.0162, -193.42); (262.1079, NA); (244.4351, -247.51); (244.68, -258.87); (230.9591, -265.74); (279.0081, -219.27); (266.1207, -204.96); (239.825, -221.2); (NA, -243.02); (214.6849, -285.69); (242.5553, NA); (231.8085, -213.43); (257.5861, -290.58); (226.8102, -230.49); (239.8886, -215.95)'''
data2 = data2_str.replace('(','').replace(')','').replace(' ', '').split(';')

X=[]
Y=[]
for i in data2:
  a, b = i.split(',')
  try:
    np.float64(a)
    np.float64(b)
    X.append(np.float64(a))
    Y.append(np.float64(b))
  except:
    continue
      
df = pd.concat([pd.Series(X, name = 'X'), pd.Series(Y, name = 'Y')], axis= 1)
print(df.head())

print()
print('Выборочный коэффициент корреляции Пирсона между X и Y =', df.corr()["X"]["Y"])
print()
'''
#для H1: mu_x != mu_y
p_val = sts.ttest_ind(X, Y, equal_var=False).pvalue 
print('p_val =', p_val)
alpha = 0.05
print('H0 не отвергается') if p_val > alpha else print ('H0 отвергается')
print()
'''

# Для H1: mu_x < mu_y или mu_x > mu_y(в формуле на месте alternative указываем из условия)
alternative = 'greater' # from ['two-sided','less','greater']
p_val = sts.ttest_ind(X, Y, alternative = alternative, equal_var = False).pvalue
print('p_val =', p_val)
alpha = 0.05
print('H0 не отвергается') if p_val > alpha else print ('H0 отвергается')
print()

'''
#для H1: sigma2_x > sigma2_y или sigma2_x < sigma2_y
s2_x = df['X'].var(ddof = 1)
s2_y = df['Y'].var(ddof = 1)
m = len(df['X'])
n = len(df['Y'])

f = s2_x / s2_y

if s2_x > s2_y:
    f_obs = f
    k1 = m - 1
    k2 = n - 1
else: 
    f_obs = 1/f
    k1 = n - 1
    k2 = m - 1

alpha = 0.1
f_cr = sts.f.ppf(1 - alpha, k1, k2)
print('H0 не отвергается') if f_obs < f_cr else print ('H0 отвергается')

p_val = sts.f.sf(f_obs, k1, k2)
print('p_val =', p_val)

print('H0 не отвергается') if p_val > alpha else print ('H0 отвергается')
'''

# для H1: sigma2_x != sigma2_y
alpha = 0.05
s2_x = df['X'].var(ddof = 1)
s2_y = df['Y'].var(ddof = 1)
m = len(df['X'])
n = len(df['Y'])

f = s2_x / s2_y

if s2_x > s2_y:
    f_obs = f
    k1 = m - 1
    k2 = n - 1
else: 
    f_obs = 1/f
    k1 = n - 1
    k2 = m - 1

f_cr = sts.f.ppf(1 - alpha/2, k1, k2)
print('H0 не отвергается') if f_obs < f_cr else print ('H0 отвергается')

p_val = 2*min(sts.f.cdf(f_obs, k1, k2), sts.f.sf(f_obs, k1, k2))
print(p_val)

print('H0 не отвергается') if p_val > alpha else print ('H0 отвергается')

print()
"""

def ms5i3():
  return """
import numpy as np
import pandas as pd
import scipy.stats as sts
import matplotlib.pyplot as plt

x = "-194.5; -216.33; -247.2; -241.51; -215.81; -266.72; -164.22; -231.4; -177.55; -230.87; -225.82; -230.89; -242.38; -220.43; -197.21; -240.79; -213.17; -236.68; -179.11; -199.46; -253.28; NA; -206.94; -205.48; -238.74; -212.82; -201.24; -186.79; -203.6; -205.14; -213.14; -196.22; -175.24; -215.01; -213.53; -235.86; NA; -227.27; -215.71; -234.83; NA; NA; -225.62; -213.72; -216.66; -200.56; -244.84; -189.06; -224.67; NA; -218.91; -218.52; NA; NA; -199.67; NA; NA; -209.94; -201.37; -197.21; NA; -196.01; -252.47; -203.01; NA; -208.58; -198.66; -262.14; -176.8; -220.92; -209.73; -211.53; -191.44; NA; -197.27; -224.94; -207.73; -198.88; NA; -195.82; -210.4; -166.47; -248.77; -196.51; -214.3; -234.92; -213.76; -234.13; -228.02; -193.68; -240.59; -229.04; -311.84; -197.03; -184.52; -205.3; -225.06; -165.86; -207.95; -237.96; -240.54; -178.94; -229.89; -229.79; -248.15; -252.93; -197.9; -257.07; -215.84; -204.28; -175.58; -247.94; -205.15; -189.81; -236.46; -235.39; -208.77; -234.83; -234.24; -242.6; -195.97; -207.14; -215.87; -224.42; -239.24; NA; -246.24; -203.26; -198.26; -211.54; NA; -188.53; -199.47; -206.53; -194.52; -175.7; -193.95; -235.34; -231.65; -214.7; -226.46; -206.05; -227.57; -203.11; -222.76; -235.67; NA; -193.68; -192.3; -206.99; -180.77; -212.9; -247.79; -247.04; -236.32; -175.46; -224.83; -217.28; -215.92; -217.53; -258.44; -208.03; -229.66; -221.78; -175.56; -310.16; -219.92; -206.41; -200.88; -169.46; -224.78; -228.77; -225.96; -215.5; -227.67; -205.34; -227.56; -236.04; -199.43; -246.95; -199.51; -258.61; -259.35; -216.13; -202.65; -228.51; -228.42; NA; -171.48; -188.09; -218.25; -221.41; -226.16; -221.05; -205.72; -195.77; -215.09; -125.66; -215.61; -189.87; -225.09; -194.28; -219.73; -198.24; -206.85; -250.06; -237.51; -252.7; -220.99; -240.83; -208.24; -232.38; -215.78; NA; -236.41; -209.53; -223.97; -215.64; -221.63; NA; NA; -241.99; -215.64; -204.62; -189.28; -211.99; -214.46; -229.05; -204.46; -194.6; -228.65; -241.29; -220.49; -232.95; -189.36; -225.44; -196.95; -242.4; -240.32; -240.08; -203.81; -209.52; -242.01; -181.97; -203.57; -227.52; -236.07; -244.95; -216.21; -218.62; -228.94; -254.22; -260.59; -209.84; -306.205; -183.76; -215.28; -260.43; -193.43; -230.69; -228.14; -219.73; -197.84; -226.96; -218.84; NA; -235.9; -205.63; NA; NA; -207.46; -203.35; -260.11; NA; -200.15; -206.73; -248.23; -161.89; -205.84; -163.26; -166.77; -233.06; -231.91; NA; -206.19; -203.03; -204.72; -207.17; -230.83; -218.94; -216.35; -205.73; -184.74; -237.34; NA; -245.27; -233.61; -193.95; -227.94; -203.37; -191.15; -176.89; -236.3; -223.89; NA; -218.12; -215.71; -205.03; -255.42; -235.13"
data = x.replace(' ', '').split(';')
print('Объём исходной выборки =', len(data))
print('Количество пропущенных значений в исходной выборке, обозначенные как "NA" =', x.count('NA'))

lst = []
for i in data:
    try: 
        lst.append(np.float64(i))
    except:
        lst.append(np.nan)

lst_ser = pd.Series(lst).dropna()
plt.boxplot(lst_ser)
plt.show()
plt.hist(lst_ser)
plt.show()

print('Объем очищенной от пропусков выборки =', lst_ser.count())
print('Количество пропущенных значений в исходной выборке, обозначенные как "NA" =', len(data) - lst_ser.count())
print('Ошибка выборки =', lst_ser.std(ddof=1)/(lst_ser.count())**0.5)
print('Минимальное значение в вариационном ряду =', lst_ser.min())
print('Максимальное значение в вариационном ряду =', lst_ser.max())
print('Значение первой квартили (Q1) =', np.quantile(lst_ser,0.25))
print('Значение медианы (Q2) =', np.quantile(lst_ser,0.5))
print('Значение третьей квартили (Q3) =', np.quantile(lst_ser,0.75))
print('Квартильный размах =', np.quantile(lst_ser,0.75) - np.quantile(lst_ser,0.25))
print('Среднее выборочное значение =', lst_ser.mean())
print('Исправленная дисперсия =', lst_ser.var(ddof=1))
print('Стандартное отклонение =', lst_ser.std(ddof=1))
print('Размах выборки =', lst_ser.max() - lst_ser.min())
print('Эксцесс =', sts.kurtosis(lst_ser, bias=False))
print('Коэффициент асимметрии =', sts.skew(lst_ser, bias=False))

gamma = 0.99
n = lst_ser.count()
x_sr = lst_ser.mean()
t_gamma = sts.t.ppf((1+gamma)/2, n-1)
s = lst_ser.std(ddof=1)
delta = t_gamma*s/np.sqrt(n)
print('Левая граница 0.99-доверительного интервала для E(X) =', x_sr - delta) 
print('Правая граница 0.99-доверительного интервала для E(X) =', x_sr + delta)

gamma = 0.99
n = lst_ser.count()
s2 = np.var(lst_ser, ddof=1)
chi2_gamma1 = sts.chi2.ppf((1+gamma)/2, n-1)
chi2_gamma2 = sts.chi2.ppf((1-gamma)/2, n-1)
print('Левая граница 0.99-доверительного интервала для Var(X) =', (n-1)*s2/chi2_gamma1) 
print('Правая граница 0.99-доверительного интервала для Var(X) =', (n-1)*s2/chi2_gamma2)

print('Значение 63%-квантили (Q2) =', np.quantile(lst_ser,0.63))
print('Квантиль уровня 0.1 =', np.quantile(lst_ser, 0.1))

lst_min = np.quantile(lst_ser,0.25) - 1.5*(np.quantile(lst_ser,0.75) - np.quantile(lst_ser,0.25))
lst_max = np.quantile(lst_ser,0.75) + 1.5*(np.quantile(lst_ser,0.75) - np.quantile(lst_ser,0.25))
print('Нижняя граница нормы =', lst_min)
print('Верхняя граница нормы =', lst_max)
print('Количество выбросов ниже нижней нормы =', len(lst_ser[lst_ser<lst_min]))
print('Количество выбросов выше верхней нормы =', len(lst_ser[lst_ser>lst_max]))
print('Общее количество выбросов =', len(lst_ser[lst_ser>lst_max]) + len(lst_ser[lst_ser<lst_min]))

######################################################################################
modes = sts.mode(lst_ser)
mod_count = lst_ser.value_counts()[modes[0]]
if mod_count == 1:
    print('ДОП5) Моды нет')
    print('ДОП6) Как часто встречается "мода" = 0')
else:
    print('ДОП5) Мода =', modes[0])
    print('ДОП6) Как часто встречается "мода" =', mod_count)
#####################################################################################

Q1 = np.quantile(lst_ser,0.25)
Q3 = np.quantile(lst_ser,0.75)
RQ = Q3 - Q1
lst_min = Q1 - 1.5*RQ
lst_max = Q3 + 1.5*RQ
lst_no_out = lst_ser[(lst_ser>=lst_min)&(lst_ser<=lst_max)]

plt.boxplot(lst_no_out)
plt.show()
plt.hist(lst_no_out)
plt.show()
"""
