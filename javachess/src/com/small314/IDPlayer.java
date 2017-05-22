package com.small314;

import java.util.ArrayList;

public class IDPlayer extends Player {
    private boolean useAdjusted = false;
    private double limit;

    public IDPlayer(String color, double lmt) {
        super(color);
        if(lmt == 0) {
            useAdjusted = true;
            limit = determineTime();
        }
    }

    public Move makeMove() {
        ArrayList<Move> moves = MoveGenerator.findMoves(posn);
        if(useAdjusted) limit = determineTime();
        Move move = posn.iterativeDeepening(limit, moves);
        posn.makeMove(move);
        return move;
    }

    private int determineTime() {
        if(posn.ply / 2 < 5) return 1;
        if(posn.ply / 2 < 10) return 2;
        if(posn.ply / 2 < 35) return 10;
        else return 4;
    }
}
