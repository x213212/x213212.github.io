---
title: "mstc dqn cube"
date: "2024-11-04T03:52:00.002+08:00"
updated: "2024-11-04T03:52:28.280+08:00"
permalink: "/2024/11/mstc-dqn-cube.html"
original_url: "https://x8795278.blogspot.com/2024/11/mstc-dqn-cube.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2813459421680416599"
tags: ["cube", "mstc"]
layout: post
---

![](https://hackmd.io/_uploads/rkdZerSb1g.png)

目前重寫一下大學的專題，這次想試試看用 chatgtp-o1 寫出 8355法解出魔術方塊看多少時間，大概從颱風天到現在四天，雖然演算法速度跟以前寫得比較慢，因為以前比較像是用一些我自己的解法和8355的轉法，這次全部靠隨機的路徑和8355的一些轉法來實作，不過當初用c#寫的時間是三個月主要是從研究魔術方塊寫法和找一個unity cube 模型和理解內部原理再把想法結合進去花費時間應該不能直接做對比

首先要先實作 cube才可以來實作解法，目前跟 chatgpt o1 回答一來一往，我覺得在面對大量的不清楚需求還是有一段差距，不過如果很清楚自己的需求我覺得大致方向還是很正確 開發速度還是快非常多.

```python
import numpy as np
import copy 

# Define constants for face indices to improve code readability
FRONT = 0
BACK = 1
TOP = 2
BOTTOM = 3
LEFT = 4
RIGHT = 5

class Cube:
    def __init__(self):
        """
        Initialize the cube's state.
        Each face uses numbers 0-5 to represent different colors. There are six faces (front, back, top, bottom, left, right), each with 9 blocks.
        Uses a NumPy array to represent the cube, with each face as a one-dimensional array of length 9.
        """
        self.cube = np.array([[i] * 9 for i in range(6)])
    
    def get_column(self, face, col):
        """
        Get the specified column of a face.
        :param face: Index of the face
        :param col: Column index (0-2)
        :return: Array containing 3 elements
        """
        return self.cube[face][col::3]

    def set_column(self, face, col, values):
        """
        Set the specified column of a face.
        :param face: Index of the face
        :param col: Column index (0-2)
        :param values: Array containing 3 elements
        """
        self.cube[face][col::3] = values

    def rotate_face_clockwise(self, face):
        """
        Rotate a face clockwise by 90 degrees.
        :param face: Index of the face to rotate (0-5)
        """
        # Reshape the one-dimensional array into a 3x3 matrix
        face_matrix = self.cube[face].reshape(3, 3)
        # Use np.rot90 function to rotate, parameter -1 indicates clockwise rotation by 90 degrees
        rotated = np.rot90(face_matrix, -1)
        # Flatten the rotated matrix back to a one-dimensional array and update the face
        self.cube[face] = rotated.flatten()

    def rotate_face_counterclockwise(self, face):
        """
        Rotate a face counterclockwise by 90 degrees.
        :param face: Index of the face to rotate (0-5)
        """
        face_matrix = self.cube[face].reshape(3, 3)
        # Parameter 1 indicates counterclockwise rotation by 90 degrees
        rotated = np.rot90(face_matrix, 1)
        self.cube[face] = rotated.flatten()

    def rotate_middle_horizontal_clockwise_e_move(self):
        """
        Rotate the horizontal middle layer clockwise (E move).
        Affects the middle rows of adjacent faces (Front, Left, Back, Right).
        """
        temp = self.cube[FRONT][[5, 4, 3]].copy()
        
        # Front's middle row <- Right's middle row
        self.cube[FRONT][3:6] = self.cube[RIGHT][3:6]
        
        # Right's middle row <- Back's middle row
        self.cube[RIGHT][3:6] = self.cube[BACK][[5, 4, 3]]
        
        # Back's middle row <- Left's middle row
        self.cube[BACK][3:6] = self.cube[LEFT][3:6]
        
        # Left's middle row <- Saved Front's middle row
        self.cube[LEFT][3:6] = temp

    def rotate_middle_horizontal_counterclockwise_e_prime_move(self):
        """
        Rotate the horizontal middle layer counterclockwise (E' move).
        Affects the middle rows of adjacent faces.
        """
        temp = self.cube[FRONT][3:6].copy()
        
        # Front's middle row <- Left's middle row
        self.cube[FRONT][3:6] = self.cube[LEFT][[5, 4, 3]]
        
        # Left's middle row <- Back's middle row
        self.cube[LEFT][3:6] = self.cube[BACK][3:6]
        
        # Back's middle row <- Right's middle row
        self.cube[BACK][3:6] = self.cube[RIGHT][[5, 4, 3]]
        
        # Right's middle row <- Saved Front's middle row
        self.cube[RIGHT][3:6] = temp

    def rotate_middle_vertical_clockwise_m_move(self):
        """
        Rotate the vertical middle layer clockwise (M move).
        Affects the middle columns of adjacent faces (Front, Top, Back, Bottom).
        """
        temp = self.cube[FRONT][1::3].copy()
        
        # Front's middle column <- Bottom's middle column (reversed order)
        self.cube[FRONT][[1, 4, 7]] = self.cube[BOTTOM][[7, 4, 1]]
        
        # Bottom's middle column <- Back's middle column
        self.cube[BOTTOM][[1, 4, 7]] = self.cube[BACK][[1, 4, 7]]
        
        # Back's middle column <- Top's middle column (reversed order)
        self.cube[BACK][[1, 4, 7]] = self.cube[TOP][[7, 4, 1]]
        
        # Top's middle column <- Saved Front's middle column
        self.cube[TOP][[1, 4, 7]] = temp

    def rotate_middle_vertical_counterclockwise_m_prime_move(self):
        """
        Rotate the vertical middle layer counterclockwise (M' move).
        Affects the middle columns of adjacent faces.
        """
        temp = self.cube[FRONT][[7, 4, 1]].copy()
        
        # Front's middle column <- Top's middle column
        self.cube[FRONT][[1, 4, 7]] = self.cube[TOP][[1, 4, 7]]
        
        # Top's middle column <- Back's middle column (reversed order)
        self.cube[TOP][[1, 4, 7]] = self.cube[BACK][[7, 4, 1]]
        
        # Back's middle column <- Bottom's middle column
        self.cube[BACK][[1, 4, 7]] = self.cube[BOTTOM][[1, 4, 7]]
        
        # Bottom's middle column <- Saved Front's middle column
        self.cube[BOTTOM][[1, 4, 7]] = temp

    def rotate_any_face(self, face, direction='clockwise'):
        """
        General function to rotate any face.
        :param face: Index of the face (FRONT, BACK, TOP, BOTTOM, LEFT, RIGHT)
        :param direction: 'clockwise' or 'counterclockwise'
        """
        if(face == LEFT):
            if direction == 'clockwise':
                self.rotate_face_counterclockwise(face)
            elif direction == 'counterclockwise':
                self.rotate_face_clockwise(face)
        else: 
            if direction == 'clockwise':
                self.rotate_face_clockwise(face)
            elif direction == 'counterclockwise':
                self.rotate_face_counterclockwise(face)
            else:
                raise ValueError("Direction must be 'clockwise' or 'counterclockwise'")
            
        # Update the adjacent edges based on the rotated face
        if face == FRONT:
            self._update_adjacent_front(direction)
        elif face == BACK:
            self._update_adjacent_back(direction)
        elif face == TOP:
            self._update_adjacent_top(direction)
        elif face == BOTTOM:
            self._update_adjacent_bottom(direction)
        elif face == LEFT:
            self._update_adjacent_left(direction)
        elif face == RIGHT:
            self._update_adjacent_right(direction)
        else:
            raise ValueError("Invalid face index")

    def _update_adjacent_front(self, direction):
        """
        Update the edges of adjacent faces when the front face is rotated.
        """
        if direction == 'clockwise':
            # Save the bottom row of the top face
            temp = self.cube[TOP][[6, 7, 8]].copy()
            # Top's bottom row <- Left's right column (indices [6,3,0])
            self.cube[TOP][[6, 7, 8]] = self.cube[LEFT][[6, 3, 0]]
            # Left's right column <- Bottom's top row (indices [6,7,8])
            self.cube[LEFT][[0, 3, 6]] = self.cube[BOTTOM][[6, 7, 8]]
            # Bottom's top row <- Right's left column (indices [6,3,0])
            self.cube[BOTTOM][[6, 7, 8]] = self.cube[RIGHT][[6, 3, 0]]
            # Right's left column <- Saved Top's bottom row
            self.cube[RIGHT][[0, 3, 6]] = temp
        else:
            # Save the bottom row of the top face
            temp = self.cube[TOP][[8, 7, 6]].copy()
            # Top's bottom row <- Right's left column
            self.cube[TOP][[6, 7, 8]] = self.cube[RIGHT][[0, 3, 6]]
            # Right's left column <- Bottom's top row (indices [8,7,6])
            self.cube[RIGHT][[0, 3, 6]] = self.cube[BOTTOM][[8, 7, 6]]
            # Bottom's top row <- Left's right column
            self.cube[BOTTOM][[6, 7, 8]] = self.cube[LEFT][[0, 3, 6]]
            # Left's right column <- Saved Top's bottom row
            self.cube[LEFT][[0, 3, 6]] = temp

    def _update_adjacent_back(self, direction):
        """
        Update the edges of adjacent faces when the back face is rotated.
        """
        if direction == 'clockwise':
            # Save the top row of the top face
            temp = self.cube[TOP][[0, 1, 2]].copy()
            # Top's top row <- Left's left column (indices [8,5,2])
            self.cube[TOP][[0, 1, 2]] = self.cube[LEFT][[8, 5, 2]]
            # Left's left column <- Bottom's bottom row (indices [0,1,2])
            self.cube[LEFT][[2, 5, 8]] = self.cube[BOTTOM][[0, 1, 2]]
            # Bottom's bottom row <- Right's right column (indices [8,5,2])
            self.cube[BOTTOM][[0, 1, 2]] = self.cube[RIGHT][[8, 5, 2]]
            # Right's right column <- Saved Top's top row
            self.cube[RIGHT][[2, 5, 8]] = temp
        else:
            # Save the top row of the top face
            temp = self.cube[TOP][[2, 1, 0]].copy()
            # Top's top row <- Right's right column
            self.cube[TOP][[0, 1, 2]] = self.cube[RIGHT][[2, 5, 8]]
            # Right's right column <- Bottom's bottom row (indices [2,1,0])
            self.cube[RIGHT][[2, 5, 8]] = self.cube[BOTTOM][[2, 1, 0]]
            # Bottom's bottom row <- Left's left column
            self.cube[BOTTOM][[0, 1, 2]] = self.cube[LEFT][[2, 5, 8]]
            # Left's left column <- Saved Top's top row
            self.cube[LEFT][[2, 5, 8]] = temp

    def _update_adjacent_top(self, direction):
        """
        Update the edges of adjacent faces when the top face is rotated.
        """
        if direction == 'clockwise':
            # Save the top row of the front face
            temp = self.cube[FRONT][[2, 1, 0]].copy()
            # Front's top row <- Right's top row
            self.cube[FRONT][[0, 1, 2]] = self.cube[RIGHT][[0, 1, 2]]
            # Right's top row <- Back's top row (indices [2,1,0])
            self.cube[RIGHT][[0, 1, 2]] = self.cube[BACK][[2, 1, 0]]
            # Back's top row <- Left's top row
            self.cube[BACK][[0, 1, 2]] = self.cube[LEFT][[0, 1, 2]]
            # Left's top row <- Saved Front's top row
            self.cube[LEFT][[0, 1, 2]] = temp
        else:
            # Save the top row of the front face
            temp = self.cube[FRONT][[0, 1, 2]].copy()
            # Front's top row <- Left's top row (indices [2,1,0])
            self.cube[FRONT][[0, 1, 2]] = self.cube[LEFT][[2, 1, 0]]
            # Left's top row <- Back's top row
            self.cube[LEFT][[0, 1, 2]] = self.cube[BACK][[0, 1, 2]]
            # Back's top row <- Right's top row (indices [2,1,0])
            self.cube[BACK][[0, 1, 2]] = self.cube[RIGHT][[2, 1, 0]]
            # Right's top row <- Saved Front's top row
            self.cube[RIGHT][[0, 1, 2]] = temp

    def _update_adjacent_bottom(self, direction):
        """
        Update the edges of adjacent faces when the bottom face is rotated.
        """
        if direction == 'clockwise':
            # Save the bottom row of the front face
            temp = self.cube[FRONT][[8, 7, 6]].copy()
            # Front's bottom row <- Right's bottom row (indices [8,7,6])
            self.cube[FRONT][[6, 7, 8]] = self.cube[RIGHT][[6, 7, 8]]
            # Right's bottom row <- Back's bottom row
            self.cube[RIGHT][[6, 7, 8]] = self.cube[BACK][[8, 7, 6]]
            # Back's bottom row <- Left's bottom row (indices [8,7,6])
            self.cube[BACK][[6, 7, 8]] = self.cube[LEFT][[6, 7, 8]]
            # Left's bottom row <- Saved Front's bottom row
            self.cube[LEFT][[6, 7, 8]] = temp
        else:
            # Save the bottom row of the front face
            temp = self.cube[FRONT][[6, 7, 8]].copy()
            # Front's bottom row <- Left's bottom row
            self.cube[FRONT][[6, 7, 8]] = self.cube[LEFT][[8, 7, 6]]
            # Left's bottom row <- Back's bottom row (indices [8,7,6])
            self.cube[LEFT][[6, 7, 8]] = self.cube[BACK][[6, 7, 8]]
            # Back's bottom row <- Right's bottom row
            self.cube[BACK][[6, 7, 8]] = self.cube[RIGHT][[8, 7, 6]]
            # Right's bottom row <- Saved Front's bottom row
            self.cube[RIGHT][[6, 7, 8]] = temp

    def _update_adjacent_left(self, direction):
        """
        Update the edges of adjacent faces when the left face is rotated.
        """
        if direction == 'clockwise':
            # Save the left column of the top face (indices [0,3,6])
            temp = self.cube[TOP][[0, 3, 6]].copy()
            # Top's left column <- Back's left column (indices [6,3,0])
            self.cube[TOP][[0, 3, 6]] = self.cube[BACK][[6, 3, 0]]
            # Back's left column <- Bottom's left column (indices [0,3,6])
            self.cube[BACK][[0, 3, 6]] = self.cube[BOTTOM][[0, 3, 6]]
            # Bottom's left column <- Front's left column (indices [6,3,0])
            self.cube[BOTTOM][[0, 3, 6]] = self.cube[FRONT][[6, 3, 0]]
            # Front's left column <- Saved Top's left column
            self.cube[FRONT][[0, 3, 6]] = temp
        else:
            # Save the left column of the top face (indices [6,3,0])
            temp = self.cube[TOP][[6, 3, 0]].copy()
            # Top's left column <- Front's left column (indices [0,3,6])
            self.cube[TOP][[0, 3, 6]] = self.cube[FRONT][[0, 3, 6]]
            # Front's left column <- Bottom's left column (indices [6,3,0])
            self.cube[FRONT][[0, 3, 6]] = self.cube[BOTTOM][[6, 3, 0]]
            # Bottom's left column <- Back's left column (indices [0,3,6])
            self.cube[BOTTOM][[0, 3, 6]] = self.cube[BACK][[0, 3, 6]]
            # Back's left column <- Saved Top's left column
            self.cube[BACK][[0, 3, 6]] = temp

    def _update_adjacent_right(self, direction):
        """
        Update the edges of adjacent faces when the right face is rotated.
        """
        if direction == 'clockwise':
            # Save the right column of the top face (indices [2,5,8])
            temp = self.cube[TOP][[8, 5, 2]].copy()
            # Top's right column <- Front's right column (indices [2,5,8])
            self.cube[TOP][[2, 5, 8]] = self.cube[FRONT][[2, 5, 8]]
            # Front's right column <- Bottom's right column (indices [2,5,8])
            self.cube[FRONT][[2, 5, 8]] = self.cube[BOTTOM][[8, 5, 2]]
            # Bottom's right column <- Back's right column (indices [2,5,8])
            self.cube[BOTTOM][[2, 5, 8]] = self.cube[BACK][[2, 5, 8]]
            # Back's right column <- Saved Top's right column
            self.cube[BACK][[2, 5, 8]] = temp
        else:
            # Save the right column of the top face (indices [8,5,2])
            temp = self.cube[TOP][[2, 5, 8]].copy()
            # Top's right column <- Back's right column (indices [8,5,2])
            self.cube[TOP][[2, 5, 8]] = self.cube[BACK][[8, 5, 2]]
            # Back's right column <- Bottom's right column (indices [2,5,8])
            self.cube[BACK][[2, 5, 8]] = self.cube[BOTTOM][[2, 5, 8]]
            # Bottom's right column <- Front's right column (indices [8,5,2])
            self.cube[BOTTOM][[2, 5, 8]] = self.cube[FRONT][[8, 5, 2]]
            # Front's right column <- Saved Top's right column
            self.cube[FRONT][[2, 5, 8]] = temp

    def check_color_counts(self):
        """
        Check if the total number of each color is correct in the cube (each color should appear nine times).
        :return: Dictionary containing the count of each color on each face and overall validity.
        """
        expected_counts = {i: 9 for i in range(6)}
        actual_counts = {}
        overall_counts = {i: 0 for i in range(6)}
        for face in range(6):
            counts = {}
            for color in range(6):
                count = np.sum(self.cube[face] == color)
                counts[color] = count
                overall_counts[color] += count
            actual_counts[face] = counts
        
        valid = all(count == 9 for count in overall_counts.values())
        return {'counts': actual_counts, 'valid': valid}

    def check_corners_unique(self):
        """
        Check if all corner blocks have three different colors.
        :return: True if all corner colors are unique, otherwise False.
        """
        corners = [
            ((FRONT, 0), (TOP, 6), (LEFT, 0)),    # Front-Top-Left
            ((FRONT, 2), (TOP, 8), (RIGHT, 0)),   # Front-Top-Right
            ((FRONT, 6), (BOTTOM, 6), (LEFT, 6)), # Front-Bottom-Left
            ((FRONT, 8), (BOTTOM, 8), (RIGHT, 6)),# Front-Bottom-Right
            ((BACK, 0), (TOP, 0), (LEFT, 2)),     # Back-Top-Left
            ((BACK, 2), (TOP, 2), (RIGHT, 2)),    # Back-Top-Right
            ((BACK, 6), (BOTTOM, 0), (LEFT, 8)),  # Back-Bottom-Left
            ((BACK, 8), (BOTTOM, 2), (RIGHT, 8)), # Back-Bottom-Right
        ]

        invalid_corners = []
        # print(corners)
        for corner in corners:
            # print(corner)
            color = set()
            for x in corner:
                face, index = x 
                # print(face)
                # print(self.cube[face][index])
                color.add(self.cube[face][index])
            # print(color)
            if len(set(color)) != 3:
                invalid_corners.append(corner)
            # print(face )
            # print(index)
            # colors = [self.cube[face][index] for face, index in corner]
            # if len(set(colors)) != 3:
            #     invalid_corners.append(corner)
            #     print(corner)
            # else:
            #     print("qweqwe")
            #     print(colors)

        if invalid_corners:
            print("Corners with repeated colors found:")
            for corner in invalid_corners:
                corner_names = [self.face_name(face) for face, index in corner]
                # corner_names2 = [(face,index
                # ) for face, index in corner]
                # print(f"{f' & {corner_names2}'.join(corner_names)}")
            return False
        else:
            print("All corners have unique colors.")
            return True

    def scramble(self, moves=1000):
        print("=======")
        """
        Randomly scramble the cube.
        :param moves: Number of moves to scramble, default is 1000.
        """
        faces = [FRONT, BACK, TOP, BOTTOM, LEFT, RIGHT]
        directions = ['clockwise', 'counterclockwise']
        step = []
        for _ in range(moves):
            face = np.random.choice(faces)
            direction = np.random.choice(directions)
            self.rotate_any_face(face, direction)
            step.append((face, direction))
            # self.display()
            # if (not self.check_corners_unique()):
            #     print(face, direction)
            #     print(step)
            #     exit(-1)

    def display(self):
        """
        Display the current state of the cube in the terminal.
        The display format is as follows:
               Top
               2 2 2
               2 2 2
               2 2 2
        Left    Front   Right   Back
        4 4 4    0 0 0    5 5 5    1 1 1
        4 4 4    0 0 0    5 5 5    1 1 1
        4 4 4    0 0 0    5 5 5    1 1 1
               Bottom
               3 3 3
               3 3 3
               3 3 3
        """
        print("Current Cube State:")
        top = self.cube[TOP].reshape(3, 3)
        front = self.cube[FRONT].reshape(3, 3)
        left = self.cube[LEFT].reshape(3, 3)
        right = self.cube[RIGHT].reshape(3, 3)
        back = self.cube[BACK].reshape(3, 3)
        bottom = self.cube[BOTTOM].reshape(3, 3)
        
        # Display the top face
        print(" " * 12 + "Top")
        for row in top:
            print(" " * 12 + " ".join(map(str, row)))
        
        # Display left, front, right, back faces
        print("\nLeft    Front   Right   Back")
        for i in range(3):
            left_row = " ".join(map(str, left[i]))
            front_row = " ".join(map(str, front[i]))
            right_row = " ".join(map(str, right[i]))
            back_row = " ".join(map(str, back[i]))
            print(f"{left_row}    {front_row}    {right_row}    {back_row}")
        
        # Display the bottom face
        print("\n" + " " * 12 + "Bottom")
        for row in bottom:
            print(" " * 12 + " ".join(map(str, row)))
        print()

    def face_name(self, face):
        """
        Return the name of the face based on its index.
        """
        names = {
            FRONT: 'Front',
            BACK: 'Back',
            TOP: 'Top',
            BOTTOM: 'Bottom',
            LEFT: 'Left',
            RIGHT: 'Right'
        }
        return names.get(face, 'Unknown')

    def copy(self):
        """Create a deep copy of a Cube instance."""
        new_cube = Cube()
        new_cube.cube = self.cube.copy()
        return new_cube

# Test the Cube
if __name__ == "__main__":
    cube = Cube()
    print("Initial state:")
    cube.display()
    
    print("Rotate middle horizontal layer clockwise (E move):")
    cube.rotate_middle_horizontal_clockwise_e_move()
    cube.display()
    
    print("Rotate middle horizontal layer counterclockwise (E' move):")
    cube.rotate_middle_horizontal_counterclockwise_e_prime_move()
    cube.display()
    
    print("Rotate middle vertical layer clockwise (M move):")
    cube.rotate_middle_vertical_clockwise_m_move()
    cube.display()
    
    print("Rotate middle vertical layer counterclockwise (M' move):")
    cube.rotate_middle_vertical_counterclockwise_m_prime_move()
    cube.display()
    
    print("Rotate left face counterclockwise:")
    cube.rotate_any_face(LEFT, 'counterclockwise')
    cube.display()
    
    print("Rotate left face clockwise:")
    cube.rotate_any_face(LEFT, 'clockwise')
    cube.display()
    
    print("Rotate right face clockwise:")
    cube.rotate_any_face(RIGHT, 'clockwise')
    cube.display()
    
    print("Rotate right face counterclockwise:")
    cube.rotate_any_face(RIGHT, 'counterclockwise')
    cube.display()
    
    print("Rotate top face counterclockwise:")
    cube.rotate_any_face(TOP, 'counterclockwise')
    cube.display()
    
    print("Rotate top face clockwise:")
    cube.rotate_any_face(TOP, 'clockwise')
    cube.display()
    
    print("Rotate bottom face clockwise:")
    cube.rotate_any_face(BOTTOM, 'clockwise')
    cube.display()
    
    print("Rotate bottom face counterclockwise:")
    cube.rotate_any_face(BOTTOM, 'counterclockwise')
    cube.display()
    
    print("Rotate front face clockwise:")
    cube.rotate_any_face(FRONT, 'clockwise')
    cube.display()
    
    print("Rotate front face counterclockwise:")
    cube.rotate_any_face(FRONT, 'counterclockwise')
    cube.display()
    
    print("Rotate back face clockwise:")
    cube.rotate_any_face(BACK, 'clockwise')
    cube.display()
    
    print("Rotate back face counterclockwise:")
    cube.rotate_any_face(BACK, 'counterclockwise')
    cube.display()
    
    cube.scramble()
    
    # Add functionality to check corner block colors
    print("Check if color counts are correct:")
    color_counts = cube.check_color_counts()
    for face in range(6):
        counts = color_counts['counts'][face]
        count_str = ", ".join([f"Color {color}: {count}" for color, count in counts.items()])
        print(f"{cube.face_name(face)} Face - {count_str}")
    if color_counts['valid']:
        print("All color counts are correct (each color appears nine times).")
    else:
        print("Color distribution has errors.")
    
    print("\nCheck if all corners have unique colors:")
    cube.check_corners_unique()
    for x in range(0, 100, 1):
        cube.scramble()
        cube.check_corners_unique()

```

mtcs 當我跟他問假設我要透過dqn+mtcs去轉魔術方塊他給我是一個簡單的dqn框架，不過這時候我想先完成
mtcs 簡單版，也就是只有亂數選擇去湊到魔術方塊解完，大概想法是分層，然後每一層都有一層目標，根據之前的一些經驗然後每一層都給她限制動作，雖然這很不正統，不過沒差哈哈
後來有一個嚴重的bug，來來回回又對cube.py debug，也就是在構建旋轉的時候，left 面的順時針和逆勢針，面其實會跟其他五面相反，這部份靠後來檢查角塊的邏輯成功debug這邊也耗時一天，這邊跟大學時候寫的當然更精簡了 不過步數變太多了，因那時候算觀察，這次用隨機的想說看電腦可不可以用隨機當方式去找到最佳解。
不過最終還是有寫出來，
![image](https://hackmd.io/_uploads/rkdZerSb1g.png)

```python
import numpy as np
import random
import os 
from cube import Cube  # Ensure that your Cube class is in cube.py file
import copy 
import random
# Define face index constants for better readability
FRONT = 0
BACK = 1
TOP = 2
BOTTOM = 3
LEFT = 4
RIGHT = 5
MIDC = 6
MIDCO = 7

class StringState:
    def __init__(self):
        self.cube = Cube()  # Create a Cube instance
        self.cube.scramble(moves=300)  # Randomly scramble the cube
        self.initial_state = copy.deepcopy(self.cube.cube)
        self.goal_phase = 0  # Goal phase marker, 1 represents cross, 2 represents corners
    
    def copy(self):
        """ 
        Create a deep copy of the current state.
        """
        return copy.deepcopy(self)
    
    def is_goal(self):
        # Check goals based on the current phase
        if self.goal_phase == 0:
            return True
        elif self.goal_phase == 1:
            return (self.cube.cube[LEFT][7] == 4 and 
                    self.cube.cube[BOTTOM][3] == 3 and 
                    self.cube.cube[FRONT][7] == 0 and 
                    self.cube.cube[BOTTOM][7] == 3)
        elif self.goal_phase == 2:
            
            return (
                (self.cube.cube[LEFT][7] == 4 and self.cube.cube[BOTTOM][3] == 3) and 
                (
                    (self.cube.cube[RIGHT][7] == 5 and self.cube.cube[BOTTOM][5] == 3) or  
                    (self.cube.cube[RIGHT][3] == 5 and self.cube.cube[FRONT][5] == 3) or  
                    (self.cube.cube[RIGHT][1] == 5 and self.cube.cube[TOP][5] == 3) or  
                    (self.cube.cube[RIGHT][5] == 5 and self.cube.cube[BACK][5] == 3) or
                    (self.cube.cube[RIGHT][7] == 3 and self.cube.cube[BOTTOM][5] == 5) or  
                    (self.cube.cube[RIGHT][3] == 3 and self.cube.cube[FRONT][5] == 5) or  
                    (self.cube.cube[RIGHT][1] == 3 and self.cube.cube[TOP][5] == 5) or  
                    (self.cube.cube[RIGHT][5] == 3 and self.cube.cube[BACK][5] == 5)
                )
            )
        elif self.goal_phase == 3:
            return (self.cube.cube[RIGHT][7] == 5 and 
                    self.cube.cube[BOTTOM][5] == 3 and 
                    self.cube.cube[BACK][7] == 1 and 
                    self.cube.cube[BOTTOM][5] == 3)
        elif self.goal_phase == 4:
            return (
                self.cube.cube[BACK][7] == 1 and 
                self.cube.cube[BOTTOM][1] == 3 and 
                self.cube.cube[RIGHT][7] == 5 and 
                self.cube.cube[BOTTOM][5] == 3 and 
                self.cube.cube[LEFT][7] == 4 and 
                self.cube.cube[BOTTOM][3] == 3 and
                self.cube.cube[FRONT][7] == 0 and 
                self.cube.cube[BOTTOM][7] == 3
            )
        elif self.goal_phase == 5:
            return (
                self.cube.cube[BOTTOM][6] == 3 and 
                self.cube.cube[LEFT][6] == 4 and 
                self.cube.cube[FRONT][6] == 0
            )
        elif self.goal_phase == 6:
            return (
                self.cube.cube[BOTTOM][6] == 3 and 
                self.cube.cube[LEFT][6] == 4 and 
                self.cube.cube[FRONT][6] == 0 and
                self.cube.cube[BOTTOM][0] == 3 and 
                self.cube.cube[LEFT][8] == 4 and 
                self.cube.cube[BACK][6] == 1
            )
        elif self.goal_phase == 7:
            
            return (
                self.cube.cube[BOTTOM][6] == 3 and 
                self.cube.cube[LEFT][6] == 4 and 
                self.cube.cube[FRONT][6] == 0 and
                self.cube.cube[BOTTOM][0] == 3 and 
                self.cube.cube[LEFT][8] == 4 and 
                self.cube.cube[BACK][6] == 1 and
                self.cube.cube[BOTTOM][2] == BOTTOM and 
                self.cube.cube[RIGHT][8] == RIGHT and 
                self.cube.cube[BACK][8] == BACK 
            )
        elif self.goal_phase == 8:
            return (
                self.cube.cube[LEFT][4] == LEFT and self.cube.cube[FRONT][4] == FRONT and self.cube.cube[BACK][4] == BACK and self.cube.cube[RIGHT][4] == RIGHT
                and
                (self.cube.cube[LEFT][3] == LEFT and 
                self.cube.cube[FRONT][3] == FRONT) and
                (self.cube.cube[LEFT][5] == LEFT and 
                self.cube.cube[BACK][3] == BACK) and
                (self.cube.cube[RIGHT][5] == RIGHT and 
                self.cube.cube[BACK][5] == BACK) 
            )
        elif self.goal_phase == 9:
            return (
                (self.cube.cube[TOP][7] == TOP and self.cube.cube[FRONT][1] == FRONT) and
                (self.cube.cube[TOP][3] == TOP and self.cube.cube[LEFT][1] == LEFT) and 
                (self.cube.cube[TOP][1] == TOP and self.cube.cube[BACK][1] == BACK) and 
                (self.cube.cube[TOP][5] == TOP and self.cube.cube[RIGHT][1] == RIGHT)
            )
        elif self.goal_phase == 10:
            self.cube.display()
            return (
                (self.cube.cube[FRONT][2] == FRONT and self.cube.cube[TOP][8] == TOP and self.cube.cube[RIGHT][0] == RIGHT)and
                (self.cube.cube[FRONT][0] == FRONT and self.cube.cube[TOP][6] == TOP and self.cube.cube[LEFT][0] == LEFT) 
                and
                (self.cube.cube[BACK][0] == BACK and self.cube.cube[TOP][0] == TOP and self.cube.cube[LEFT][2] == LEFT) 
                and
                (self.cube.cube[BACK][2] == BACK and self.cube.cube[TOP][2] == TOP and self.cube.cube[RIGHT][2] == RIGHT) 
                and   (self.cube.cube[BOTTOM][0] == BOTTOM) and (self.cube.cube[BOTTOM][2] == BOTTOM) and (self.cube.cube[BOTTOM][6] == BOTTOM) 
                          and 
                  (self.cube.cube[TOP][7] == TOP and self.cube.cube[FRONT][1] == FRONT) and
                (self.cube.cube[TOP][3] == TOP and self.cube.cube[LEFT][1] == LEFT) and 
                (self.cube.cube[TOP][1] == TOP and self.cube.cube[BACK][1] == BACK) and 
                (self.cube.cube[TOP][5] == TOP and self.cube.cube[RIGHT][1] == RIGHT)
            )
    def get_possible_actions(self):
        actions = []
        if self.goal_phase == 0 or self.goal_phase == 1:
            faces = [FRONT, BACK, TOP, BOTTOM, LEFT, RIGHT]
            directions = ['clockwise', 'counterclockwise']
            for face in faces:
                for direction in directions:
                    actions.append((face, direction))
        elif self.goal_phase == 2:
            actions.extend([
                (LEFT, 'clockwise'),
                (RIGHT, 'clockwise'),
                (TOP, 'clockwise'),
                (BACK, 'clockwise')
            ])
        elif self.goal_phase == 3:
            actions.extend([
                (TOP, 'clockwise'), 
                (BACK, 'clockwise'),
                (RIGHT, 'clockwise')
            ])
        elif self.goal_phase == 4:
            actions.extend([
                (TOP, 'clockwise'), 
                (BACK, 'counterclockwise'),
                (LEFT, 'clockwise'), 
                (LEFT, 'counterclockwise'), 
                (LEFT, 'clockwise'), 
                (LEFT, 'counterclockwise')
            ])
        elif self.goal_phase == 5:
            actions.extend([
                [(RIGHT, 'clockwise'), (TOP, 'clockwise'), (RIGHT, 'counterclockwise')],
                [(RIGHT, 'counterclockwise'), (TOP, 'clockwise'), (RIGHT, 'clockwise')],
                [(LEFT, 'clockwise'), (TOP, 'clockwise'), (LEFT, 'counterclockwise')],
                [(LEFT, 'counterclockwise'), (TOP, 'clockwise'), (LEFT, 'clockwise')],
                [(FRONT, 'clockwise'), (TOP, 'clockwise'), (FRONT, 'counterclockwise')],
                [(BACK, 'clockwise'), (TOP, 'clockwise'), (BACK, 'counterclockwise')]
            ])
        elif self.goal_phase == 6:
            actions.extend([
                [(RIGHT, 'clockwise'), (TOP, 'clockwise'), (RIGHT, 'counterclockwise')],
                [(RIGHT, 'counterclockwise'), (TOP, 'clockwise'), (RIGHT, 'clockwise')],
                [(LEFT, 'counterclockwise'), (TOP, 'clockwise'), (LEFT, 'clockwise')],
                [(BACK, 'clockwise'), (TOP, 'clockwise'), (BACK, 'counterclockwise')],
                [(BACK, 'counterclockwise'), (TOP, 'clockwise'), (BACK, 'clockwise')]
            ])
        elif self.goal_phase == 7:
            actions.extend([
                [(RIGHT, 'clockwise'), (TOP, 'clockwise'), (RIGHT, 'counterclockwise')],
                [(RIGHT, 'clockwise'), (TOP, 'clockwise'),(TOP, 'clockwise'), (RIGHT, 'counterclockwise')],
                [(RIGHT, 'clockwise'), (TOP, 'counterclockwise'), (TOP, 'counterclockwise'),(RIGHT, 'counterclockwise')],
                [(BACK, 'counterclockwise'), (TOP, 'clockwise'), (BACK, 'clockwise')],
                [(BACK, 'counterclockwise'), (TOP, 'clockwise'), (TOP, 'clockwise'), (BACK, 'clockwise')],
                [(BACK, 'counterclockwise'), (TOP, 'counterclockwise'), (TOP, 'counterclockwise'), (BACK, 'clockwise')]
            ])  
        elif self.goal_phase == 8:
            insert_sequence = [
                (MIDC, 'clockwise') ,
                (TOP, 'clockwise'), 
                (RIGHT, 'clockwise'), 
                (TOP, 'counterclockwise'), 
                (RIGHT, 'counterclockwise'), 
                (TOP, 'counterclockwise'), 
                (FRONT, 'counterclockwise'), 
                (TOP, 'clockwise'), 
                (FRONT, 'clockwise'),
                (MIDC, 'counterclockwise') 
        
            ]

            insert_inverse_sequence = [
                (MIDC, 'clockwise') ,
                (FRONT, 'counterclockwise'), 
                (TOP, 'clockwise'), 
                (FRONT, 'clockwise'), 
                (TOP, 'counterclockwise'), 
                (RIGHT, 'clockwise'), 
                (TOP, 'counterclockwise'), 
                (RIGHT, 'counterclockwise'), 
                (TOP, 'clockwise'),
                (MIDC, 'counterclockwise') 
      
            ]
            actions.extend([ 
                (MIDC, 'clockwise') ,
                insert_sequence,
                insert_inverse_sequence
            ])
        elif self.goal_phase == 9:
            actions.extend([ (TOP, 'clockwise'),
                [(RIGHT, 'clockwise'), (TOP, 'clockwise'), (RIGHT, 'counterclockwise')],
                [(FRONT, 'counterclockwise'), (TOP, 'clockwise'), (FRONT, 'clockwise')]
            ])
        elif self.goal_phase == 10:
            actions.extend([ 
                (TOP, 'counterclockwise'),
                [(RIGHT, 'counterclockwise'), (BOTTOM, 'clockwise'), (RIGHT, 'clockwise'), (BOTTOM, 'counterclockwise')],
            ])
        # elif self.goal_phase == 11:
        #     actions.extend([ 
        #          (TOP, 'clockwise'),
        #          [(RIGHT, 'counterclockwise'), (BOTTOM, 'clockwise'), (RIGHT, 'clockwise'), (BOTTOM, 'counterclockwise')],
        #     ])
    
        return actions

    def check_gos(self):
        # Advance to the next goal phase if the current phase is achieved
        if self.is_goal():
            self.goal_phase += 1
    
    def perform_action(self, action):
        if isinstance(action, list):
            for move in action:
                face, direction = move
                if face == MIDC:
                    self.cube.rotate_middle_horizontal_clockwise_e_move()
                elif face == MIDCO:
                    self.cube.rotate_middle_horizontal_counterclockwise_e_prime_move()
                else:
                    self.cube.rotate_any_face(face, direction)
              
        else:
            face, direction = action
            if face == MIDC:
                self.cube.rotate_middle_horizontal_clockwise_e_move()
            elif face == MIDCO:
                self.cube.rotate_middle_horizontal_counterclockwise_e_prime_move()
            else:
                self.cube.rotate_any_face(face, direction)
           
        self.check_gos()
        return self  # Return itself to support chaining

def mcts_search(root, max_iterations, simulation_depth):
    best_action_sequence = []
    best_distance = float('inf')
    
    all_step = []
    for iteration in range(max_iterations):
        state = root
        # state = root
        action_sequence = []
        distance = 0
        
        for _ in range(simulation_depth):
            actions = state.get_possible_actions()
            if actions:  # If there are available actions
                action = random.choice(actions)
                state = state.perform_action(action)
                action_sequence.append(action)
               
                distance += 1
            else:  # If there are no available actions, it means completed
                break

        if state.is_goal():
            state.cube.display()
            
            if distance < best_distance:
                best_action_sequence = action_sequence
                best_distance = distance
            
            all_step.extend(action_sequence)
            
            
            return all_step
        elif distance < best_distance:
            best_action_sequence = action_sequence
            best_distance = distance

        all_step.extend(action_sequence)
    return all_step

# Test MCTS with Cube
initial_state = StringState()  # Initial state is Cube
max_iterations = 1000000  
simulation_depth = 300

# Display the scrambled cube
initial_state.cube.display()

# Search for the best solution
best_action_sequence = mcts_search(initial_state, max_iterations, simulation_depth)

initial_state.cube.cube = copy.deepcopy(initial_state.initial_state)
for action in best_action_sequence:
    initial_state.perform_action(action)

print(f"Number of actions in the best sequence: {len(best_action_sequence)}")
initial_state.cube.display()  # Display the current cube state

```

哈哈本來想讓dqn 去學習8355,這邊實驗下來整個還是被tune 壞，可能設計上還是有點問題，不過大致想法就是讓他學習在某個state 的 array 可以映射到 某種狀態選擇某種動作的東西    
```python
import numpy as np
import random
import os
import copy
from collections import deque
import torch
import torch.nn as nn
import torch.optim as optim
from cube import Cube  # 確保Cube類在cube.py文件中

# 定義面索引常數
FRONT = 0
BACK = 1
TOP = 2
BOTTOM = 3
LEFT = 4
RIGHT = 5
MIDC = 6
MIDCO = 7

# 定義動作空間
# 定義動作空間
ACTIONS = []
DIRECTIONS = ['clockwise', 'counterclockwise']
for face in [FRONT, BACK, TOP, BOTTOM, LEFT, RIGHT, MIDC, MIDCO]:  # 包含 MIDC 和 MIDCO
    for direction in DIRECTIONS:
        ACTIONS.append((face, direction))

# MIDC和MIDCO也作為特殊動作
ACTIONS.append((MIDC, 'clockwise'))
ACTIONS.append((MIDCO, 'counterclockwise'))
COMBO_ACTIONS_MAP = {
    "C1": [(RIGHT, 'clockwise'), (TOP, 'clockwise'), (RIGHT, 'counterclockwise')],
    "C2": [(RIGHT, 'counterclockwise'), (TOP, 'clockwise'), (RIGHT, 'clockwise')],
    "C3": [(LEFT, 'clockwise'), (TOP, 'clockwise'), (LEFT, 'counterclockwise')],
    "C4": [(LEFT, 'counterclockwise'), (TOP, 'clockwise'), (LEFT, 'clockwise')],
    "C5": [(FRONT, 'clockwise'), (TOP, 'clockwise'), (FRONT, 'counterclockwise')],
    "C6": [(BACK, 'clockwise'), (TOP, 'clockwise'), (BACK, 'counterclockwise')],
    "C7": [(RIGHT, 'clockwise'), (TOP, 'clockwise'), (TOP, 'clockwise'), (RIGHT, 'counterclockwise')],
    "C8": [(RIGHT, 'clockwise'), (TOP, 'counterclockwise'), (TOP, 'counterclockwise'), (RIGHT, 'counterclockwise')],
    "C9": [(BACK, 'counterclockwise'), (TOP, 'clockwise'), (BACK, 'clockwise')],
    "C10": [(BACK, 'counterclockwise'), (TOP, 'clockwise'), (TOP, 'clockwise'), (BACK, 'clockwise')],
    "C11": [(BACK, 'counterclockwise'), (TOP, 'counterclockwise'), (TOP, 'counterclockwise'), (BACK, 'clockwise')],
    "C12": [(MIDC, 'clockwise'), (TOP, 'clockwise'), (RIGHT, 'clockwise'), (TOP, 'counterclockwise'),
            (RIGHT, 'counterclockwise'), (TOP, 'counterclockwise'), (FRONT, 'counterclockwise'),
            (TOP, 'clockwise'), (FRONT, 'clockwise'), (MIDC, 'counterclockwise')],
    "C13": [(MIDC, 'clockwise'), (FRONT, 'counterclockwise'), (TOP, 'clockwise'), (FRONT, 'clockwise'),
            (TOP, 'counterclockwise'), (RIGHT, 'clockwise'), (TOP, 'counterclockwise'),
            (RIGHT, 'counterclockwise'), (TOP, 'clockwise'), (MIDC, 'counterclockwise')],
    "C14": [(RIGHT, 'counterclockwise'), (BOTTOM, 'clockwise'), (RIGHT, 'clockwise'), (BOTTOM, 'counterclockwise')]
}
# 添加組合動作的符號到 ACTIONS
ACTIONS.extend(COMBO_ACTIONS_MAP.keys())
ACTION_SIZE = len(ACTIONS)

# DQN模型
class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, output_dim)
        )
    
    def forward(self, x):
        return self.fc(x)

# 定義StringState類
class StringState:
    def __init__(self):
        self.cube = Cube()  # 創建Cube實例
        self.cube.scramble(moves=30)  # 隨機打亂魔方，您可以調整打亂步數
        self.initial_state = copy.deepcopy(self.cube.cube)
        self.goal_phase = 0  # 目標階段標記，0代表初始階段

    def copy(self):
        """創建當前狀態的深拷貝"""
        return copy.deepcopy(self)

    def get_possible_actions(self):
        actions = []
        if self.goal_phase == 0 or self.goal_phase == 1:
            faces = [FRONT, BACK, TOP, BOTTOM, LEFT, RIGHT]
            directions = ['clockwise', 'counterclockwise']
            for face in faces:
                for direction in directions:
                    actions.append((face, direction))
        elif self.goal_phase == 2:
            actions.extend([
                (LEFT, 'clockwise'),
                (RIGHT, 'clockwise'),
                (TOP, 'clockwise'),
                (BACK, 'clockwise')
            ])
        elif self.goal_phase == 3:
            actions.extend([
                (TOP, 'clockwise'), 
                (BACK, 'clockwise'),
                (RIGHT, 'clockwise')
            ])
        elif self.goal_phase == 4:
            actions.extend([
                (TOP, 'clockwise'), 
                (BACK, 'counterclockwise'),
                (LEFT, 'clockwise'), 
                (LEFT, 'counterclockwise')
            ])
        elif self.goal_phase == 5:
            actions.extend(["C1", "C2", "C3", "C4", "C5", "C6"])
        elif self.goal_phase == 6:
            actions.extend(["C1", "C2", "C3", "C4", "C5", "C6"])
        elif self.goal_phase == 7:
            actions.extend(["C1", "C7", "C8", "C9", "C10", "C11"])
        elif self.goal_phase == 8:
            actions.extend(["C12", "C13"])
        elif self.goal_phase == 9:
            actions.extend([
                (TOP, 'clockwise'),
                "C1", "C5"
            ])
        elif self.goal_phase == 10:
            actions.extend([
                (TOP, 'counterclockwise'),
                "C14"
            ])
        return actions

    def is_goal(self):
        # 根據當前階段檢查目標
        if self.goal_phase == 0:
            return True
        elif self.goal_phase == 1:
            return (self.cube.cube[LEFT][7] == 4 and 
                    self.cube.cube[BOTTOM][3] == 3 and 
                    self.cube.cube[FRONT][7] == 0 and 
                    self.cube.cube[BOTTOM][7] == 3)
        elif self.goal_phase == 2:
            return (
                (self.cube.cube[LEFT][7] == 4 and self.cube.cube[BOTTOM][3] == 3) and 
                (
                    (self.cube.cube[RIGHT][7] == 5 and self.cube.cube[BOTTOM][5] == 3) or  
                    (self.cube.cube[RIGHT][3] == 5 and self.cube.cube[FRONT][5] == 3) or  
                    (self.cube.cube[RIGHT][1] == 5 and self.cube.cube[TOP][5] == 3) or  
                    (self.cube.cube[RIGHT][5] == 5 and self.cube.cube[BACK][5] == 3) or
                    (self.cube.cube[RIGHT][7] == 3 and self.cube.cube[BOTTOM][5] == 5) or  
                    (self.cube.cube[RIGHT][3] == 3 and self.cube.cube[FRONT][5] == 5) or  
                    (self.cube.cube[RIGHT][1] == 3 and self.cube.cube[TOP][5] == 5) or  
                    (self.cube.cube[RIGHT][5] == 3 and self.cube.cube[BACK][5] == 5)
                )
            )
        elif self.goal_phase == 3:
            return (self.cube.cube[RIGHT][7] == 5 and 
                    self.cube.cube[BOTTOM][5] == 3 and 
                    self.cube.cube[BACK][7] == 1 and 
                    self.cube.cube[BOTTOM][5] == 3)
        elif self.goal_phase == 4:
            return (
                self.cube.cube[BACK][7] == 1 and 
                self.cube.cube[BOTTOM][1] == 3 and 
                self.cube.cube[RIGHT][7] == 5 and 
                self.cube.cube[BOTTOM][5] == 3 and 
                self.cube.cube[LEFT][7] == 4 and 
                self.cube.cube[BOTTOM][3] == 3 and
                self.cube.cube[FRONT][7] == 0 and 
                self.cube.cube[BOTTOM][7] == 3
            )
        elif self.goal_phase == 5:
            return (
                self.cube.cube[BOTTOM][6] == 3 and 
                self.cube.cube[LEFT][6] == 4 and 
                self.cube.cube[FRONT][6] == 0
            )
        elif self.goal_phase == 6:
            return (
                self.cube.cube[BOTTOM][6] == 3 and 
                self.cube.cube[LEFT][6] == 4 and 
                self.cube.cube[FRONT][6] == 0 and
                self.cube.cube[BOTTOM][0] == 3 and 
                self.cube.cube[LEFT][8] == 4 and 
                self.cube.cube[BACK][6] == 1
            )
        elif self.goal_phase == 7:
            return (
                self.cube.cube[BOTTOM][6] == 3 and 
                self.cube.cube[LEFT][6] == 4 and 
                self.cube.cube[FRONT][6] == 0 and
                self.cube.cube[BOTTOM][0] == 3 and 
                self.cube.cube[LEFT][8] == 4 and 
                self.cube.cube[BACK][6] == 1 and
                self.cube.cube[BOTTOM][2] == BOTTOM and 
                self.cube.cube[RIGHT][8] == RIGHT and 
                self.cube.cube[BACK][8] == BACK 
            )
        elif self.goal_phase == 8:
            return (
                self.cube.cube[LEFT][4] == LEFT and self.cube.cube[FRONT][4] == FRONT and self.cube.cube[BACK][4] == BACK and self.cube.cube[RIGHT][4] == RIGHT
                and
                (self.cube.cube[LEFT][3] == LEFT and 
                self.cube.cube[FRONT][3] == FRONT) and
                (self.cube.cube[LEFT][5] == LEFT and 
                self.cube.cube[BACK][3] == BACK) and
                (self.cube.cube[RIGHT][5] == RIGHT and 
                self.cube.cube[BACK][5] == BACK) 
            )
        elif self.goal_phase == 9:
            return (
                (self.cube.cube[TOP][7] == TOP and self.cube.cube[FRONT][1] == FRONT) and
                (self.cube.cube[TOP][3] == TOP and self.cube.cube[LEFT][1] == LEFT) and 
                (self.cube.cube[TOP][1] == TOP and self.cube.cube[BACK][1] == BACK) and 
                (self.cube.cube[TOP][5] == TOP and self.cube.cube[RIGHT][1] == RIGHT)
            )
        elif self.goal_phase == 10:
            self.cube.display()
            return (
                (self.cube.cube[FRONT][2] == FRONT and self.cube.cube[TOP][8] == TOP and self.cube.cube[RIGHT][0] == RIGHT) and
                (self.cube.cube[FRONT][0] == FRONT and self.cube.cube[TOP][6] == TOP and self.cube.cube[LEFT][0] == LEFT) and
                (self.cube.cube[BACK][0] == BACK and self.cube.cube[TOP][0] == TOP and self.cube.cube[LEFT][2] == LEFT) and
                (self.cube.cube[BACK][2] == BACK and self.cube.cube[TOP][2] == TOP and self.cube.cube[RIGHT][2] == RIGHT) and
                (self.cube.cube[BOTTOM][0] == BOTTOM) and 
                (self.cube.cube[BOTTOM][2] == BOTTOM) and 
                (self.cube.cube[BOTTOM][6] == BOTTOM) and 
                (self.cube.cube[TOP][7] == TOP and self.cube.cube[FRONT][1] == FRONT) and
                (self.cube.cube[TOP][3] == TOP and self.cube.cube[LEFT][1] == LEFT) and 
                (self.cube.cube[TOP][1] == TOP and self.cube.cube[BACK][1] == BACK) and 
                (self.cube.cube[TOP][5] == TOP and self.cube.cube[RIGHT][1] == RIGHT)
            )
        else:
            return False  # 如果超出定義的階段
    def check_gos(self):
        """如果達到當前階段的目標，進入下一階段"""
        if self.is_goal():
            self.goal_phase += 1

    def perform_action(self, action):
        """執行一個動作"""
        if action in COMBO_ACTIONS_MAP:
            # 如果動作是組合動作符號，則執行對應的動作序列
            for move in COMBO_ACTIONS_MAP[action]:
                face, direction = move
                # 確保方向符合預期值
                if direction not in ['clockwise', 'counterclockwise']:
                    raise ValueError(f"無效的方向: {direction}. 必須是 'clockwise' 或 'counterclockwise'")
                if face == MIDC:
                    self.cube.rotate_middle_horizontal_clockwise_e_move()
                elif face == MIDCO:
                    self.cube.rotate_middle_horizontal_counterclockwise_e_prime_move()
                else:
                    self.cube.rotate_any_face(face, direction)
        elif isinstance(action, tuple) and len(action) == 2:
            # 處理單一的 (face, direction) 動作
            face, direction = action
            # 確保方向符合預期值
            if direction not in ['clockwise', 'counterclockwise']:
                raise ValueError(f"無效的方向: {direction}. 必須是 'clockwise' 或 'counterclockwise'")
            if face == MIDC:
                if direction == 'clockwise':
                    self.cube.rotate_middle_horizontal_clockwise_e_move()
                elif direction == 'counterclockwise':
                    self.cube.rotate_middle_horizontal_counterclockwise_e_prime_move()
            elif face == MIDCO:
                if direction == 'clockwise':
                    self.cube.rotate_middle_horizontal_clockwise_e_move()
                elif direction == 'counterclockwise':
                    self.cube.rotate_middle_horizontal_counterclockwise_e_prime_move()
            else:
                self.cube.rotate_any_face(face, direction)
        else:
            raise ValueError(f"無效的動作格式: {action}")

        self.check_gos()
        return self  # 支持鏈式調用

    def get_state_vector(self):
        """將魔方狀態轉換為數值向量"""
        # 假設魔方有6個面，每個面9個方塊，每個方塊用一個數字表示顏色
        # 這裡將每個方塊的顏色編碼為一個數字
        # 您需要根據您的Cube類實現調整此方法
        state_vector = []
        for face in range(6):
            state_vector.extend(self.cube.cube[face])
        return np.array(state_vector, dtype=np.float32)

# DQN代理
class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size  # 輸入維度
        self.action_size = action_size  # 動作空間大小
        self.memory = deque(maxlen=200000)
        self.gamma = 0.99    # 折扣因子
        self.epsilon = 1.0   # 探索率
        self.epsilon_min = 0.4
        self.epsilon_decay = 0.9999
        self.learning_rate = 1e-4
        self.batch_size = 32
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.policy_net = DQN(state_size, action_size).to(self.device)
        self.target_net = DQN(state_size, action_size).to(self.device)
        self.update_target_network()
        
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.learning_rate)
        self.loss_fn = nn.MSELoss()
    
    def update_target_network(self):
        self.target_net.load_state_dict(self.policy_net.state_dict())
    
    def remember(self, state, action, reward, next_state, done):
        """存儲經驗"""
        self.memory.append((state, action, reward, next_state, done))
    def act(self, state, possible_actions):
        """選擇動作"""
        if np.random.rand() <= self.epsilon:
            # 隨機選擇一個可行動作
            return random.choice(possible_actions)

        # 將狀態轉換為張量並傳遞給設備
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)

        with torch.no_grad():
            q_values = self.policy_net(state_tensor)[0]  # 保留在設備上

        # 提前建立一個動作索引的查找表
        action_to_index = {action: idx for idx, action in enumerate(ACTIONS)}

        # 將可行動作的索引提取出來
        action_indices = [action_to_index[a] for a in possible_actions]

        # 篩選出可行動作的 Q 值
        q_values_filtered = q_values[action_indices]

        # 選擇 Q 值最高的可行動作
        best_action_idx_in_filtered = torch.argmax(q_values_filtered).item()  # 保持在 PyTorch 張量內
        best_action = possible_actions[best_action_idx_in_filtered]
        return best_action

    
    def replay(self):
        """經驗回放與訓練"""
        if len(self.memory) < self.batch_size:
            return
        minibatch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*minibatch)
        
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor([ACTIONS.index(a) for a in actions]).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor(rewards).unsqueeze(1).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).unsqueeze(1).to(self.device)
        
        # 計算當前Q值
        current_q = self.policy_net(states).gather(1, actions)
        # 計算目標Q值
        with torch.no_grad():
            max_next_q = self.target_net(next_states).max(1)[0].unsqueeze(1)
            target_q = rewards + (self.gamma * max_next_q * (1 - dones))
        
        # 計算損失
        loss = self.loss_fn(current_q, target_q)
        
        # 優化
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # 更新探索率
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

# 環境步進函數
def step(state_obj, action,phs):
    """執行一個動作，返回下一狀態、獎勵和完成標記"""
    next_state_obj = state_obj.copy()
    next_state_obj.perform_action(action)
    next_state_vector = next_state_obj.get_state_vector()
    done = next_state_obj.is_goal()
    
    if done:
        reward = 100+(phs + 1)*200 # 達到目標的獎勵
    else:
        reward = -0.1  # 每一步的代價
    
    return next_state_obj, reward, done

# 訓練DQN
def train_dqn(episodes=10000, target_update=1000, model_path=None, start_episode=1):
    state_size = 54  # 假設每個方塊用一個整數表示，6面*9個方塊
    action_size = ACTION_SIZE
    agent = DQNAgent(state_size, action_size)
    
    # 加載之前保存的模型（如果提供了 model_path）
    # if model_path:
    #     agent.policy_net.load_state_dict(torch.load(model_path))
    #     print(f"已加載模型: {model_path}")
    
    total_steps = 0
    for e in range(start_episode, episodes + 1):
        state_obj = StringState()
        state = state_obj.get_state_vector()
        done = False
        total_reward = 0
        steps = 0
        
        while  steps < 1000:  # 限制每個回合的最大步數
            possible_actions = state_obj.get_possible_actions()
            if not possible_actions:
                break  # 沒有可行動作，結束回合
            action = agent.act(state, possible_actions)
            next_state_obj, reward, done = step(state_obj, action,state_obj.goal_phase )
            next_state = next_state_obj.get_state_vector()
            agent.remember(state, action, reward, next_state, done)
            agent.replay()
            state_obj = next_state_obj
            state = next_state
            steps += 1
            total_reward += reward 
            total_steps += 1
            if(steps% 100 == 0):
                print(f"訓練中 ..{steps} 步內, 走到最遠目標 {state_obj.goal_phase}")
        
        # 每隔 target_update 回合更新目標網絡
        if e % target_update == 0:
            agent.update_target_network()
            print(f"更新目標網絡在回合 {e}")
        if done:
            print(f"{steps} 步內, 走到最遠目標 {state_obj.goal_phase}")
        
        print(f"回合 {e}/{episodes}, 步數: {steps}, 總獎勵: {total_reward}, 探索率: {agent.epsilon:.4f}")
        
        # 可選：每隔一定回合保存模型
        if e % 1000 == 0:
            torch.save(agent.policy_net.state_dict(), f"dqn_cube_solver_{e}.pth")
            print(f"模型已保存: dqn_cube_solver_{e}.pth")
    
    # 保存訓練好的模型
    torch.save(agent.policy_net.state_dict(), "dqn_cube_solver_final.pth")
    print("訓練完成，最終模型已保存。")

# 評估DQN
def evaluate_dqn(model_path, episodes=100):
    state_size = 54
    action_size = ACTION_SIZE
    agent = DQNAgent(state_size, action_size)
    agent.policy_net.load_state_dict(torch.load(model_path, map_location=agent.device))
    agent.epsilon = 0.3  # 禁用探索
    
    success = 0
    total_steps = 0
    for e in range(1, episodes + 1):
        state_obj = StringState()
        state = state_obj.get_state_vector()
        done = False
        steps = 0
        
        while  steps < 300000:
            possible_actions = state_obj.get_possible_actions()
            if not possible_actions:
                break  # 沒有可行動作，結束回合
            action = agent.act(state, possible_actions)
            next_state_obj, reward, done = step(state_obj, action, state_obj.goal_phase)
            state = next_state_obj.get_state_vector()
            state_obj = next_state_obj
            steps += 1
            print(state_obj.goal_phase, steps)
        
        if done:
            success += 1
            print(f"回合 {e}/{episodes}: 在 {steps} 步內解決魔方。")
        else:
            print(f"回合 {e}/{episodes}: 未在步數限制內解決魔方。")
        total_steps += steps
    
    print(f"成功率: {success}/{episodes}")
    print(f"平均步數: {total_steps / episodes}")

# 主函數
if __name__ == "__main__":
    # 開始訓練
    
    train_dqn(episodes=100000, target_update=5, model_path="dqn_cube_solver_final.pth", start_episode=5750)

    
    # 訓練完成後，可以進行評估
    # evaluate_dqn("dqn_cube_solver_16000.pth", episodes=16000)

```

後續有分析再繼續往這邊擴充dqn

```python
# cube_env.py
import numpy as np
import gym
from gym import spaces
from cube import Cube  # Ensure that your Cube class is in cube.py file
from mcts_solver import StringState, mcts_search  # Import MCTS-related classes and functions

# Define face index constants for better readability
FRONT = 0
BACK = 1
TOP = 2
BOTTOM = 3
LEFT = 4
RIGHT = 5
MIDC = 6
MIDCO = 7

class CubeEnv(gym.Env):
    """
    Custom Rubik's Cube environment for solving one face using hierarchical MCTS.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, verbose=False):
        super(CubeEnv, self).__init__()

        self.target_face = FRONT
        self.action_list = [
            ('rotate_any_face', FRONT, 'clockwise'),        # 0
            ('rotate_any_face', FRONT, 'counterclockwise'), # 1
            ('rotate_any_face', BACK, 'clockwise'),         # 2
            ('rotate_any_face', BACK, 'counterclockwise'),  # 3
            ('rotate_any_face', TOP, 'clockwise'),          # 4
            ('rotate_any_face', TOP, 'counterclockwise'),   # 5
            ('rotate_any_face', BOTTOM, 'clockwise'),       # 6
            ('rotate_any_face', BOTTOM, 'counterclockwise'),# 7
            ('rotate_any_face', LEFT, 'clockwise'),         # 8
            ('rotate_any_face', LEFT, 'counterclockwise'),  # 9
            ('rotate_any_face', RIGHT, 'clockwise'),        # 10
            ('rotate_any_face', RIGHT, 'counterclockwise')  # 11
        ]

        self.action_space = spaces.Discrete(len(self.action_list))
        self.observation_space = spaces.Box(low=0.0, high=5.0, shape=(6, 3, 3), dtype=np.float32)
        self.cube = Cube()
        self.max_steps = 100
        self.current_step = 0
        self.solved = False
        self.correct_edges = set()
        self.correct_corners = set()
        self.verbose = verbose
        self.prev_dominant_count = self._get_dominant_color_count()
        
        # Initialize MCTS-related variables
        self.mcts_root = StringState()
        self.mcts_max_iterations = 1000
        self.mcts_simulation_depth = 100

    def _execute_action(self, action_info):
        """ Execute the specified action """
        method_name = action_info[0]
        method = getattr(self.cube, method_name)
        if len(action_info) == 3:
            face = action_info[1]
            direction = action_info[2]
            method(face, direction)
        else:
            method()

    def step(self, action):
        # Execute the action
        action_info = self.action_list[action]
        self._execute_action(action_info)

        self.current_step += 1
        reward = self._compute_reward()
        done = self.solved or self.current_step >= self.max_steps

        if done:
            reward += self._compute_final_reward()
            if self.verbose:
                self._display_target_face()

        state = self._get_state()
        info = {}  # Remove known state recommendation actions

        return state, reward, done, info

    def reset(self):
        self.cube = Cube()
        for _ in range(50):
            action = self.action_space.sample()
            action_info = self.action_list[action]
            self._execute_action(action_info)
        self.current_step = 0
        self.solved = False
        self.correct_edges = set()
        self.correct_corners = set()
        self.prev_dominant_count = self._get_dominant_color_count()
        
        # Reset MCTS root node
        self.mcts_root = StringState()
        
        return self._get_state()

    def render(self, mode='human'):
        self._display_target_face()

    def close(self):
        pass

    def _get_state(self):
        return self.cube.cube.reshape(6, 3, 3).astype(np.float32)

    def _compute_reward(self):
        face_colors = self.cube.cube[self.target_face]
        center_color = face_colors[4]
        reward = 0.0

        edge_indices = [1, 3, 5, 7]
        for idx in edge_indices:
            if face_colors[idx] == center_color and idx not in self.correct_edges:
                self.correct_edges.add(idx)
                reward += 5

        corner_indices = [0, 2, 6, 8]
        for idx in corner_indices:
            if face_colors[idx] == center_color and idx not in self.correct_corners:
                self.correct_corners.add(idx)
                reward += 2.5

        step_penalty = -0.1  # Penalty for each step to encourage shorter solutions
        reward += step_penalty

        if len(self.correct_edges) == 4 and len(self.correct_corners) == 4:
            if all(face_colors[idx] == center_color for idx in edge_indices + corner_indices):
                reward += 10 + ((self.max_steps - self.current_step) * 0.1)
                self.solved = True

        return reward

    def _compute_final_reward(self):
        face_colors = self.cube.cube[self.target_face]
        center_color = face_colors[4]
        matching_count = np.sum(face_colors == center_color)
        return matching_count * 0.2

    def _get_dominant_color_count(self):
        face_colors = self.cube.cube[self.target_face]
        center_color = face_colors[4]
        return np.sum(face_colors == center_color)

    def _display_target_face(self):
        self.cube.display()

    def get_available_actions(self, state):
        """
        Temporarily remove action pruning, return all available actions
        """
        return list(range(len(self.action_list)))

    def get_mcts_action_sequence(self):
        """
        Use MCTS to search for the best action sequence based on the current goal phase.
        """
        best_action_sequence = mcts_search(
            root=self.mcts_root,
            max_iterations=self.mcts_max_iterations,
            simulation_depth=self.mcts_simulation_depth
        )
        return best_action_sequence

```
train dqn
```python
import gym
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
import torch
import torch.nn as nn
from cube_env import CubeEnv  # 导入我们自定义的环境

# 自定义 CNN + Transformer 特征提取器
class CubeAttentionCNN(BaseFeaturesExtractor):
    def __init__(self, observation_space: gym.spaces.Box, features_dim: int = 256):
        super(CubeAttentionCNN, self).__init__(observation_space, features_dim)
        n_input_channels = observation_space.shape[0]  # 应该是 6

        # CNN 部分：提取初始空间特征
        self.cnn = nn.Sequential(
            nn.Conv2d(n_input_channels, 64, kernel_size=2, stride=1),
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=2, stride=1),
            nn.ReLU(),
            nn.Flatten(),
        )

        # 计算卷积输出的维度
        with torch.no_grad():
            sample_input = torch.zeros(1, n_input_channels, 3, 3)
            n_flatten = self.cnn(sample_input).shape[1]

        # 自注意力层：用于跨面注意力
        self.attention = nn.MultiheadAttention(embed_dim=n_flatten, num_heads=4, batch_first=True)

        # 最终特征提取线性层
        self.linear = nn.Sequential(
            nn.Linear(n_flatten, features_dim),
            nn.ReLU(),
        )

    def forward(self, observations):
        # CNN 提取特征
        x = observations.float()
        x = self.cnn(x)  # Shape: [batch_size, n_flatten]

        # 将 CNN 提取的特征用于注意力层
        x = x.unsqueeze(1)  # 调整维度以适配注意力机制 (batch_size, seq_len=1, embed_dim)
        attn_output, _ = self.attention(x, x, x)  # 自注意力机制应用
        attn_output = attn_output.squeeze(1)  # 移除多余的维度

        # 全连接层输出
        x = self.linear(attn_output)
        return x

# 创建环境
env = CubeEnv()

# 定义政策参数，使用自定义的注意力 CNN 特征提取器
policy_kwargs = dict(
    features_extractor_class=CubeAttentionCNN,
    features_extractor_kwargs=dict(features_dim=128),
)

# 创建 PPO 智能体，指定使用 GPU
model = PPO(
    'CnnPolicy',
    env,
    verbose=1,
    learning_rate=2.5e-4,
    batch_size=64,
    n_epochs=50,
    gamma=0.99,
    gae_lambda=0.95,
    clip_range=0.2,
    policy_kwargs=policy_kwargs,
    tensorboard_log="./tensorboard_logs/",
    device='cuda'
)

# 可选：创建评估回调
eval_env = CubeEnv()
eval_callback = EvalCallback(
    eval_env,
    best_model_save_path='./logs/',
    log_path='./logs/',
    eval_freq=5000,
    deterministic=True,
    render=False
)

# 训练智能体
model.learn(total_timesteps=500000, callback=eval_callback)

# 保存模型
model.save("cube_attention_ppo_model")

```
```
tensorboard --logdir=./tensorboard_logs/
```

![image](https://hackmd.io/_uploads/rkVo3OSZ1e.png)

