let currentQuestionId = null;
let currentAnswer = "";
let currentDifficulty = 1;


// ----------------------
// START QUIZ
// ----------------------
async function startQuiz() {
    const res = await fetch("/start");
    const data = await res.json();

    renderQuestion(data);
}


// ----------------------
// RENDER QUESTION
// ----------------------
function renderQuestion(data) {

    currentQuestionId = data.question_id;
    currentAnswer = data.correct_answer;
    currentDifficulty = data.difficulty;

    document.getElementById("question").innerText = data.question;
    document.getElementById("difficulty").innerText =
        "Difficulty Level: " + data.difficulty;

    const box = document.getElementById("options");
    box.innerHTML = "";

    data.options.forEach(opt => {
        const btn = document.createElement("button");
        btn.innerText = opt;

        btn.onclick = () => submitAnswer(opt);

        box.appendChild(btn);
    });

    document.getElementById("result").innerText = "";
    document.getElementById("result").className = "";
}


// ----------------------
// SUBMIT ANSWER
// ----------------------
async function submitAnswer(answer) {

    const res = await fetch("/answer", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            question_id: currentQuestionId,
            answer: answer
        })
    });

    const data = await res.json();

    const resultBox = document.getElementById("result");

    if (data.correct) {
        resultBox.innerText = "✔ Mission Success";
        resultBox.className = "correct";
    } else {
        resultBox.innerText = "✖ Mission Failed";
        resultBox.className = "wrong";
    }

    // small delay for UX feel
    setTimeout(() => {
        renderQuestion(data.next_question);
    }, 600);
}


// ----------------------
// INIT
// ----------------------
startQuiz();