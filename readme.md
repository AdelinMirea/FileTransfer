A utility tool to transfer files between two computers in the same network.

## How to use:
Both machines should be connected to the same network.

1. Replace the IPs from classes with yours (both of them should be server's IP)
1. Start the program on one machine and write "send". This will be your server.
2. Start the program on another machine and write something different from "send" (you can just press enter)
3. Use the commands from below

## Commands

    ls - show files from current folder
    ls d:\Downloads - show files from d:\Downloads 

    get d:\Downloads\Book.pdf - download the book file on client machine

If there is no such file then a dummy file will be created with the name "No such file".

Warning! If you connect more than one client to the server, using the "ls" command will affect everybody's state.

## Work in progress

Download an entire folder
    
    get D:\Downloads - get the entire "Downloads" folder

Every client will have its own session (using ls will not affect other sessions).