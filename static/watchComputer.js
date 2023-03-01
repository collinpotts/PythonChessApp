// Watch computer play button
document.getElementById('watchComputerBtn').addEventListener('click', function() {
    var board = null
    var game = new Chess()
    
    function makeRandomMove () {
        var possibleMoves = game.moves()

        if (game.game_over()) return
    
      var randomIdx = Math.floor(Math.random() * possibleMoves.length)
        game.move(possibleMoves[randomIdx])
        board.position(game.fen())
    
        window.setTimeout(makeRandomMove, 500)
    }
    
    var config = {
    
        position: 'start',
        pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png'
    }
    board = Chessboard('myBoard', config)
    
    window.setTimeout(makeRandomMove, 500)
});