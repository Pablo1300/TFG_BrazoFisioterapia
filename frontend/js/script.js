const articulations = document.getElementById("articulation")
const movements = document.getElementById("movement")
const endfeels = document.getElementById("endfeel")
const range = document.getElementById("executionPoint")
const simulateButton = document.getElementById("simulateButton")

function activateExecutionPoint() {
    if (movements.value === "disabled") {
        range.disabled = true;
        range.nextElementSibling.value = "Selecciona articulación y movimiento para calcular rango de movimiento"
    } else {
        range.disabled = false;
        let executionPointList = {
            hombro: [[-60, 180, "flexext"], [0, 180, "abdadu"], [-90, 90, "intext"]],
            codo: [[-7, 140, "flexext"]],
        }
        if (articulations.value === "hombro") {
            executionPointList.hombro.forEach(function (executionPoint) {
                if (movements.value === executionPoint[2]) {
                    range.min = executionPoint[0]
                    range.max = executionPoint[1]
                }
            })
        } else {
            range.min = executionPointList.codo[0][0]
            range.max = executionPointList.codo[0][1]
        }
        range.value = 0
        range.nextElementSibling.value = range.value
    }
}

function loadMovements() {
    // Objeto de provincias con pueblos
    let movementList = {
        hombro: [["Flexión/Extensión", "flexext"], ["Abducción/Aducción", "abdadu"], ["Rotación Interna/Externa", "intext"]],
        codo: [["Flexión/Extensión", "flexext"]],
    }

    let articulationSelected = articulations.value

    // Se limpian los pueblos
    movements.innerHTML = '<option value="disabled" disabled selected>Selecciona tipo de movimiento...</option>'

    if (articulationSelected !== '') {
        // Se seleccionan los pueblos y se ordenan
        articulationSelected = movementList[articulationSelected]

        // Insertamos los pueblos
        articulationSelected.forEach(function (movement) {
            let option = document.createElement('option')
            option.value = movement[1]
            option.text = movement[0]
            movements.add(option)
        });
    }
}

simulateButton.addEventListener("click", function (event) {
    let movementSelected = movements.value
    let endFeelSelected = endfeels.value
    let executionPoint = range.value

    let errorMovement = document.getElementById("error-movement")
    let errorEndFeel = document.getElementById("error-endfeel")
    let errorRange = document.getElementById("error-range")

    if (movementSelected === "disabled") {
        errorMovement.style.display = "block";
        event.preventDefault()
    } else {
        errorMovement.style.display = "none";
    }

    if (endFeelSelected === "disabled") {
        errorEndFeel.style.display = "block";
        event.preventDefault()
    } else {
        errorEndFeel.style.display = "none";
    }

    if (executionPoint == 0) {
        errorRange.style.display = "block";
        event.preventDefault()
    } else {
        errorRange.style.display = "none";
    }
})