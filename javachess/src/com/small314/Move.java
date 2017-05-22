package com.small314;

import java.util.HashMap;

public class Move {
    public Square from, to;
    public boolean win;

    public Move(Square from, Square to) {
        this.from = from;
        this.to = to;
        this.win = false;
    }


    public Move(String move) {
        HashMap<String, Integer> FILES_TO_INT = new HashMap<>();
        FILES_TO_INT.put("a", 0);
        FILES_TO_INT.put("b", 1);
        FILES_TO_INT.put("c", 2);
        FILES_TO_INT.put("d", 3);
        FILES_TO_INT.put("e", 4);

        from = new Square(Math.abs(Character.getNumericValue(move.charAt(1)) - State.NROWS),
                FILES_TO_INT.get(String.valueOf(move.charAt(0))));
        to = new Square(Math.abs(Character.getNumericValue(move.charAt(4)) - State.NROWS),
                FILES_TO_INT.get(String.valueOf(move.charAt(3))));
    }

    public void setWin() {
        win = true;
    }

    public String toStr() {
        return this.from.toStr() + "-" + this.to.toStr();
    }
}
