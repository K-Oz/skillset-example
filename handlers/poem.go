package handlers

import (
	"fmt"
	"net/http"
)

// Poem returns a poem about blitterblatter
func Poem(w http.ResponseWriter, r *http.Request) {
	fmt.Println("Poem Called")
	
	poem := `Blitterblatter, whimsical word,
Dancing on the tongue, quite absurd.
A sound that splashes, a rhythmic patter,
In a world of nonsense, what does it matter?

Blitterblatter through puddles of rain,
Echoing laughter, soothing the pain.
A made-up term with magical power,
Blooming like an imaginary flower.

Blitterblatter in dreams and in play,
A fantastical concept that's here to stay.
Neither thing nor thought but somewhere between,
The most curious word you've ever seen.`

	w.Header().Set("Content-Type", "text/plain")
	w.Write([]byte(poem))
}