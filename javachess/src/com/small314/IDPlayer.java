package com.small314;

import java.util.ArrayList;

/**
 * A player that does iterative deepening search.
 * @param lmt Time limit in seconds that the player will continue
 *            searching. If 0, it will adjust its time limit as the game
 *            continues.
 */
public class IDPlayer extends Player {
    private boolean useAdjusted = false;
    private double limit;

    public IDPlayer(String color, double lmt) {
        super(color);
        if(lmt == 0) 
            useAdjusted = true;
        else
            limit = lmt;
    }

    public Move makeMove() {
        ArrayList<Move> moves = MoveGenerator.findMoves(posn);
        if(useAdjusted) limit = determineTime();
        Move move = posn.iterativeDeepening(limit, moves);
        posn.makeMove(move);
        return move;
    }

    /**
     * Determines the amount of time to use at this point in the game.
     */
    private int determineTime() {
        if(posn.ply / 2 < 5) return 1;
        if(posn.ply / 2 < 10) return 2;
        if(posn.ply / 2 < 30) return 9;
        else return 4;
    }
}
