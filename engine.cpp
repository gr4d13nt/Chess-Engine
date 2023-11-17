#include <iostream>
#include <string>

using namespace std;

int main() {
    string fen_string;
    getline(cin, fen_string);  // Read FEN string from standard input

    // Process the FEN string...
    // Example: Print it back to the console
    cout << "Received FEN: " << fen_string << endl;

    return 0;
}
 