package com.small314;

import java.io.IOException;

public class Main {

    // Offline variables
    private static String p1_type = null;
    private static int p1_depth = -1;
    private static double p1_limit = -1.0;

    private static String p2_type = null;
    private static int p2_depth = -1;
    private static double p2_limit = -1.0;

    // Online variables
    private static String user = "small314";
    private static String passwd = null;
    private static String gameNumber = null;
    private static String offerColor = null;

    public static void main(String[] args) {
        parseArgs(args);
        if (passwd != null) {
            play_online();
        } else {
            play_local();
        }
    }

    // Connect to IMCS and play. Game type depends on command line arguments.
    private static void play_online() {
        assert(user != null && passwd != null && (gameNumber != null || offerColor != null));
        try {
            String color;
            Client c = new Client("imcs.svcs.cs.pdx.edu", "3589", user, passwd);
            if(gameNumber != null)
                color = String.valueOf(c.accept(gameNumber, '?'));
            else
                color = String.valueOf(c.offer(offerColor.charAt(0)));

            Player player = new IDPlayer(color, 0);
            if("B".equals(color)) {
                String move = c.getMove();
                System.out.print(player.posn.getPosnString());
                System.out.println(move);
                player.getMove(move);
            }

            while(true) {
                // Print board, make a move, and print the move.
                System.out.print(player.posn.getPosnString());
                Move move = player.makeMove();
                System.out.println(move.toStr());
                c.sendMove(move.toStr());
                if(move.win) {
                    System.out.print(player.posn.getPosnString());
                    System.out.println("I won!");
                    c.close();
                    break;
                }

                // Get a move, print it and the board, update player.
                String mv = c.getMove();
                System.out.print(player.posn.getPosnString());
                System.out.println(mv);
                player.getMove(mv);
                if(player.posn.checkEnd()) {
                    System.out.print(player.posn.getPosnString());
                    System.out.println("I lost!");
                    c.close();
                    break;
                }
            }

        } catch (IOException e) {
            System.out.println("Client failure: " + e);
            System.exit(1);
        }


    }

    // Play a game locally. Player types depend on command line arguments.
    private static void play_local() {
        assert(p1_type != null);
        assert(p2_type != null);
        Player p1 = null;
        Player p2 = null;
        System.out.println(p1_type);
        System.out.println(p2_type);
        switch(p1_type) {
            case "human":
                p1 = new HumanPlayer("W");
                break;
            case "random":
                p1 = new RandomPlayer("W");
                break;
            case "heuristic":
                p1 = new HeuristicPlayer("W");
                break;
            case "negamax":
                p1 = new NegamaxPlayer("W", p1_depth);
                break;
            case "ab":
                p1 = new AlphaBetaPlayer("W", p1_depth);
                break;
            case "id":
                p1 = new IDPlayer("W", p1_limit);
                break;
            default:
                printHelp();
        }

        switch(p2_type) {
            case "human":
                p2 = new HumanPlayer("B");
                break;
            case "random":
                p2 = new RandomPlayer("B");
                break;
            case "heuristic":
                p2 = new HeuristicPlayer("B");
                break;
            case "negamax":
                p2 = new NegamaxPlayer("B", p2_depth);
                break;
            case "ab":
                p2 = new AlphaBetaPlayer("B", p2_depth);
                break;
            case "id":
                p2 = new IDPlayer("B", p2_limit);
                break;
            default:
                printHelp();
        }

        assert(p1 != null && p2 != null);
        while(p1.posn.ply / 2 < 40) {
            System.out.println("p1");
            System.out.print(p1.posn.getPosnString());
            Move p1Move = p1.makeMove();
            System.out.println(p1Move.toStr());
            if(p1Move.win) {
                System.out.print(p1.posn.getPosnString());
                System.out.println("W wins!");
                System.exit(0);
            }

            p2.getMove(p1Move.toStr());
            System.out.println("p2");
            System.out.print(p2.posn.getPosnString());
            Move p2Move = p2.makeMove();
            System.out.println(p2Move.toStr());
            if(p2Move.win) {
                System.out.print(p2.posn.getPosnString());
                System.out.println("B wins!");
                System.exit(0);
            }
            p1.getMove(p2Move.toStr());
        }
    }

    // Parse command line arguments.
    private static void parseArgs(String[] args) {
        for(int i = 0; i < args.length; i++) {
            if("-h".equals(args[i]) || "--help".equals(args[i]))
                printHelp();

            if("-1".equals(args[i]) || "--player1".equals(args[i])) {
                if(args[i+1].contains(":")) {
                    String[] parts = args[i+1].split(":");
                    p1_type = parts[0];
                    if("id".equals(p1_type))
                        p1_limit = Double.parseDouble(parts[1]);
                    else
                        p1_depth = Integer.parseInt(parts[1]);
                }
                else
                    p1_type = args[i+1];
                i++;
            }

            if("-2".equals(args[i]) || "--player2".equals(args[i])) {
                if(args[i+1].contains(":")) {
                    String[] parts = args[i+1].split(":");
                    p2_type = parts[0];
                    if("id".equals(p2_type))
                        p2_limit = Double.parseDouble(parts[1]);
                    else
                        p2_depth = Integer.parseInt(parts[1]);
                }
                else
                    p2_type = args[i+1];
                i++;
            }

            if("-u".equals(args[i]) || "--user".equals(args[i])) {
                user = args[i+1];
                i++;
            }

            if("-p".equals(args[i]) || "--passwd".equals(args[i])) {
                passwd = args[i+1];
                i++;
            }

            if("-o".equals(args[i]) || "--offer".equals(args[i])) {
                String color = args[i+1];
                if("?".equals(color) || "B".equals(color) || "W".equals(color))
                    offerColor = color;
                else
                    offerColor = "?";
                i++;
            }

            if("-a".equals(args[i]) || "--accept".equals(args[i])) {
                gameNumber = (args[i+1]);
                i++;
            }
        }

        if(gameNumber != null && offerColor != null)
            printHelp();
        if(passwd == null && (gameNumber != null || offerColor != null))
            printHelp();
        if((p1_type == null && p2_type != null) || (p1_type != null && p2_type == null))
            printHelp();
    }

    // Print help message, then exit.
    private static void printHelp() {
        System.out.println("Usage: java Main.class");
        System.out.println("Offline example: java Main.java -1 human -2 ab:6");
        System.out.println("Online example: java Main.java -u johnHanChess -p chess -o ?");
        System.out.println("Options:");
        System.out.println("-h --help: This help message.");
        System.out.println("-1 --player1: Player 1 type. (human, random, heuristic, negamax:<depth>, ab:<depth>, id:<limit>");
        System.out.println("-2 --player2: Player 2 type. Same as above. If one is present both must be.");
        System.out.println("<depth> is an integer. <limit> is a time limit, can be a double.");
        System.out.println("-u --user: username for PSU IMCS server. Requires -p and one of -o or -a.");
        System.out.println("-p --passwd: password for PSU IMCS server.");
        System.out.println("-o --offer: Offer game. Optionally followed by ?, B, or W to offer specific color.");
        System.out.println("-a --accept: Accept game. Must be followed by game number.");
        System.exit(1);
    }
}
