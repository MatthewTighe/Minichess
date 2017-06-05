package com.small314;

import java.util.ArrayList;

/**
 * Player that uses alpha-beta search to decide on its move.
 * @param dpth Depth to which the player will search.
 */
public class AlphaBetaPlayer extends Player {
    private int depth;

    public AlphaBetaPlayer(String color, int dpth) { super(color); depth = dpth; }

    public Move makeMove() {
        ArrayList<Move> moves = MoveGenerator.findMoves(posn);
        Move move = posn.alphaBetaMove(depth, moves);
        posn.makeMove(move);
        return move;
    }
}
