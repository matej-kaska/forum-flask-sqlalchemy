function edit(input) {
    var elements = ["input", "text"]
    for (i = 0; i < 2; i++){
        const target = document.getElementById(input + elements[i]);
        if (target.style.display == "none") {
            target.style.display = "inline";
            } else {
            target.style.display = "none";
            }
    }
  };