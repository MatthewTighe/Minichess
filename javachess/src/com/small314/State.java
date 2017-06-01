package com.small314;

import java.util.ArrayList;

public class State {
    public static int NROWS = 6;
    public static int NCOLS = 5;

    public static int MAX_SCORE = 10000;
    public static int MIN_SCORE = -10000;

    public char board[][];
    public String color;
    public String onMove;
    public int ply;
    public ArrayList<Character> wPieces;
    public ArrayList<Character> bPieces;


    // Constructor. Always starts on white, since black should receive a move before
    // making one.
    public State(String clr) {
        board = new char[][] {
                {'k', 'q', 'b', 'n', 'r'},
                {'p', 'p', 'p', 'p', 'p'},
                {'.', '.', '.', '.', '.'},
                {'.', '.', '.', '.', '.'},
                {'P', 'P', 'P', 'P', 'P'},
                {'R', 'N', 'B', 'Q', 'K'}
        };

        char[] pieces = new char[] {'K', 'Q', 'B', 'N', 'R', 'P', 'P', 'P', 'P', 'P'};
        wPieces = new ArrayList<>();
        bPieces = new ArrayList<>();
        for(int i=0; i < pieces.length; i++) {
            wPieces.add(pieces[i]);
            bPieces.add(Character.toLowerCase(pieces[i]));
        }

        color = clr;
        onMove = "W";
        ply = 0;
    }

    // Get the next player on move.
    String flip(String current) {
        if ("W".equals(current))
            return "B";
        return "W";
    }

    // Get the color of a piece. Used in move generation.
    String pieceColor(int x, int y) {
        assert(board[x][y] != '.');
        if(Character.isLowerCase(board[x][y])) return "B";
        return "W";
    }

    // Get the board state as a string.
    public String getBoardString() {
        String builder = "";
            for(int i = 0; i < board.length; i++) {
                for(int j = 0; j < board[i].length; j++) {
                    builder += String.valueOf(board[i][j]);
                }
                builder += "\n";
            }
        return builder;
    }

    // Build the rest of the position.
    public String getPosnString() {
        return onMove + " " + String.valueOf(ply/2) + "\n" + getBoardString();
    }


    // Move a piece, being sure to remove pieces from the piece list, and do promotion.
    void makeMove(Move move) {

        char piece = board[move.from.x][move.from.y];
        assert(piece != '.');

        board[move.from.x][move.from.y] = '.';

        char captured = board[move.to.x][move.to.y];
        if(captured != '.') {
            if(Character.toUpperCase(captured) == 'K') move.setWin();
            if(Character.isLowerCase(captured)) bPieces.remove(Character.valueOf(captured));
            else wPieces.remove(Character.valueOf(captured));
        }

        board[move.to.x][move.to.y] = piece;

        doPromotion(move.to.x, move.to.y);

        onMove = flip(onMove);
        ply += 1;
    }

    // Undo a move, being sure to add pieces back to list, and undo promotion.
    void doUndo(Undo undo) {
        assert(undo != null);
        assert(undo.startPiece != '.');

        board[undo.startx][undo.starty] = undo.startPiece;
        board[undo.endx][undo.endy] = undo.endPiece;

        if(undo.endPiece != '.') {
            if(Character.isLowerCase(undo.endPiece)) bPieces.add(undo.endPiece);
            else wPieces.add(undo.endPiece);
        }

        if(Character.toUpperCase(undo.startPiece) == 'P') {
            if(undo.endx == 0) {
                wPieces.remove(Character.valueOf('Q'));
                wPieces.add('P');
            }
            else if (undo.endx == 5) {
                bPieces.remove(Character.valueOf('q'));
                bPieces.add('p');
            }
        }

        ply -= 1;
        onMove = flip(onMove);
    }

    // Check if the game is over.
    boolean checkEnd() {
        if(ply / 2 == 40) return true;
        if(!wPieces.contains('K')) return true;
        if(!bPieces.contains('k')) return true;
        return false;
    }

    // Score possible moves using the negamax algorithm, and return the best.
    Move negamaxMove(int depth, ArrayList<Move> moves) {
        long time = System.currentTimeMillis();
        ArrayList<Integer> scores = new ArrayList<>();
        for(int i = 0; i < moves.size(); i++) {
            Move move = moves.get(i);
            Undo undo = new Undo(board, move);
            makeMove(move);
            scores.add(-(negamax(depth-1)));
            doUndo(undo);
        }
        int max = Integer.MIN_VALUE;
        int index = -1;
        for(int i = 0; i < scores.size(); i++) {
            int score = scores.get(i);
            if(score > max) {
                index = i;
                max = score;
            }
        }
        assert(index != -1);
        return moves.get(index);
    }

    // Recursively compute scores using negamax algorithm.
    int negamax(int depth) {
        if(checkEnd() || depth <= 0) return computeScore();

        ArrayList<Move> moves = MoveGenerator.findMoves(this);
        int max = Integer.MIN_VALUE;
        for(int i = 0; i < moves.size(); i++) {
            Move move = moves.get(i);
            Undo undo = new Undo(board, move);
            makeMove(move);
            int val = -(negamax(depth - 1));
            if(val > max) max = val;
            doUndo(undo);
        }
        assert(max != Integer.MIN_VALUE);
        return max;
    }

    // Score moves based on negamax algorithm, with added alpha-beta pruning.
    Move alphaBetaMove(int depth, ArrayList<Move> moves) {
        ArrayList<Integer> scores = new ArrayList<>();
        int alpha = Integer.MAX_VALUE;
        for(int i = 0; i < moves.size(); i++) {
            Move move = moves.get(i);
            Undo undo = new Undo(board, move);
            makeMove(move);
            int score = -(alphaBeta(depth-1, -alpha, Integer.MAX_VALUE));
            alpha = Math.max(alpha, score);
            scores.add(score);
            doUndo(undo);
        }
        int max = Integer.MIN_VALUE;
        int index = -1;
        for(int i = 0; i < scores.size(); i++) {
            int score = scores.get(i);
            if (score > max) {
                max = score;
                index = i;
            }
        }
        assert(index != -1);
        return moves.get(index);
    }

    // Recursively compute scores to depth or game over.
    int alphaBeta(int depth, int alpha, int beta) {
        if(checkEnd() || depth <= 0)
            return computeScore();

        ArrayList<Move> moves = MoveGenerator.findMoves(this);

        Move move = moves.get(0);
        moves.remove(0);
        Undo undo = new Undo(board, move);
        makeMove(move);
        int val_prime = -(alphaBeta(depth - 1, -beta, -alpha));
        doUndo(undo);
        if(val_prime >= beta) {
            return val_prime;
        }
        alpha = Math.max(val_prime, alpha);
        for(int i = 0; i < moves.size(); i++) {
            move = moves.get(i);
            undo = new Undo(board, move);
            makeMove(move);
            int val = -(alphaBeta(depth - 1, -beta, -alpha));
            doUndo(undo);
            if(val >= beta) {
                return val;
            }
            val_prime = Math.max(val, val_prime);
            alpha = Math.max(alpha, val);
        }

        return val_prime;
    }

    Move iterativeDeepening(double limit, ArrayList<Move> moves) {
        long start = System.currentTimeMillis();
        int depth = 1;
        int max_score = Integer.MIN_VALUE;
        int idx = -1;
        ArrayList<Integer> scores = new ArrayList<>();
        for(int i = 0; i < moves.size(); i++) {
            Move move = moves.get(i);
            Undo undo = new Undo(board, move);

            makeMove(move);
            int score = -(alphaBeta(depth, -Integer.MAX_VALUE, Integer.MAX_VALUE));
            if(score > max_score) {
                max_score = score;
                idx = i;
            }
            doUndo(undo);
        }
        Move curr_move = moves.get(idx);
        while(depth < 40) {
            depth++;

            max_score = Integer.MIN_VALUE;
            idx = -1;
            for(int i = 0; i < moves.size(); i++) {
                Move move = moves.get(i);

                if(System.currentTimeMillis() - start > limit * 1000)
                    return curr_move;
                Undo undo = new Undo(board, move);
                makeMove(move);
                
                if(move.win) {
                    doUndo(undo);
                    return move;
                }

                if("W".equals(onMove) &&  !wPieces.contains('K')) {
                    doUndo(undo);
                    return curr_move;
                }
                else if("B".equals(onMove) &&  !wPieces.contains('k')) {
                    doUndo(undo);
                    return curr_move;
                }

                int score = -(alphaBeta(depth, -Integer.MAX_VALUE, Integer.MAX_VALUE)); 
                if(score > max_score) {
                    max_score = score;
                    idx = i;
                }

                doUndo(undo);
            }
            curr_move = moves.get(idx);
        }

        return curr_move;
    }

    // Promote a pawn.
    private void doPromotion(int x, int y) {
        if(Character.toUpperCase(board[x][y]) == 'P') {
            if("W".equals(onMove) && x == 0) {
                board[x][y] = 'Q';
                wPieces.add('Q');
                wPieces.remove(Character.valueOf('P'));
            }
            else if("B".equals(onMove) && x == 5) {
                board[x][y] = 'q';
                bPieces.add('q');
                bPieces.remove(Character.valueOf('p'));
            }
        }
    }

    // Evaluate the score.
    int computeScore() {
        int wScore = 0;
        int bScore = 0;

        for(int i = 0; i < NROWS; i++) {
            for(int j = 0; j < NCOLS; j++) {
                if(board[i][j] == '.')
                    continue;
                if(Character.isUpperCase(board[i][j])) {
                    wScore += centerControl(i, j);
                    switch(board[i][j]) {
                        case 'K':
                            wScore += 10000;
                            wScore += kingFormation(i, j, "W");
                            break;
                        case 'Q':
                            wScore += 900;
                            break;
                        case 'B':
                            wScore += 300;
                            break;
                        case 'N':
                            wScore += 400;
                            break;
                        case 'R':
                            wScore += 500;
                            break;
                        case 'P':
                            wScore += 100;
                            wScore += pawnFormation(i, j, 'P');
                            break;
                        default:
                            System.out.println("Unrecognized white piece: " + String.valueOf(board[i][j]));
                            System.exit(1);
                    }
                }
                else {
                    bScore += centerControl(i, j);
                    switch (board[i][j]) {
                        case 'k':
                            bScore += 10000;
                            bScore += kingFormation(i, j, "B");
                            break;
                        case 'q':
                            bScore += 900;
                            break;
                        case 'b':
                            bScore += 300;
                            break;
                        case 'n':
                            bScore += 400;
                            break;
                        case 'r':
                            bScore += 500;
                            break;
                        case 'p':
                            bScore += 100;
                            bScore += pawnFormation(i, j, 'p');
                            break;
                        default:
                            System.out.println("Unrecognized black piece: " + String.valueOf(board[i][j]));
                            System.exit(1);
                    }
                }
            }
        }

        if("W".equals(onMove)) return wScore - bScore;
        else return bScore - wScore;
    }

    // Increase score the closer to the center a piece is.
    private int centerControl(int x, int y) {
        int score = 0;
        if(x == 2 || x == 3)
            score += 20;
        switch(y) {
            case 1:
            case 3:
                score += 50;
                break;
            case 2:
                score += 20;
        }
        return score;
    }

    // Increase score as pawns advance. Increase score slightly for side-by-side pawns,
    // and slightly more for pawns adjacent diagonally.
    private int pawnFormation(int x, int y, char color) {
        int score = 0;
        if(color == 'P')
            score += (6 - x) * 50;
        else
            score += x*50;
        for(int i = -1; i < 2; i+=2) {
            for(int j = -1; j < 2; j+=2) {
                try {
                    if (board[x][y + j] == color)
                        score += 25;
                    if (board[x + i][y + j] == color)
                        score += 50;
                }
                catch (IndexOutOfBoundsException e) {} // Harmless, just don't do anything
            }
        }
        return score;
    }

    // Increase score the more friendly pieces surround the king.
    private int kingFormation(int x0, int y0, String color) {
        int score = 0;
        for(int i = -1; i < 2; i++) {
            for(int j = -1; j < 2; j++) {
                int x = x0 + i;
                int y = y0 + j;
                try {
                    if(board[x][y] == '.')
                        continue;
                    if ("W".equals(color) && Character.isUpperCase(board[x][y]))
                        score += 15;
                    else if("B".equals(color) && Character.isLowerCase(board[x][y]))
                        score += 15;
                }
                catch (IndexOutOfBoundsException e) {} // Harmless, just don't do anything
            }
        }
        return score;
    }
}


