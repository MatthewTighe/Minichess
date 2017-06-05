package com.small314;

import java.util.HashMap;

/**
 * The representation of a square of the board.
 */
public class Square {
    public int x, y;

    public Square(int startX, int startY) {
        x = startX;
        y = startY;
    }

    public String toStr() {
        HashMap<Integer, String> INT_TO_FILES = new HashMap<>();
        INT_TO_FILES.put(0, "a");
        INT_TO_FILES.put(1, "b");
        INT_TO_FILES.put(2, "c");
        INT_TO_FILES.put(3, "d");
        INT_TO_FILES.put(4, "e");
        return INT_TO_FILES.get(this.y) + Integer.toString(State.NROWS - this.x);
    }
}
