package com.small314;

import java.util.ArrayList;

public class MoveGenerator {
    static int YES = 0;
    static int NO = 1;
    static int ONLY = 2;

    // Scan the board in specified direction until a piece is encountered or until
    // stopShort becomes true.
    public static ArrayList<Move> movescan(int x0, int y0, int dx, int dy,
                             State posn, int capture, boolean stopShort) {
        int x = x0;
        int y = y0;
        String c = posn.pieceColor(x, y);
        assert(posn.board[x][y] != '.');

        ArrayList<Move> moves = new ArrayList<>();
        while(true) {
            x = x + dx;
            y = y + dy;
            if(x >= State.NROWS || y >= State.NCOLS || x < 0 || y < 0) break;
            if(posn.board[x][y] != '.') {
                if(posn.pieceColor(x, y).equals(c)) break;
                if(capture == NO) break;
                stopShort = true;
            }
            else if(capture == ONLY) break;
            moves.add(new Move(new Square(x0, y0), new Square(x, y)));
            if(stopShort) break;
        }
        return moves;
    }

    // Rotate the direction of movement so that pieces can scan in all possible
    // directions.
    public static ArrayList<Move> symmscan(int x, int y, int dx, int dy,
                             State posn, int capture, boolean stopShort) {
        ArrayList<Move> moves = new ArrayList<>();
        for(int i = 0; i < 4; i++) {
            moves.addAll(movescan(x, y, dx, dy, posn, capture, stopShort));
            int tmp = dx;
            dx = dy;
            dy = tmp;
            dx *= -1;
        }
        return moves;
    }

    // Generated moves for all piece types.
    public static ArrayList<Move> movelist(int x, int y, State posn) {
        assert(posn.board[x][y] != '.');
        ArrayList<Move> moves = new ArrayList<>();
        char kind = Character.toUpperCase(posn.board[x][y]);
        boolean stopShort;
        switch(kind) {
            case 'K':
            case 'Q':
                stopShort = (kind == 'K');
                moves.addAll(symmscan(x, y, 1, 0, posn, YES, stopShort));
                moves.addAll(symmscan(x, y, 1, 1, posn, YES, stopShort));
                break;
            case 'B':
            case 'R':
                stopShort = (kind == 'B');
                int capture = (kind == 'R') ? YES : NO;
                moves.addAll(symmscan(x, y, 1, 0, posn, capture, stopShort));
                if (kind == 'B') {
                    capture = YES;
                    moves.addAll(symmscan(x, y, 1, 1, posn, capture, false));
                }
                break;
            case 'N':
                moves.addAll(symmscan(x, y, 2, 1, posn, YES, true));
                moves.addAll(symmscan(x, y, 2, -1, posn, YES, true));
                break;
            case 'P':
                // Move toward 0 if white, 5 if black
                int d = ("W".equals(posn.onMove)) ? -1 : 1;
                moves.addAll(movescan(x, y, d, -1, posn, ONLY, true));
                moves.addAll(movescan(x, y, d, 1, posn, ONLY, true));
                moves.addAll(movescan(x, y, d, 0, posn, NO, true));
                break;
        }
        return moves;
    }

    // Find each piece for the player on move, then generate all their moves.
    public static ArrayList<Move> findMoves(State posn) {
        ArrayList<Integer> xs = new ArrayList<>();
        ArrayList<Integer> ys = new ArrayList<>();
        for(int i = 0; i < State.NROWS; i++) {
            for(int j = 0; j < State.NCOLS; j++) {
                if(posn.board[i][j] == '.') continue;
                else if("W".equals(posn.onMove) && Character.isUpperCase(posn.board[i][j])) {
                    xs.add(i);
                    ys.add(j);
                }
                else if("B".equals(posn.onMove) && Character.isLowerCase(posn.board[i][j])) {
                    xs.add(i);
                    ys.add(j);
                }
            }
        }
        assert(xs.size() == ys.size());
        ArrayList<Move> moves = new ArrayList<>();
        for(int i = 0; i < xs.size(); i++) {
            moves.addAll(movelist(xs.get(i), ys.get(i), posn));
        }
        return moves;
    }
}
