package com.small314;

/**
 * Every player will get moves the same, as the String version of the move.
 * Making moves is dependent on the type of player, so that function is abstracted.
 */
public abstract class Player {
    public State posn;

    public Player(String color) {
        posn = new State(color);
    }

    public abstract Move makeMove();

    public void getMove(String mv) {
        Move move = new Move(mv);
        posn.makeMove(move);
    }
}