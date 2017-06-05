package com.small314;

import java.util.ArrayList;

/**
 * A player that chooses moves based on the results of a negamax search.
 * @param dpth The depth to which the search is executed.
 */
public class NegamaxPlayer extends Player {
    private int depth;

    public NegamaxPlayer(String color, int dpth) { super(color); depth = dpth; }

    public Move makeMove() {
        ArrayList<Move> moves = MoveGenerator.findMoves(posn);
        Move move = posn.negamaxMove(depth, moves);
        posn.makeMove(move);
        return move;
    }
}
