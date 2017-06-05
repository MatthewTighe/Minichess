package com.small314;


import java.util.Scanner;

/**
 * A player that gets input from a user to make moves.
 */
public class HumanPlayer extends Player {

    public HumanPlayer(String color) { super(color); }

    public Move makeMove() {
        Scanner scanner = new Scanner(System.in);
        System.out.print("Enter your move human: ");
        Move move = new Move(scanner.nextLine());
        posn.makeMove(move);
        return move;
    }
}
