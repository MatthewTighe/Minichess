package com.small314;

import java.util.ArrayList;

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
