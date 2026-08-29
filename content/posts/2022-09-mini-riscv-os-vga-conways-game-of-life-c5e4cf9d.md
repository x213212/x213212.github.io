---
title: "mini-riscv-os vga Conway’s Game of Life"
date: "2022-09-30T00:00:00.007+08:00"
updated: "2022-09-30T13:34:36.771+08:00"
permalink: "/2022/09/mini-riscv-os-vga-conways-game-of-life.html"
original_url: "https://x8795278.blogspot.com/2022/09/mini-riscv-os-vga-conways-game-of-life.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-842397528815130884"
tags: ["Conway’s Game of Life"]
layout: post
---

![](https://i.imgur.com/meQQr1N.gif)

# mini-riscv-os vga Conway's Game of Life
前面作者實現了碎形圖
https://zh.wikipedia.org/wiki/%E5%88%86%E5%BD%A2
那我們就來在上面實現一個生命遊戲
https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life
https://github.com/alnvdl/Life
這是一個簡單的c 生命遊戲可以觀察每一個步驟，我們目前專案，還沒實現動態分配記憶體，contex switch 好像也沒保存記憶體狀態，我們直接把專案中的array 改為 靜態宣告
https://www.geeksforgeeks.org/dynamically-allocate-2d-array-c/

```c
#include "os.h"
#include <stdio.h>
#include <stdlib.h>
//#include<string.h>

#define WIDTH 250
#define HEIGHT 200
#define ACTIVE 1
#define INACTIVE 0
#define ACTIVE_SYMBOL '*'
#define INACTIVE_SYMBOL ' '
int *arr[320*200];
void *next[320*200];
void *memset(void *dst, int c, size_t n)
{
	char *q = dst;
	char *end = q + n;
	for (;;)
	{
		if (q >= end)
			break;
		*q++ = (char)c;
		if (q >= end)
			break;
		*q++ = (char)c;
		if (q >= end)
			break;
		*q++ = (char)c;
		if (q >= end)
			break;
		*q++ = (char)c;
	}
	return dst;
}
int count_neighbors(int *board, int x, int y)
{
	/*
	Counts the number os neighbors for a given cell.
		board: the board
		x: the cell's horizontal coordinate
		y: the cell's vertical coordinate
	*/

	int i, j, count = 0;

	for (i = -1; i <= 1; i++)
		for (j = -1; j <= 1; j++)
			if (!(i == 0 && j == 0) &&
				(x + i >= 0 && x + i < WIDTH) &&
				(y + j >= 0 && y + j < HEIGHT) &&
				(board[(x + i) * WIDTH + (y + j)] == ACTIVE))
				count++;
	return count;
}

int count_active(int *board)
{
	/*
	Counts the number os active cells on the board.
		board: the board
	*/
	int i, j, count = 0;

	for (i = 0; i < WIDTH; i++)
		for (j = 0; j < HEIGHT; j++)
			if (board[i * WIDTH + j] == ACTIVE)
				count++;

	return count;
}

void iter_cell(int *board, int *next, int x, int y)
{
	/*
	Sets the state of the cell based on the game rules.
		board: the curent iteration board
		next: the next iteration board
		x: the cell's horizontal coordinate
		y: the cell's vertical coordinate
	*/
	int current_state = board[x * WIDTH + y];
	int n_neighbors = count_neighbors(board, x, y);

	if (current_state == ACTIVE && n_neighbors < 2)
		next[x * WIDTH + y] = INACTIVE;
	else if (current_state == ACTIVE && n_neighbors > 3)
		next[x * WIDTH + y] = INACTIVE;
	else if (current_state == ACTIVE && (n_neighbors == 2 || n_neighbors == 3))
		next[x * WIDTH + y] = ACTIVE;
	else if (current_state == INACTIVE && n_neighbors == 3)
		next[x * WIDTH + y] = ACTIVE;
	else
		next[x * WIDTH + y] = INACTIVE;
}

void init_board(int *arr)
{
	/*
	Initializes the board cells to a inactive state.
		board: the curent iteration board
	*/

	for (int i = 0; i < WIDTH ; i++)
	{
		for (int j = 0; j < HEIGHT; j++)
			// lib_printf("%d ", arr[i * y + j]);
			arr[i * WIDTH + j] = 0;
		// lib_printf("\n");
	}
}

void copy_board(int *source, int *destination)
{
	/*
	Copies the a source board cells to a destination board.
		source: the source board
		destination: the destination board
	*/

	for (int i = 0; i < WIDTH ; i++)
		for (int j = 0; j < HEIGHT; j++)
			destination[i * WIDTH + j] = source[i * WIDTH + j];
}

void next_iteration(int *arr)
{
	/*
	Iterates the given board to its next state.
		board: the curent iteration board
	*/
	// x*y
	//void *next[WIDTH * HEIGHT];
	init_board(next);

	for (int i = 0; i < WIDTH; i++)
		for (int j = 0; j < HEIGHT; j++)
			iter_cell(arr, next, i, j);
	copy_board(next, arr);
}

void print_board(int *arr)
{
	/*
	Outputs the board.
		board: the board
	*/

	for (int i = 0; i < WIDTH; i++)
	{
		for (int j = 0; j < HEIGHT; j++)
		{
			if (arr[i * WIDTH + j] == INACTIVE)
				putpixel(i, j, 0x000000);
			// printf("%c ", INACTIVE_SYMBOL);
			else
				putpixel(i, j, 0x0000ff);
			// printf("%c ", ACTIVE_SYMBOL);
		}
		//  printf("\n");
	}
}

void system_clear()
{
	/*
	Clears the output.
	FIXME: not portable
	*/
	//    system("clear");

	for (int i = 0; i < WIDTH; i++)
		for (int j = 0; j < HEIGHT; j++)
		{
			putpixel(i, j, 0x000000);
		}
}

void redraw(int *arr, char *shell, int gen_count,
			int active_count)
{
	/*
	Redraws the content of the game.
		board: the board to print
		shell: the message to ask for input
		gen_count: generation (iteration) count
		active_count: the number of active cells
	*/
	system_clear();
	// printf("\n%d generations; %d active cells (%dx%d board)\n", gen_count,
	// active_count,
	//                                                               WIDTH, HEIGHT);

	print_board(arr);
	// printf("%s: ", shell);
}

void show_help()
{
}

void show_cell_info(int board[HEIGHT][WIDTH], int x, int y)
{
	int internal_x = (HEIGHT - y), internal_y = (x - 1);
}

void user_task0(void)
{

	lib_puts("Task0: Created!\n");
	lib_puts("Task0: Now, return to kernel mode\n");
	os_kernel();

	while (1)
	{
		lib_puts("Task0: Running...\n");
		lib_delay(10);
		os_kernel();
	}
}

void user_task1(void)
{

	lib_puts("Task1: Created!\n");
	lib_puts("Task1: Now, return to kernel mode\n");
	os_kernel();

	int x =HEIGHT, y =  WIDTH;

	int gen_count = 0, active_count = 0;

	init_board(arr);
	for (int i = 0 ; i <x ; i++)
		for (int j = 0 ; j <y ; j++){
		if((i* y )%2 == 0)
			arr[i* y + j] = 1;
		if((j*x*y*i )%2 == 2)
			arr[i* y + j] = 1;
	}
				
	arr[20 * y + 20] = 1;
	arr[21 * y + 19] = 1;
	arr[20 * y + 18] = 1;
	arr[21 * y + 18] = 1;
	arr[19 * y + 18] = 1;

	arr[20 * y + 20] = 1;
	arr[21 * y + 19] = 1;
	arr[20 * y + 18] = 1;
	arr[21 * y + 18] = 1;
	arr[19 * y + 18] = 1;

	arr[12 * y + 16] = 1;
	arr[13 * y + 16] = 1;
	arr[14 * y + 16] = 1;

	arr[10 * y + 14] = 1;
	arr[10 * y + 13] = 1;
	arr[10 * y + 12] = 1;

	arr[15 * y + 14] = 1;
	arr[15 * y + 13] = 1;
	arr[15 * y + 12] = 1;

	arr[12 * y + 11] = 1;
	arr[13 * y + 11] = 1;
	arr[14 * y + 11] = 1;

	arr[18 * y + 11] = 1;
	arr[19 * y + 11] = 1;
	arr[20 * y + 11] = 1;

	arr[17 * y + 14] = 1;
	arr[17 * y + 13] = 1;
	arr[17 * y + 12] = 1;

	arr[22 * y + 14] = 1;
	arr[22 * y + 13] = 1;
	arr[22 * y + 12] = 1;

	arr[18 * y + 11] = 1;
	arr[18 * y + 11] = 1;
	arr[18 * y + 11] = 1;

	arr[12 * y + 9] = 1;
	arr[13 * y + 9] = 1;
	arr[14 * y + 9] = 1;

	arr[10 * y + 8] = 1;
	arr[10 * y + 7] = 1;
	arr[10 * y + 6] = 1;

	arr[15 * y + 8] = 1;
	arr[15 * y + 7] = 1;
	arr[15 * y + 6] = 1;

	arr[12 * y + 4] = 1;
	arr[13 * y + 4] = 1;
	arr[14 * y + 4] = 1;

	arr[18 * y + 9] = 1;
	arr[19 * y + 9] = 1;
	arr[20 * y + 9] = 1;

	arr[17 * y + 8] = 1;
	arr[17 * y + 7] = 1;
	arr[17 * y + 6] = 1;

	arr[22 * y + 8] = 1;
	arr[22 * y + 7] = 1;
	arr[22 * y + 6] = 1;

	arr[18 * y + 4] = 1;
	arr[19 * y + 4] = 1;
	arr[20 * y + 4] = 1;
	redraw(arr, "x,y", gen_count, active_count);
	next_iteration(arr);

	// redraw(arr, "x,y", gen_count, active_count);
	// next_iteration(arr);

	while (1)
	{

		lib_puts("Task1: Running...\n");
		lib_delay(10);
		// os_kernel();
		redraw(arr, "x,y", gen_count, active_count);
		next_iteration(arr);
		// next_iteration(board);
		// active_count = count_active(board);
		// gen_count++;
	}
}

void user_init()
{
	task_create(&user_task0);
	task_create(&user_task1);
}

```

生命遊戲有一個太空船和作者給的範例test case，我們把它直接轉為array
現在我們直接就在這個os上實現一個生命遊戲!
https://gist.github.com/x213212/a16312fb476427a14cb63e6484b31ae5
![](https://i.imgur.com/NLA5GAz.gif)

改個解析度

![](https://i.imgur.com/meQQr1N.gif)

