package com.small314;

import java.util.ArrayList;
import java.util.concurrent.ThreadLocalRandom;

public class RandomPlayer extends Player {
    public RandomPlayer(String color) { super(color); }

    public Move makeMove() {
        ArrayList<Move> moves = MoveGenerator.findMoves(posn);
        Move move = moves.get(ThreadLocalRandom.current().nextInt(0, moves.size()));
        posn.makeMove(move);
        return move;
    }
}
