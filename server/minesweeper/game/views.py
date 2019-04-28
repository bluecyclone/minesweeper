from random import randint
from django.http import JsonResponse
import json
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import BoardSerializer
from .models import Board
# Create your views here.

class BoardView(APIView):
    def get(self, request):
        boards = Board.objects.all()
        serializer = BoardSerializer(boards, many=True)
        return Response({"boards": serializer.data})

    def post(self, request):
        difficulty = request.data.get('difficulty')
        self.width = (int(difficulty) + 1) * 8
        self.height = (int(difficulty) + 1) * 8
        self.num_bombs = ( (int(difficulty) + 1) ** 2 ) * 10
        self.generate_map()

        data = {
            "mines":self.num_bombs,
            "data": str(self.data),
            "board": str(self.get_map_matrix('notReveal')),
            "state":"new",
            "width": self.width,
            "height": self.height
        }

        serializer = BoardSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        inserted = {
            "id": serializer.data.get('id'),
            "mines":self.num_bombs, 
            "board": self.get_map_matrix('notReveal'),
            "state":"new"
        }
        return Response(inserted)
    
    
    def open(request, id):
        game = Board.objects.get(id=id)
        view = BoardView()
        view.data = game.data
        view.width = game.width
        view.height = game.height
        response = {
            "id": id,
            "mines":game.mines, 
            "board": view.get_map_matrix('notReveal'),
            "state":game.state
        }
        return JsonResponse(response)


    def check(request, id):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        game = Board.objects.get(id=id)
        
        view = BoardView()
        view.data = game.data
        view.width = game.width
        view.height = game.height

        if game.state == "lost" :
            return JsonResponse( {
                "id": id,
                "mines":game.mines, 
                "board": view.get_map_matrix('reveal'),
                "state":game.state
            })

        content = view.mark(x=body['col'], y=body['row'])
        view.compile_empties(x=body['col'], y=body['row'])
        
        if content == 'B' :
            game.state = "lost"
            map = view.get_map_matrix('reveal')
        else :
            game.state = "playing"
            map = view.get_map_matrix('notReveal')
        if view.check_for_win() :
            game.state = "won"
            map = view.get_map_matrix('reveal')
        
        game.data = view.data
        game.save()

        response = {
            "id": id,
            "mines":game.mines, 
            "board": map,
            "state":game.state
        }
        return JsonResponse(response)

    # Mark a coordinate as clicked
    def mark(self, x, y):
        contents = self._get_contents(x, y)

        if contents == 'B':
            return "B"
        elif contents == 'E':
            num_bombs = self._count_adj_bombs(x, y)
            self._change_contents(x, y, str(num_bombs))
            return num_bombs

    # Perform chain reaction of supers to find all revealed coords
    def compile_empties(self, x, y):
        empties = set(self._get_adj_empties(x, y))
        supers = self._get_unmarked_supers(empties)

        while supers:
            group = supers.pop()
            new_empties = self._get_adj_empties(group[0], group[1])
            new_supers = self._get_unmarked_supers(new_empties)
            supers = supers.union(new_supers)
            empties = empties.union(new_empties)
            self._change_contents(group[0], group[1], str(group[2]))

        return list(empties)

    # Get all empty spots adjacent to coordinate
    def _get_adj_empties(self, x, y):
        bombs = self._count_adj_bombs(x, y)
        empties = [(x, y, bombs)]
        coords = self._build_adj_coords(x, y)

        for pair in coords:
            out_of_bounds_x = pair[0] < 0 or pair[0] >= self.width
            out_of_bounds_y = pair[1] < 0 or pair[1] >= self.height

            if out_of_bounds_x or out_of_bounds_y:
                continue

            bombs = self._count_adj_bombs(pair[0], pair[1])
            pair.append(bombs)
            empties.append(tuple(pair))

            if bombs != 0:
                self._change_contents(pair[0], pair[1], str(bombs))

        return empties

    # Get all the supers from a list that aren't yet marked
    def _get_unmarked_supers(self, superclears):
        supers = set([])
        for group in superclears:
            if group[2] == 0 and self._get_contents(group[0], group[1]) == 'E':
                supers.add(group)
        return supers

    def generate_map(self):
        data = []

        # Make empty map
        for i in range(self.width * self.height):
            data.append('E')
        self.data = "".join(data)

        # Place the bombs
        for i in range(self.num_bombs):
            self._place_random_bomb()

    # Place a single random bomb on the map
    def _place_random_bomb(self):
        is_set = False

        while not is_set:
            randx = randint(0, self.width - 1)
            randy = randint(0, self.height - 1)

            if self._get_contents(randx, randy) == 'E':
                self._change_contents(randx, randy, 'B')
                is_set = True

    # Get the contents of a single space on the map
    def _get_contents(self, x, y):
        index = self._get_data_index(x, y)
        c = self.data[index]
        return c

    # Change the contents of a single space on the map
    def _change_contents(self, x, y, new_content):
        index = self._get_data_index(x, y)
        data = list(self.data)
        data[index] = new_content
        self.data = "".join(data)

    # Transform x, y coordinate into index in the data field
    def _get_data_index(self, x, y):
        z = self.width * y
        index = z + x
        return index

    # Get a matrix version of the map
    def get_map_matrix(self, type):

        matrix = []

        for i in range(self.height):
            row = []
            for j in range(self.width):
                content = self._get_contents(j, i)

                # a revealing matrix will show everything
                if type != 'reveal':
                    if content == 'B' or content == 'E':
                        content = ''

                else:
                    if content != 'B':
                        content = self._count_adj_bombs(j, i)

                row.append(content)
            matrix.append(row)

        return matrix

    # Count the number of bombs adjacent to coordinate
    def _count_adj_bombs(self, x, y):
        count = 0
        coords = self._build_adj_coords(x, y)

        stack = []

        # If this space is a bomb, just say so
        if self._get_contents(x, y) == 'B':
            return 'B'

        for pair in coords:
            out_of_bounds_x = pair[0] < 0 or pair[0] >= self.width
            out_of_bounds_y = pair[1] < 0 or pair[1] >= self.height

            if out_of_bounds_x or out_of_bounds_y:
                continue

            if self._get_contents(pair[0], pair[1]) == 'B':
                count += 1

        return count

    # Build coordinates array
    def _build_adj_coords(self, x, y):
        coords = [
          [x-1, y],
          [x-1, y-1],
          [x, y-1],
          [x+1, y-1],
          [x+1, y],
          [x+1, y+1],
          [x, y+1],
          [x-1, y+1]
        ]
        return coords

    # Determine whether game has been won
    def check_for_win(self):
        if not 'E' in self.data:
            return True
        return False