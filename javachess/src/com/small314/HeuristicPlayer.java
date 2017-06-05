package com.small314;

import java.util.ArrayList;

/**
 * A heuristic player that chooses the best move based on the board state.
 */
public class HeuristicPlayer extends Player {

    public HeuristicPlayer(String color) { super(color); }

    public Move makeMove() {
        ArrayList<Move> moves = MoveGenerator.findMoves(posn);
        ArrayList<Integer> scores = new ArrayList<>();
        for(int i = 0; i < moves.size(); i++) {
            Move move = moves.get(i);
            Undo undo = new Undo(posn.board, move);
            posn.makeMove(move);
            scores.add(posn.computeScore());
            posn.doUndo(undo);
        }

        int max = Integer.MIN_VALUE;
        int index = -1;
        for(int i = 0; i < scores.size(); i++)
            if(scores.get(i) > max) index = i;
        assert(index != -1);
        posn.makeMove(moves.get(index));
        return moves.get(index);
    }
}
