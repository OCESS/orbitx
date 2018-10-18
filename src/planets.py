import random

# dictionaries with planet parameters
sun = { 'name': "Sun",
        'x': random.uniform(-1e300, 1e300),
        'y': random.uniform(-1e300, 1e300),
        'vx': random.uniform(-1e300, 1e300),
        'vy' : random.uniform(-1e300, 1e300),
        'r' : random.uniform(-1e300, 1e300),
       }

earth = { 'name': "Earth",
          'x': random.uniform(-1e300, 1e300),
          'y': random.uniform(-1e300, 1e300),
          'vx': random.uniform(-1e300, 1e300),
          'vy': random.uniform(-1e300, 1e300),
          'r': random.uniform(-1e300, 1e300),
        }

mars = {'name': "Mars",
          'x': random.uniform(-1e300, 1e300),
          'y': random.uniform(-1e300, 1e300),
          'vx': random.uniform(-1e300, 1e300),
          'vy': random.uniform(-1e300, 1e300),
          'r': random.uniform(-1e300, 1e300),
        }

planet_list = [sun, earth, mars]
