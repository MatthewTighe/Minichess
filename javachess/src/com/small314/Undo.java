package com.small314;

/**
 * All the information necessary to undo a move.
 */
public class Undo {
    int startx;
    int starty;
    int endx;
    int endy;
    char startPiece;
    char endPiece;

    public Undo(char[][] board, Move move) {
        startx = move.from.x;
        starty = move.from.y;
        endx = move.to.x;
        endy = move.to.y;
        startPiece = board[startx][starty];
        endPiece = board[endx][endy];
    }
}
